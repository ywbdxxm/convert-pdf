# Progress

## Current Status

2026-04-13:

- Mainline comparison reduced to `docling_batch`, `Docling` native output, and `OpenDataLoader PDF`.
- `OpenDataLoader` hybrid mode is included because it may improve hard table pages while staying local.
- `OpenDataLoader + LangChain` and `Docling + LlamaIndex/LangChain` are kept only as metadata spot-checks.
- All other parser/UI/RAG tools are deferred.
- Added a dedicated architecture note for `docling_batch` future optimization boundaries.

## Next Action

1. Use existing `docling_batch` output as baseline.
2. Generate `Docling` native output for the ESP32-S3 datasheet.
3. Run `OpenDataLoader PDF` local mode on the same file.
4. If local mode table quality is weak, run `OpenDataLoader PDF` hybrid mode with local `docling-fast`.
5. Inspect metadata using the official LangChain/OpenDataLoader path and the official Docling consumer paths.

## Verification Focus

- `Table 2-9. Peripheral Pin Assignment`
- page numbers
- bounding boxes
- Markdown / JSON / HTML usefulness
- ability to return to the original PDF
- whether Codex direct folder inspection is already sufficient
