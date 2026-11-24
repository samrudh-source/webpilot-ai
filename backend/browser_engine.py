from pathlib import Path

ALLOWED_FIELD_NAMES = {"full_name", "email", "gpa", "statement"}


class PlaywrightBrowserEngine:
    """Playwright boundary for sandbox-only semantic field discovery."""

    def __init__(self, user_data_dir: str = ".webpilot-browser"):
        self.user_data_dir = str(Path(user_data_dir).resolve())

    def inspect_sandbox(self, url: str) -> list[dict]:
        if not url.startswith("http://localhost:8000/sandbox/"):
            raise ValueError("Browser access is restricted to the local sandbox")
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise RuntimeError("Install Playwright with pip and 'playwright install chromium'") from exc

        fields = []
        with sync_playwright() as playwright:
            context = playwright.chromium.launch_persistent_context(
                self.user_data_dir, headless=True
            )
            page = context.new_page()
            page.goto(url)
            for name in ALLOWED_FIELD_NAMES:
                locator = page.locator(f'[name="{name}"]')
                if locator.count():
                    fields.append({
                        "name": name,
                        "label": locator.get_attribute("aria-label") or name,
                    })
            context.close()
        return fields
