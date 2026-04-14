# OpenDataLoader Output Handling

Date: 2026-04-13

## Question

When using `OpenDataLoader PDF`, should its final outputs be forced to match the current `manuals/processed/<doc_id>` structure produced by `docling_bundle`?

## Short Answer

No.

Do not force OpenDataLoader's raw outputs to fully match the current `manuals/processed/<doc_id>` structure on day one.

The current `manuals/processed/<doc_id>` layout is useful as an example of agent-friendly packaging, but it is not yet proven to be the universal best schema for every parser.

The better default is:

```text
raw native output + thin agent-friendly overlay
```

## Why Not Force Full Alignment

The current `manuals/processed/<doc_id>` tree was built around `docling_bundle`.

It mixes together:

- Docling native outputs
- our custom manifest format
- our custom chunk and section schemas
- our custom alert semantics
- our custom table sidecar conventions
- our custom Markdown link injection
- our custom cache layout

This is fine for the current baseline, but if we force `OpenDataLoader PDF` into the same shape too early, we risk:

- losing native OpenDataLoader metadata
- hiding where parser behavior differs from our wrapper behavior
- spending time on format conversion instead of quality evaluation
- accidentally biasing the comparison toward the existing `docling_bundle` worldview

## What Is Good In The Current Layout

The current `manuals/processed/<doc_id>` design still contains good ideas worth preserving:

- one obvious directory per source document
- both human-readable and machine-readable outputs
- easy entrypoints for an agent
- explicit provenance
- explicit table/image sidecars
- explicit quality/risk signaling

These are design goals, not a fixed schema contract.

## Recommended OpenDataLoader Layout

For `OpenDataLoader PDF`, use a two-layer structure:

```text
<doc_root>/
  raw/
    ...native OpenDataLoader outputs...
  overlay/
    ...thin agent-friendly derived files...
```

### `raw/`

Keep the parser's outputs intact:

- original Markdown
- original JSON
- original HTML
- any native assets or sidecars

This preserves:

- native metadata
- native page and bbox information
- direct comparability with upstream docs/examples

### `overlay/`

Only add a minimal layer when it helps the agent:

- `README.generated.md` or `index.json`
- optional `pages/` page-level slices
- optional `quality-summary.md`
- optional convenience links to raw files

The overlay should not invent a giant schema. It should mainly help the agent discover and navigate the raw outputs.

## Best-Practice Decision Rule

For OpenDataLoader output handling, ask:

1. Does this preserve the parser's native metadata?
2. Does this make Codex read the folder more easily?
3. Does this avoid encoding parser-specific assumptions into a universal schema too early?

If the answer to all three is yes, keep it.

If not, defer it.

## Comparison With `docling_bundle`

`docling_bundle` can stay as:

- a historical baseline
- an example of file packaging
- a source of useful ideas like page slices, index files, quality summaries, and optional hard-page images

But OpenDataLoader should not be forced to become a byte-for-byte imitation of it.

Instead:

- compare OpenDataLoader raw outputs against the current `docling_bundle` bundle
- if OpenDataLoader wins, add only the thinnest overlay needed for agentic file retrieval
- if the same overlay ideas later make sense for both parsers, they can be generalized later

## Practical Conclusion

The likely best practice is:

```text
OpenDataLoader raw output first
-> inspect with Codex
-> add minimal overlay only where the agent needs help
```

not:

```text
OpenDataLoader raw output
-> reshape everything into docling_bundle schema
-> only then evaluate
```
