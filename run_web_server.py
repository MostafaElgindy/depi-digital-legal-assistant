#!/usr/bin/env python3
"""
Simple HTTP Server for serving web frontend
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# Get web directory
WEB_DIR = os.path.join(os.path.dirname(__file__), 'web')
PORT = 8080

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_GET(self):
        # Serve index.html for root
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")

if __name__ == '__main__':
    # Change to web directory
    os.chdir(WEB_DIR)
    
    print(f"\n{'='*60}")
    print(f"🚀 Web Server جاري التشغيل...")
    print(f"{'='*60}")
    print(f"📍 الموقع: http://127.0.0.1:{PORT}")
    print(f"📂 المجلد: {WEB_DIR}")
    print(f"⚠️  اضغط Ctrl+C للإيقاف")
    print(f"{'='*60}\n")

    try:
        with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
            print(f"✅ الخادم يعمل بنجاح على http://127.0.0.1:{PORT}")
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 48:  # Port already in use
            print(f"❌ خطأ: المنفذ {PORT} مستخدم بالفعل")
            print(f"جرب منفذ مختلف أو أغلق البرنامج الآخر")
        else:
            print(f"❌ خطأ: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  الخادم توقف بنجاح")
