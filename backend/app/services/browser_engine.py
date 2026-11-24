from urllib.parse import urlparse
import ipaddress
import socket
from playwright.sync_api import sync_playwright

BLOCKED_ACTIONS = {"submit", "payment", "otp", "captcha"}

class BrowserEngine:
    def validate_url(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            return False
        host = parsed.hostname.lower()
        if host in {"localhost", "127.0.0.1", "::1"}:
            return True
        try:
            address = ipaddress.ip_address(host)
            return not (address.is_private or address.is_loopback or address.is_link_local or address.is_reserved)
        except ValueError:
            try:
                for info in socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80)):
                    resolved = ipaddress.ip_address(info[4][0].split("%")[0])
                    if resolved.is_private or resolved.is_loopback or resolved.is_link_local or resolved.is_reserved:
                        return False
                return True
            except socket.gaierror:
                return False

    def inspect(self, url: str) -> dict:
        if not self.validate_url(url):
            raise ValueError("URL is outside the local browser allowlist")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")
            title = page.title()
            text = page.locator("body").inner_text(timeout=5000)
            headings = page.locator("h1, h2, h3").all_inner_texts()
            fields = []
            for el in page.locator("input, select, textarea").all():
                name = el.get_attribute("name") or el.get_attribute("id") or ""
                label = el.get_attribute("aria-label") or name
                if name:
                    fields.append({"name": name, "label": label, "type": el.get_attribute("type") or "text"})
            links = page.locator("a").evaluate_all("(els) => els.map(e => ({text:e.innerText.trim(), href:e.href}))")
            browser.close()
            return {"url": page.url, "title": title, "text": text[:12000], "headings": headings, "fields": fields, "links": links[:50]}

    def fill_fields(self, url: str, fields: dict[str, str]) -> dict:
        if not self.validate_url(url):
            raise ValueError("URL is outside the local browser allowlist")
        forbidden = [key for key in fields if any(word in key.lower() for word in BLOCKED_ACTIONS)]
        if forbidden:
            raise ValueError("Sensitive fields are blocked")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")
            filled = []
            for name, value in fields.items():
                locator = page.locator(f"[name='{name}'], #{name}")
                if locator.count():
                    field = locator.first
                    if not field.is_visible():
                        continue_button = page.get_by_role("button", name="Continue")
                        if continue_button.count() and continue_button.is_visible():
                            continue_button.click()
                            page.wait_for_timeout(100)
                    if not field.is_visible():
                        continue
                    if (field.get_attribute("tag_name") or "").lower() == "select":
                        field.select_option(label=value)
                    elif field.evaluate("(e) => e.tagName") == "SELECT":
                        field.select_option(label=value)
                    else:
                        field.fill(value)
                    filled.append(name)
            browser.close()
            return {"filled": filled, "url": url}

browser_engine = BrowserEngine()
