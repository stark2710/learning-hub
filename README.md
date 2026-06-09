---
title: Learning Hub
emoji: ⚡
colorFrom: purple
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# Learning Hub — public read-only demo

A self-paced mastery-learning app: pick a program, work through lessons (mental
models, code walkthroughs, production stories, practice), and chat with an AI
mentor about any lesson.

## This deployment is a read-only demo

Running with `DEMO_MODE=1`, so the following are **disabled** (the server returns
`403` and the UI hides the controls):

- Lesson generation ("Generate Next Lesson")
- The in-browser Python terminal (Run)
- Creating programs / domains / modules / lessons

Still available:

- Browsing every pre-generated lesson
- **"Ask Master" chat** — bring your own Claude API key (stored only in your
  browser, sent straight to Anthropic via a same-origin proxy)
- **TTS narration** via `espeak-ng` (robotic; macOS dev uses the native `say` voice)

## Run locally (full features)

```bash
python3 server.py          # http://localhost:3131 — generation + Python terminal ON
```

## Run the demo locally (Docker)

```bash
docker build -t learning-hub .
docker run --rm -p 7860:7860 learning-hub   # http://localhost:7860
```

## Configuration (env vars)

| Var | Default | Purpose |
|-----|---------|---------|
| `PORT` | `3131` | Listen port (HF Spaces uses `7860`) |
| `HOST` | `127.0.0.1` | Bind address (`0.0.0.0` in container) |
| `DEMO_MODE` | _off_ | `1`/`true` disables generation, Python terminal, and creation |
