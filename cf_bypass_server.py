#!/usr/bin/env python3
"""Lightweight Cloudflare bypass server using cloudscraper."""
import os
import sys
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

try:
    import cloudscraper
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True},
        delay=10
    )
    logger.info("cloudscraper initialized successfully")
except ImportError:
    logger.error("cloudscraper not installed. Run: pip install cloudscraper")
    sys.exit(1)

class BypassHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        hostname = self.headers.get('x-hostname')
        if not hostname:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "x-hostname header required"}).encode())
            return

        url = f"https://{hostname}{self.path}"
        logger.info(f"Fetching: {url}")

        try:
            resp = scraper.get(url, timeout=30)
            self.send_response(resp.status_code)
            for key, value in resp.headers.items():
                if key.lower() not in ('transfer-encoding', 'content-encoding', 'connection'):
                    self.send_header(key, value)
            self.send_header('Content-Type', resp.headers.get('Content-Type', 'text/html'))
            self.end_headers()
            self.wfile.write(resp.content)
            logger.info(f"Success: {resp.status_code} ({len(resp.content)} bytes)")
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def do_POST(self):
        hostname = self.headers.get('x-hostname')
        if not hostname:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "x-hostname header required"}).encode())
            return

        url = f"https://{hostname}{self.path}"
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length else None
        content_type = self.headers.get('Content-Type', 'application/x-www-form-urlencoded')

        logger.info(f"POST to: {url}")
        try:
            resp = scraper.post(url, data=body, headers={'Content-Type': content_type}, timeout=30)
            self.send_response(resp.status_code)
            for key, value in resp.headers.items():
                if key.lower() not in ('transfer-encoding', 'content-encoding', 'connection'):
                    self.send_header(key, value)
            self.end_headers()
            self.wfile.write(resp.content)
            logger.info(f"Success: {resp.status_code} ({len(resp.content)} bytes)")
        except Exception as e:
            logger.error(f"Error posting to {url}: {e}")
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def log_message(self, format, *args):
        logger.info(f"{self.address_string()} - {format % args}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), BypassHandler)
    logger.info(f"CF Bypass server running on port {port}")
    server.serve_forever()
