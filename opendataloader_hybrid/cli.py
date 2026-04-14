from __future__ import annotations

import argparse
from pathlib import Path

from .bundle import build_bundle


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="opendataloader-hybrid-bundle")
    parser.add_argument("--doc-id", required=True)
    parser.add_argument("--source-pdf", required=True)
    parser.add_argument("--native-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    build_bundle(
        doc_id=args.doc_id,
        source_pdf_path=args.source_pdf,
        native_dir=Path(args.native_dir),
        out_dir=Path(args.output_dir),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
