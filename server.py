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

from agent import KillerResumeAgent, LLMClient
from rules.rule4_google_xyz import transform_to_xyz, DIMENSIONS
from pdf_parser import extract_pdf_data
from pdf_generator import generate_pdf_from_markdown
from format_preserver import extract_pdf_style_fingerprint
from qa_validator import run_full_qa_pipeline, validate_pdf_render
from template_formatter import extract_roles_from_resume

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
        elif parsed.path == "/api/config":
            self.handle_config()
        elif parsed.path == "/" or parsed.path == "":
            self.path = "/index.html"
            super().do_GET()
        else:
            super().do_GET()

    def handle_config(self):
        detected = {
            "gemini": bool(os.environ.get("GEMINI_API_KEY")),
            "groq": bool(os.environ.get("GROQ_API_KEY")),
            "openrouter": bool(os.environ.get("OPENROUTER_API_KEY")),
            "mistral": bool(os.environ.get("MISTRAL_API_KEY")),
            "openai": bool(os.environ.get("OPENAI_API_KEY")),
            "anthropic": bool(os.environ.get("ANTHROPIC_API_KEY")),
        }
        self.send_json_response({"detected_keys": detected})

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
                pdf_diag["detected_roles"] = extract_roles_from_resume(pdf_diag.get("text", ""))
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
            result["detected_roles"] = extract_roles_from_resume(resume_text)
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
            provider = data.get("provider", "heuristic")
            api_key = data.get("api_key", "")
            model = data.get("model", "")

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

            try:
                llm = LLMClient(provider=provider, api_key=api_key, model=model)
                t_agent = KillerResumeAgent(llm_client=llm)

                result = t_agent.transform_resume(resume_text, jd_text, style_meta=style_meta, user_metrics=user_metrics)
                if pdf_diag:
                    result["pdf_metadata"] = pdf_diag
                if style_meta:
                    result["style_meta"] = style_meta
                result.pop("pdf_bytes", None)
                self.send_json_response(result)
            except Exception as e:
                print(f"❌ [AGENT SERVER ERROR] /api/transform error: {e}")
                self.send_json_response({"error": f"Transformation error: {str(e)}"}, status=500)

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
            notes = data.get("notes") or data.get("metric", "")
            provider = data.get("provider", "heuristic")
            api_key = data.get("api_key", "")
            model = data.get("model", "")
            role = data.get("role", "")
            jd = data.get("jd", "")

            try:
                llm = LLMClient(provider=provider, api_key=api_key, model=model)
                rewritten = llm.rewrite_bullet_xyz(raw_bullet=bullet, user_notes=notes, role_title=role, jd_context=jd)
                self.send_json_response({
                    "original": bullet,
                    "notes": notes,
                    "rewritten": rewritten,
                    "provider": llm.provider,
                    "model": llm.model
                })
            except Exception as e:
                print(f"❌ [AGENT SERVER ERROR] /api/xyz failed: {e}")
                # Fallback to heuristic rewrite so user is never blocked
                heuristic_llm = LLMClient(provider="heuristic")
                fallback = heuristic_llm.rewrite_bullet_xyz(raw_bullet=bullet, user_notes=notes, role_title=role, jd_context=jd)
                self.send_json_response({
                    "original": bullet,
                    "notes": notes,
                    "rewritten": fallback,
                    "provider": "heuristic (fallback)",
                    "error": str(e)
                })

        elif parsed.path == "/api/providers":
            self.send_json_response({
                "providers": [
                    {
                        "id": "gemini",
                        "name": "Google Gemini (Free Tier)",
                        "free": True,
                        "limits": "15 req/min • 1,500 req/day free",
                        "default_model": "gemini-2.0-flash",
                        "models": ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash-latest", "gemini-1.5-flash-8b", "gemini-1.5-pro"],
                        "key_url": "https://aistudio.google.com/"
                    },
                    {
                        "id": "groq",
                        "name": "Groq (Free & Blazing Fast)",
                        "free": True,
                        "limits": "30 req/min • 14,400 req/day free (No card required)",
                        "default_model": "llama-3.3-70b-versatile",
                        "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"],
                        "key_url": "https://console.groq.com/keys"
                    },
                    {
                        "id": "openrouter",
                        "name": "OpenRouter (Free Models)",
                        "free": True,
                        "limits": "Free tier access to DeepSeek R1, Llama 3.3, Gemini 2.0 Flash",
                        "default_model": "google/gemini-2.0-flash-exp:free",
                        "models": ["google/gemini-2.0-flash-exp:free", "meta-llama/llama-3.3-70b-instruct:free", "deepseek/deepseek-r1:free", "qwen/qwen-2.5-coder-32b-instruct:free"],
                        "key_url": "https://openrouter.ai/keys"
                    },
                    {
                        "id": "mistral",
                        "name": "Mistral AI (Free Tier)",
                        "free": True,
                        "limits": "Free experimentation tier",
                        "default_model": "mistral-small-latest",
                        "models": ["mistral-small-latest", "open-mistral-7b"],
                        "key_url": "https://console.mistral.ai/"
                    },
                    {
                        "id": "openai",
                        "name": "OpenAI (GPT-4o-mini)",
                        "free": False,
                        "limits": "Pay-as-you-go ($0.15/1M tokens)",
                        "default_model": "gpt-4o-mini",
                        "models": ["gpt-4o-mini", "gpt-4o"],
                        "key_url": "https://platform.openai.com/api-keys"
                    },
                    {
                        "id": "anthropic",
                        "name": "Anthropic Claude (3.5 Sonnet)",
                        "free": False,
                        "limits": "Pay-as-you-go",
                        "default_model": "claude-3-5-sonnet-20241022",
                        "models": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
                        "key_url": "https://console.anthropic.com/"
                    },
                    {
                        "id": "ollama",
                        "name": "Ollama (Local / 100% Free)",
                        "free": True,
                        "limits": "Unlimited local compute (no API key)",
                        "default_model": "llama3",
                        "models": ["llama3", "mistral", "qwen2.5"],
                        "key_url": "https://ollama.com/"
                    },
                    {
                        "id": "heuristic",
                        "name": "Offline Rule Engine (Built-in)",
                        "free": True,
                        "limits": "100% Free • No API key • Zero network latency",
                        "default_model": "rule-engine",
                        "models": ["rule-engine"],
                        "key_url": ""
                    }
                ]
            })

        elif parsed.path == "/api/clarify":
            bullet = data.get("bullet", "")
            xyz = transform_to_xyz(bullet)
            self.send_json_response({
                "bullet": bullet,
                "xyz": xyz,
                "dimensions": DIMENSIONS
            })
        elif parsed.path == "/api/detect-roles":
            resume_text = data.get("resume", "")
            pdf_b64 = data.get("pdf_base64", "")
            if pdf_b64 and not resume_text:
                try:
                    if "," in pdf_b64:
                        pdf_b64 = pdf_b64.split(",", 1)[1]
                    pdf_bytes = base64.b64decode(pdf_b64)
                    pdf_diag = extract_pdf_data(pdf_bytes)
                    resume_text = pdf_diag.get("text", "")
                except Exception:
                    pass
            roles = extract_roles_from_resume(resume_text)
            self.send_json_response({"roles": roles})

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
        def json_serializer(obj):
            if isinstance(obj, bytes):
                return base64.b64encode(obj).decode("utf-8")
            return str(obj)

        body = json.dumps(data, default=json_serializer).encode("utf-8")
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
