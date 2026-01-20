from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import requests


@dataclass(frozen=True)
class UploadLink:
    href: str
    method: str


class YandexDiskClient:
    """
    Мини-клиент Я.Диска (REST).
    База: https://cloud-api.yandex.net/v1/disk/ :contentReference[oaicite:3]{index=3}
    """

    def __init__(self, token: str, timeout: int = 30) -> None:
        self.token = token.strip()
        self.timeout = timeout
        self.base_url = "https://cloud-api.yandex.net/v1/disk"
        self.headers = {"Authorization": f"OAuth {self.token}"}

    def create_folder(self, path: str) -> None:
        """
        PUT /resources?path=...  (создание папки) :contentReference[oaicite:4]{index=4}
        Если папка уже есть — считаем ок.
        """
        url = f"{self.base_url}/resources"
        params = {"path": path}
        resp = requests.put(url, headers=self.headers, params=params, timeout=self.timeout)

        if resp.status_code in (201, 409):  # 409 Conflict: already exists
            return

        resp.raise_for_status()

    def get_upload_link(self, path: str, overwrite: bool = True) -> UploadLink:
        """
        GET /resources/upload?path=... (&overwrite=...) :contentReference[oaicite:5]{index=5}
        """
        url = f"{self.base_url}/resources/upload"
        params = {"path": path, "overwrite": str(overwrite).lower()}
        resp = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
        resp.raise_for_status()

        data = resp.json()
        return UploadLink(href=data["href"], method=data.get("method", "PUT"))

    def upload_stream_to_href(
        self,
        href: str,
        data_iter,
        content_type: Optional[str] = None,
    ) -> None:
        """
        Заливаем байты на уже выданный href (обычно PUT).
        """
        headers = {}
        if content_type:
            headers["Content-Type"] = content_type

        resp = requests.put(href, data=data_iter, headers=headers, timeout=self.timeout)
        if resp.status_code not in (201, 202, 204):
            resp.raise_for_status()
