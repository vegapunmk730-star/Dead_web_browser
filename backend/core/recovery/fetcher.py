import requests
from config.settings import settings
from infrastructure.logging.logger import get_logger

log = get_logger("fetcher")
HEADERS = {"User-Agent": "DeadWebNavigator/3.0"}


def fetch_html(url: str) -> str | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=settings.fetch_timeout)
        r.encoding = r.apparent_encoding or "utf-8"
        log.info("Fetched", url=url, status=r.status_code, size=len(r.text))
        return r.text
    except Exception as e:
        log.error("Fetch failed", url=url, error=str(e))
        return None
