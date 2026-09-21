#!/usr/bin/env python3
"""
Killer Resume Agent - Web Server & API
Runs on Python 3 Standard Library (Zero third-party dependencies required).
"""
import http.server
import socketserver
import json
import urllib.parse
import os
import sys

from agent import KillerResumeAgent
from rules.rule4_google_xyz import transform_to_xyz, DIMENSIONS

PORT = 5050
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")
EXAMPLES_DIR = os.path.join(BASE_DIR, "examples")

agent = KillerResumeAgent()

class KillerResumeHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/sample":
            self.handle_sample_data()
        elif parsed.path == "/" or parsed.path == "":
            self.path = "/index.html"
            super().do_GET()
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_length).decode("utf-8")

        try:
            data = json.loads(post_body) if post_body else {}
        except json.JSONDecodeError:
            self.send_json_response({"error": "Invalid JSON payload"}, status=400)
            return

        if parsed.path == "/api/audit":
            resume_text = data.get("resume", "")
            jd_text = data.get("jd", "")
            result = agent.run_comprehensive_audit(resume_text, jd_text)
            self.send_json_response(result)

        elif parsed.path == "/api/transform":
            resume_text = data.get("resume", "")
            jd_text = data.get("jd", "")
            result = agent.transform_resume(resume_text, jd_text)
            self.send_json_response(result)

        elif parsed.path == "/api/xyz":
            bullet = data.get("bullet", "")
            result = transform_to_xyz(bullet)
            self.send_json_response(result)

        elif parsed.path == "/api/clarify":
            bullet = data.get("bullet", "")
            xyz = transform_to_xyz(bullet)
            self.send_json_response({
                "bullet": bullet,
                "xyz": xyz,
                "dimensions": DIMENSIONS
            })
        else:
            self.send_json_response({"error": f"Endpoint {parsed.path} not found"}, status=404)

    def handle_sample_data(self):
        sample_resume_path = os.path.join(EXAMPLES_DIR, "sample_resume.md")
        sample_jd_path = os.path.join(EXAMPLES_DIR, "sample_jd.md")

        resume_text = ""
        jd_text = ""
        if os.path.exists(sample_resume_path):
            with open(sample_resume_path, "r", encoding="utf-8") as f:
                resume_text = f.read()
        if os.path.exists(sample_jd_path):
            with open(sample_jd_path, "r", encoding="utf-8") as f:
                jd_text = f.read()

        self.send_json_response({
            "sample_resume": resume_text,
            "sample_jd": jd_text
        })

    def send_json_response(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

def run_server(port=PORT):
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), KillerResumeHandler) as httpd:
        print(f"================================================================")
        print(f"🚀 KILLER RESUME AGENT IS LIVE & HOSTED AT:")
        print(f"   http://localhost:{port}")
        print(f"================================================================")
        print("Ready for live user audits and Google XYZ transformations.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.server_close()

if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run_server(p)
