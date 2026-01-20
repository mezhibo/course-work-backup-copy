from __future__ import annotations

from dataclasses import dataclass

import requests


@dataclass(frozen=True)
class CatImageStream:
    """
    Поток для скачивания картинки кота.
    content_type нужен, чтобы сохранить расширение/заголовки.
    """
    response: requests.Response
    content_type: str


def get_cat_with_text(text: str, timeout: int = 30) -> CatImageStream:
    """
    Берём кота с текстом: /cat/says/:text  (CATAAS) :contentReference[oaicite:2]{index=2}
    """
    url = f"https://cataas.com/cat/says/{requests.utils.quote(text)}"
    resp = requests.get(url, stream=True, timeout=timeout)
    resp.raise_for_status()
    ctype = resp.headers.get("Content-Type", "application/octet-stream")
    return CatImageStream(response=resp, content_type=ctype)
