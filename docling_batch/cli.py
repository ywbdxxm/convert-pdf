import argparse
from pathlib import Path

from docling_batch.models import RuntimeConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="docling-batch")
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert = subparsers.add_parser("convert")
    convert.add_argument("--input", action="append", required=True)
    convert.add_argument("--output", required=True)
    convert.add_argument(
        "--page-window-size",
        type=int,
        default=250,
    )
    convert.add_argument(
        "--page-window-min-pages",
        type=int,
        default=500,
    )
    convert.add_argument(
        "--device",
        default="cuda",
        choices=["auto", "cpu", "cuda", "mps", "xpu"],
    )
    convert.add_argument(
        "--ocr-engine",
        default="rapidocr",
        choices=["rapidocr", "tesseract"],
    )
    convert.add_argument(
        "--tokenizer",
        default="sentence-transformers/all-MiniLM-L6-v2",
    )
    convert.add_argument(
        "--max-chunk-tokens",
        type=int,
        default=384,
    )
    convert.add_argument(
        "--image-mode",
        default="referenced",
        choices=["placeholder", "referenced", "embedded"],
    )
    convert.add_argument(
        "--generate-page-images",
        action="store_true",
    )
    convert.add_argument(
        "--image-scale",
        type=float,
        default=2.0,
    )
    convert.add_argument(
        "--image-filter",
        default="heuristic",
        choices=["off", "heuristic"],
    )
    convert.add_argument(
        "--no-ocr",
        action="store_true",
    )
    convert.add_argument(
        "--force-full-page-ocr",
        action="store_true",
    )

    return parser


def build_runtime_config(args: argparse.Namespace) -> RuntimeConfig:
    return RuntimeConfig(
        input_paths=[Path(item) for item in args.input],
        output_root=Path(args.output),
        page_window_size=args.page_window_size if args.page_window_size and args.page_window_size > 0 else None,
        page_window_min_pages=max(0, args.page_window_min_pages),
        device=args.device,
        enable_ocr=not args.no_ocr,
        ocr_engine=args.ocr_engine,
        force_full_page_ocr=args.force_full_page_ocr,
        tokenizer=args.tokenizer,
        max_chunk_tokens=args.max_chunk_tokens,
        image_mode=args.image_mode,
        generate_picture_images=args.image_mode != "placeholder",
        generate_page_images=args.generate_page_images,
        image_scale=args.image_scale,
        image_filter=args.image_filter,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command != "convert":
        parser.error(f"unsupported command: {args.command}")

    config = build_runtime_config(args)
    from docling_batch.converter import run_batch

    summary = run_batch(config)
    print(
        f"processed={summary['total_documents']} "
        f"success={summary['success_count']} "
        f"partial={summary['partial_success_count']} "
        f"failure={summary['failure_count']}"
    )
    return 0 if summary["failure_count"] == 0 else 1
