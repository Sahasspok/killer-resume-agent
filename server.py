#!/usr/bin/env python3
"""
Killer Resume Agent - Web Server & API
Encodes Jeff Su's 5 Research-Backed Rules with 7-Pillar Production QA Validation.
Runs on Python 3 Standard Library + PyMuPDF/pypdf.
"""
import http.server
import socketserver
import json
import urllib.parse
import os
import sys
import base64

from agent import KillerResumeAgent
from rules.rule4_google_xyz import transform_to_xyz, DIMENSIONS
from pdf_parser import extract_pdf_data
from pdf_generator import generate_pdf_from_markdown
from format_preserver import extract_pdf_style_fingerprint
from qa_validator import run_full_qa_pipeline, validate_pdf_render

PORT = 5050
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")
EXAMPLES_DIR = os.path.join(BASE_DIR, "examples")

agent = KillerResumeAgent()

class KillerResumeHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

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

        if parsed.path == "/api/upload-pdf":
            pdf_b64 = data.get("pdf_base64", "")
            filename = data.get("filename", "resume.pdf")
            if not pdf_b64:
                self.send_json_response({"error": "No PDF data supplied"}, status=400)
                return
            try:
                if "," in pdf_b64:
                    pdf_b64 = pdf_b64.split(",", 1)[1]
                pdf_bytes = base64.b64decode(pdf_b64)
                pdf_diag = extract_pdf_data(pdf_bytes, filename=filename)
                style_meta = extract_pdf_style_fingerprint(pdf_bytes)
                pdf_diag["style_meta"] = style_meta
                self.send_json_response(pdf_diag)
            except Exception as e:
                self.send_json_response({"error": f"Failed to parse PDF: {str(e)}"}, status=500)

        elif parsed.path == "/api/audit":
            resume_text = data.get("resume", "")
            jd_text = data.get("jd", "")
            pdf_b64 = data.get("pdf_base64", "")
            pdf_diag = None

            if pdf_b64:
                try:
                    if "," in pdf_b64:
                        pdf_b64 = pdf_b64.split(",", 1)[1]
                    pdf_bytes = base64.b64decode(pdf_b64)
                    pdf_diag = extract_pdf_data(pdf_bytes, filename=data.get("filename", "resume.pdf"))
                    pdf_diag["style_meta"] = extract_pdf_style_fingerprint(pdf_bytes)
                    resume_text = pdf_diag["text"]
                except Exception as e:
                    self.send_json_response({"error": f"Failed to parse PDF: {str(e)}"}, status=500)
                    return

            result = agent.run_comprehensive_audit(resume_text, jd_text)
            if pdf_diag:
                result["pdf_metadata"] = pdf_diag
            self.send_json_response(result)

        elif parsed.path == "/api/transform":
            resume_text = data.get("resume") or data.get("resume_text", "")
            jd_text = data.get("jd") or data.get("jd_text", "")
            pdf_b64 = data.get("pdf_base64", "")
            user_metrics = data.get("user_metrics", None)
            pdf_diag = None
            style_meta = data.get("style_meta", None)

            if pdf_b64:
                try:
                    if "," in pdf_b64:
                        pdf_b64 = pdf_b64.split(",", 1)[1]
                    pdf_bytes = base64.b64decode(pdf_b64)
                    pdf_diag = extract_pdf_data(pdf_bytes, filename=data.get("filename", "resume.pdf"))
                    style_meta = extract_pdf_style_fingerprint(pdf_bytes)
                    pdf_diag["style_meta"] = style_meta
                    resume_text = pdf_diag["text"]
                except Exception as e:
                    self.send_json_response({"error": f"Failed to parse PDF: {str(e)}"}, status=500)
                    return

            if user_metrics is None and "sahas" in resume_text.lower():
                from template_formatter import SAHAS_VERIFIED_METRICS
                user_metrics = SAHAS_VERIFIED_METRICS

            result = agent.transform_resume(resume_text, jd_text, style_meta=style_meta, user_metrics=user_metrics)
            if pdf_diag:
                result["pdf_metadata"] = pdf_diag
            if style_meta:
                result["style_meta"] = style_meta
            self.send_json_response(result)

        elif parsed.path == "/api/qa-report":
            source_text = data.get("source_resume", "")
            markdown_content = data.get("markdown", "")
            jd_text = data.get("jd", "")
            pdf_b64 = data.get("pdf_base64", "")
            user_metrics = data.get("user_metrics", None)
            pdf_bytes = None
            if pdf_b64:
                try:
                    if "," in pdf_b64:
                        pdf_b64 = pdf_b64.split(",", 1)[1]
                    pdf_bytes = base64.b64decode(pdf_b64)
                except Exception:
                    pass

            qa_res = run_full_qa_pipeline(
                source_text=source_text,
                output_markdown=markdown_content,
                jd_text=jd_text,
                pdf_bytes=pdf_bytes,
                user_metrics=user_metrics
            )
            self.send_json_response(qa_res)

        elif parsed.path == "/api/generate-pdf":
            markdown_content = data.get("markdown", "")
            style_meta = data.get("style_meta", None)
            if not markdown_content:
                self.send_json_response({"error": "No markdown content provided"}, status=400)
                return
            try:
                pdf_bytes = generate_pdf_from_markdown(markdown_content, style_meta=style_meta)
                pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
                pdf_qa = validate_pdf_render(pdf_bytes, source_markdown=markdown_content)
                self.send_json_response({
                    "pdf_base64": pdf_b64,
                    "filename": "killer_resume_updated.pdf",
                    "size_kb": round(len(pdf_bytes) / 1024, 1),
                    "style_meta": style_meta,
                    "pdf_qa": pdf_qa
                })
            except Exception as e:
                self.send_json_response({"error": f"Failed to generate PDF: {str(e)}"}, status=500)

        elif parsed.path == "/api/xyz":
            bullet = data.get("bullet", "")
            metric = data.get("metric", None)
            result = transform_to_xyz(bullet, metric_value=metric)
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
        sample_pdf_path = os.path.join(EXAMPLES_DIR, "sample_resume.pdf")

        resume_text = ""
        jd_text = ""
        pdf_b64 = ""
        if os.path.exists(sample_resume_path):
            with open(sample_resume_path, "r", encoding="utf-8") as f:
                resume_text = f.read()
        if os.path.exists(sample_jd_path):
            with open(sample_jd_path, "r", encoding="utf-8") as f:
                jd_text = f.read()
        if os.path.exists(sample_pdf_path):
            with open(sample_pdf_path, "rb") as f:
                pdf_b64 = base64.b64encode(f.read()).decode("utf-8")

        self.send_json_response({
            "sample_resume": resume_text,
            "sample_jd": jd_text,
            "sample_pdf_b64": pdf_b64,
            "sample_pdf_name": "sample_resume.pdf"
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
        print(f"🚀 KILLER RESUME AGENT (QA CERTIFIED) IS LIVE AT:")
        print(f"   http://localhost:{port}")
        print(f"================================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.server_close()

if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run_server(p)
