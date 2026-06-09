FROM python:3.13-slim

# espeak-ng provides Linux text-to-speech (replaces macOS `say`/`afconvert`).
RUN apt-get update \
    && apt-get install -y --no-install-recommends espeak-ng \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# HF Spaces serves on 7860. Bind all interfaces and run as a public read-only demo
# (generation, the Python terminal, and program/lesson creation are disabled).
ENV HOST=0.0.0.0 \
    PORT=7860 \
    DEMO_MODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 7860

CMD ["python3", "server.py"]
