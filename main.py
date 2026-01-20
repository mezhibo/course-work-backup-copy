from __future__ import annotations

import json
import mimetypes
from datetime import datetime
from typing import Dict, List, Optional

from tqdm import tqdm

from cataas import get_cat_with_text
from utils import safe_filename
from yandex_disk import YandexDiskClient


GROUP_FOLDER = "fpy-140"


def guess_extension(content_type: str) -> str:
    ext = mimetypes.guess_extension(content_type.split(";")[0].strip())
    return ext or ".jpg"


def read_positive_int(prompt: str, default: int = 1) -> int:
    raw = input(prompt).strip()
    if not raw:
        return default
    try:
        val = int(raw)
        return val if val > 0 else default
    except ValueError:
        return default


def main() -> None:
    print("=== Курсовая: резервное копирование котов на Яндекс.Диск ===")
    print(f"Папка на Я.Диске: {GROUP_FOLDER}\n")

    text = input("Введите текст для картинки: ").strip()
    token = input("Введите OAuth-токен Я.Диска (из Полигона): ").strip()
    count = read_positive_int("Сколько картинок загрузить? (например 5): ", default=5)

    if not text:
        print("Ошибка: текст обязателен.")
        return
    if not token:
        print("Ошибка: токен обязателен.")
        return

    yd = YandexDiskClient(token=token)

    folder_path = f"disk:/{GROUP_FOLDER}"
    yd.create_folder(folder_path)

    safe_text = safe_filename(text)
    results: List[Dict] = []

    for i in range(1, count + 1):
        # 1) Берём кота с текстом потоком
        cat_stream = get_cat_with_text(text)
        ext = guess_extension(cat_stream.content_type)

        filename = f"{safe_text}_{i:02d}{ext}"
        disk_file_path = f"{folder_path}/{filename}"

        # 2) Получаем href для загрузки
        link = yd.get_upload_link(disk_file_path, overwrite=True)

        # 3) Загружаем по воздуху (stream -> PUT href)
        resp = cat_stream.response

        total: Optional[int] = None
        if resp.headers.get("Content-Length"):
            try:
                total = int(resp.headers["Content-Length"])
            except ValueError:
                total = None

        uploaded_size = 0

        def gen():
            nonlocal uploaded_size
            for chunk in resp.iter_content(chunk_size=1024 * 64):
                if chunk:
                    uploaded_size += len(chunk)
                    pbar.update(len(chunk))
                    yield chunk

        desc = f"[{i}/{count}] Uploading {filename}"
        with tqdm(total=total, unit="B", unit_scale=True, desc=desc) as pbar:
            yd.upload_stream_to_href(
                href=link.href,
                data_iter=gen(),
                content_type=cat_stream.content_type,
            )

        resp.close()

        results.append(
            {
                "file_name": filename,
                "disk_path": disk_file_path,
                "size_bytes": uploaded_size,
                "uploaded_at": datetime.now().isoformat(timespec="seconds"),
            }
        )

    with open("result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\nГотово!")
    print(f"Папка на Я.Диске: {folder_path}")
    print("Отчёт: result.json")


if __name__ == "__main__":
    main()
