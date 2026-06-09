---
name: large-file-generator
description: Use when generating large files (HTML, CSV, Markdown, JSON, or any text format) that risk session hangs, per-task token limits, or incomplete output — especially when file exceeds ~150 lines or requires many repeated elements
---

# Large File Generator

## Overview
Generate large files in small, fast fragments with progress logging to prevent session hangs and stay within Claude's per-task limits.

**Core rule:** Never generate more than ~100 lines in a single tool call. For anything 500+ lines, use a generator script — one Write + one Bash run beats 20 Write calls.

## Strategy by File Size

| Size | Strategy |
|------|----------|
| < 150 lines | Write tool directly — no chunking |
| 150–800 lines | Chunked writes with progress echo |
| 800+ lines | Generator script (Python/Bash) |

## Fragment Size Limits

| Format | Max per chunk | Preferred |
|--------|--------------|-----------|
| CSV | 200 rows | 100 rows |
| HTML | 80 elements | 50 elements |
| Markdown | 100 lines | 60 lines |
| JSON | 100 objects | 50 objects |
| Any text | 150 lines | 80 lines |

## Method 1: Generator Script (Best for 800+ lines)

Write a script, run it once. No hanging.

```python
# gen_file.py — generates output.csv with 10,000 rows
import csv

TOTAL = 10000
CHUNK = 500

with open('output.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'name', 'value'])
    for i in range(TOTAL):
        writer.writerow([i, f'item_{i}', i * 1.5])
        if i % CHUNK == 0:
            print(f'[{i//CHUNK}/{TOTAL//CHUNK}] rows {i}–{min(i+CHUNK,TOTAL)}', flush=True)

print(f'Done — {TOTAL} rows written')
```

Run with: `python3 gen_file.py`

## Method 2: Chunked Writes (150–800 lines)

1. Use `Write` tool for the first chunk (file header + first N lines)
2. Append remaining chunks with `Bash` using heredoc
3. Log progress after each chunk

```bash
cat >> output.md << 'CHUNK'
## Section 3
...60 lines of content...
CHUNK
echo "[3/8] Section 3 done"
```

## Method 3: Direct Write (< 150 lines)

Use `Write` tool once — no special handling needed.

## Progress Logging Pattern

Always announce before starting, log after each chunk:

```
[START] output.csv — 5000 rows, 10 chunks of 500
[1/10]  rows 1–500 written
[2/10]  rows 501–1000 written
...
[DONE]  output.csv — 5000 rows complete
```

## Task Breakdown When Spread Across Turns

When a large file requires multiple Claude turns:
1. Announce: "Generating X in N chunks — logging each"
2. Each turn: complete exactly one chunk, log it, state what remains
3. Never stop mid-chunk — each fragment must be syntactically complete and valid
4. Use a tracking comment at the top of the file: `<!-- generated: 3/10 chunks -->`

## HTML-Specific Pattern

Generate skeleton once, inject content in loop:

```python
with open('page.html', 'w') as f:
    f.write('<!DOCTYPE html><html><body>\n')
    for i, item in enumerate(items):
        f.write(f'  <div class="card">{item}</div>\n')
        if i % 100 == 0:
            print(f'[HTML] {i}/{len(items)} cards', flush=True)
    f.write('</body></html>\n')
```

## Red Flags — Stop and Apply This Skill

- About to do a single `Write` call with 500+ lines
- No progress log planned for a file > 150 lines
- "I'll just write the whole thing at once, it's fine"
- Generating repeated HTML/CSV rows manually instead of via a loop
- Stopping mid-way and leaving a syntactically broken file

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| One Write call for 1000+ lines | Use generator script |
| No progress logging | `echo` or `print(..., flush=True)` after each chunk |
| Chunk > 200 lines | Reduce to 80–100 lines |
| Forgetting `flush=True` | Progress won't appear until end |
| Leaving half-written file on limit | Always finish current chunk before stopping |
