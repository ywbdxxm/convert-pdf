# Progress

## Current Status

2026-04-13:

- Direction reset to external-first tooling.
- `docling_batch` is frozen as a historical baseline.
- `manual_eval` custom framework was stopped and removed before commit.
- Heavy RAGFlow and paid/remote parser routes are deferred or excluded.
- New local/free plan is documented in `docs/architecture/2026-04-13-external-first-manual-tooling-plan.md`.
- `findings.md` and `README.md` were compressed to current decisions and next steps.

## Recent Decisions

- First parser to test: `OpenDataLoader PDF` local mode.
- First app/UI candidate: `AnythingLLM`.
- Dify remains a serious candidate, but only after parser output is chosen.
- Docling should be tested through mature integrations such as LlamaIndex and LangChain, not through more custom wrapper code.

## Next Action

Run a small, local OpenDataLoader PDF smoke test on:

```text
manuals/raw/espressif/esp32s3/esp32-s3_datasheet_en.pdf
```

Check:

- `Table 2-9. Peripheral Pin Assignment`
- JSON page numbers
- bounding boxes
- Markdown readability
- HTML/table rendering
- ability to map evidence back to the original PDF page

## Verification

- Planning files are intentionally concise after cleanup.
- Runtime code was not changed.
- `docling_batch` remains untouched.
