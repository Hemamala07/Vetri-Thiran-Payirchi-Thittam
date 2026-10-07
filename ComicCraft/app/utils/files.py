import re
from pathlib import Path


def safe_filename(
    value: str,
    fallback: str = "comic",
) -> str:

    cleaned = re.sub(
        r"[^a-zA-Z0-9._-]+",
        "_",
        value.strip(),
    )

    cleaned = cleaned.strip("._")

    return cleaned[:80] or fallback


def static_url_from_path(
    path: Path,
    static_dir: Path,
) -> str:

    relative = path.resolve().relative_to(
        static_dir.resolve()
    )

    return (
        "/static/"
        + relative.as_posix()
    )