#!/usr/bin/env python3
"""
Learning app server — http://localhost:3131
Run: python3 server.py
"""
from http.server import ThreadingHTTPServer

from app.config import PORT, HOST, DEMO_MODE, TTS_VOICE
from app.handlers.router import ProxyHandler

if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), ProxyHandler)
    print(f"\n  ✦ Learning app  → http://{HOST}:{PORT}")
    print(f"  ✦ Dashboard     → http://{HOST}:{PORT}/index.html")
    print(f"  Demo mode: {'ON (generation, Python terminal & create disabled)' if DEMO_MODE else 'off'}")
    print(f"  Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Proxy stopped.")
