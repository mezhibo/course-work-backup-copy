import re


_ILLEGAL = r'[<>:"/\\|?*\n\r\t]'


def safe_filename(name: str, max_len: int = 120) -> str:
    """
    Делает строку безопасной для имени файла/пути на Я.Диске.
    """
    name = name.strip()
    name = re.sub(_ILLEGAL, "_", name)
    name = re.sub(r"\s+", " ", name).strip()
    if not name:
        name = "untitled"
    return name[:max_len]
