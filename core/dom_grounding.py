import asyncio
from typing import Dict, Any, List, Optional
from playwright.async_api import Page, ElementHandle

class DomGroundingEngine:
    """
    Extracts an accessible, simplified representation of the active web page
    and maps interactive elements to clean numeric index locators.
    """
    def __init__(self):
        self.element_map: Dict[int, Dict[str, Any]] = {}

    async def scan_interactive_tree(self, page: Page) -> Dict[str, Any]:
        """
        Scans the DOM for inputs, buttons, links, selects, textareas, and text content.
        Returns a human-and-LLM friendly AXTree string and stores locators.
        """
        self.element_map.clear()
        
        # JavaScript helper to discover all visible interactable nodes
        js_script = """
        () => {
            const elements = Array.from(document.querySelectorAll('input, button, select, textarea, a, form, [role="button"]'));
            return elements.map((el, idx) => {
                const rect = el.getBoundingClientRect();
                const isVisible = rect.width > 0 && rect.height > 0 && window.getComputedStyle(el).visibility !== 'hidden';
                if (!isVisible) return null;
                
                let label = '';
                if (el.labels && el.labels.length > 0) {
                    label = el.labels[0].innerText;
                } else if (el.placeholder) {
                    label = el.placeholder;
                } else if (el.innerText) {
                    label = el.innerText.trim();
                } else if (el.getAttribute('aria-label')) {
                    label = el.getAttribute('aria-label');
                } else if (el.name) {
                    label = el.name;
                }

                return {
                    index: idx + 1,
                    tag: el.tagName.toLowerCase(),
                    type: el.getAttribute('type') || '',
                    id: el.id || '',
                    name: el.name || '',
                    label: label.substring(0, 100),
                    value: el.value || '',
                    href: el.href || ''
                };
            }).filter(Boolean);
        }
        """
        raw_items = await page.evaluate(js_script)
        
        tree_lines = [f"=== Page Title: {await page.title()} (URL: {page.url}) ==="]
        for i, item in enumerate(raw_items):
            idx = i + 1
            item["runtime_index"] = idx
            self.element_map[idx] = item
            
            tag = item["tag"]
            label_str = f"'{item['label']}'" if item["label"] else f"name={item['name'] or item['id']}"
            val_str = f" [current_value: '{item['value']}']" if item["value"] else ""
            tree_lines.append(f"  [{idx}] <{tag} type='{item['type']}'> {label_str}{val_str}")

        # Check for presence of alerts or error banners
        error_text = await page.evaluate("""
            () => {
                const banner = document.querySelector('.alert-error, #error-banner, .error');
                return banner ? banner.innerText : null;
            }
        """)
        if error_text:
            tree_lines.append(f"\n⚠️ [PAGE ALERT / ERROR DETECTED]: {error_text}")

        # Check for success banner
        success_text = await page.evaluate("""
            () => {
                const banner = document.querySelector('.alert-success, #confirmation-banner, .success');
                return banner ? banner.innerText : null;
            }
        """)
        if success_text:
            tree_lines.append(f"\n✓ [PAGE SUCCESS DETECTED]: {success_text}")

        return {
            "axtree_text": "\n".join(tree_lines),
            "elements": self.element_map,
            "has_error": bool(error_text),
            "error_message": error_text,
            "has_success": bool(success_text),
            "success_message": success_text
        }

    async def interact_by_index(self, page: Page, index: int, action: str, value: Optional[str] = None):
        """
        Interacts with an element using its index in the scanned element map.
        """
        if index not in self.element_map:
            raise ValueError(f"Element index [{index}] not found in active AXTree map.")
        
        elem_info = self.element_map[index]
        selector = f"#{elem_info['id']}" if elem_info["id"] else f"[name='{elem_info['name']}']" if elem_info["name"] else elem_info["tag"]

        if action == "click":
            await page.click(selector)
        elif action == "fill":
            await page.fill(selector, value or "")
        elif action == "select":
            await page.select_option(selector, value or "")
        else:
            raise ValueError(f"Unsupported action: {action}")
