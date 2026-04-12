from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimeConfig:
    input_paths: list[Path]
    output_root: Path
    device: str
    enable_ocr: bool
    ocr_engine: str
    force_full_page_ocr: bool
    tokenizer: str
    max_chunk_tokens: int | None
    image_mode: str
    generate_picture_images: bool
    generate_page_images: bool
    image_scale: float
