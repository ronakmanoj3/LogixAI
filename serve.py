"""Local ReStock browser interface. Run: python3 serve.py --open"""
import argparse
import copy
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import webbrowser
import os

from reference_engine import evaluate, number

ROOT = Path(__file__).resolve().parent
CASE = json.loads((ROOT / "scenario.json").read_text())
FIELDS = {
    "on_hand": (0, 1000000), "daily_demand": (0, 1000000),
    "transfer_available": (0, 1000000), "response_budget": (0, 1000000000),
    "regular_day": (1, 60), "regular_quantity": (0, 1000000),
    "express_day": (1, 60), "contribution_per_unit": (0, 1000000),
}


def build_case(values):
    if not isinstance(values, dict) or set(values) != set(FIELDS):
        raise ValueError("Provide all eight scenario inputs")
    case = copy.deepcopy(CASE)
    for key, value in values.items():
        low, high = FIELDS[key]
        number(value, key, integer=key not in {"response_budget", "contribution_per_unit"}, minimum=low)
        if value > high:
            raise ValueError(f"{key} must be at most {high}")
        if key in case:
            case[key] = value
    case["regular_receipts"][0] = {"day": values["regular_day"], "quantity": values["regular_quantity"]}
    case["actions"][2]["day"] = values["express_day"]
    return case


class Handler(BaseHTTPRequestHandler):
    def respond(self, status, body, content_type="application/json; charset=utf-8"):
        if not isinstance(body, bytes):
            body = json.dumps(body, allow_nan=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/defaults":
            values = {key: CASE[key] for key in FIELDS if key in CASE}
            values.update(regular_day=CASE["regular_receipts"][0]["day"],
                          regular_quantity=CASE["regular_receipts"][0]["quantity"],
                          express_day=CASE["actions"][2]["day"])
            self.respond(200, values)
        elif path == "/api/chat/status":
            self.respond(200, {"configured": bool(os.environ.get("OPENAI_API_KEY")),
                               "model": os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")})
        elif path in {"/", "/index.html", "/app.js", "/style.css"}:
            file = "index.html" if path == "/" else path[1:]
            mime = {"html": "text/html", "js": "text/javascript", "css": "text/css"}[file.split(".")[-1]]
            self.respond(200, (ROOT / "web" / file).read_bytes(), mime + "; charset=utf-8")
        else:
            self.respond(404, {"error": "Not found"})

    def do_POST(self):
        if self.path not in {"/api/evaluate", "/api/chat"}:
            return self.respond(404, {"error": "Not found"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 30000:
                raise ValueError("Request must contain a small JSON payload")
            payload = json.loads(self.rfile.read(length))
            if self.path == "/api/evaluate":
                case = build_case(payload)
                self.respond(200, {"case": case, "result": evaluate(case)})
                return
            self.handle_chat(payload)
        except (ValueError, KeyError, TypeError) as error:
            self.respond(400, {"error": str(error)})

    def handle_chat(self, payload):
        message = payload.get("message") if isinstance(payload, dict) else None
        if not isinstance(message, str) or not message.strip() or len(message) > 2000:
            return self.respond(400, {"error": "Enter a message of 1–2000 characters."})
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return self.respond(503, {"error": "AI is not configured yet. Stop the server, set OPENAI_API_KEY in Command Prompt, then restart ReStock. See AI_CHATBOT_SETUP.md."})
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
            context = {
                "scenario": payload.get("scenario", {}),
                "simulation_result": payload.get("result", {}),
                "note": "This is synthetic teaching data. Explain only values supported by the provided result. If a requested what-if scenario has not been calculated, say so and explain it must be run in the simulator first. Do not invent computed results. No orders or transfers can be executed."
            }
            instructions = (
                "You are ReStock AI, a careful retail inventory decision-support assistant. "
                "Answer in plain language, with concise headings or bullets when useful. "
                "Use the supplied current scenario and simulation_result as the source of truth for numeric results. "
                "Do not claim to have rerun the simulator, accessed live stock, checked suppliers, used real routes, or placed orders. "
                "Distinguish contribution from revenue and cash required from incremental response cost. "
                "If the current result is missing, ask the user to run the Stock Simulator. "
                "For a hypothetical change not present in the supplied calculation, explain the likely mechanics but do not fabricate a result; ask the user to change the inputs/run the what-if tool. "
                "Always state that recommendations are model-based and require human review before real action."
            )
            history = payload.get("history", [])
            history_lines = []
            if isinstance(history, list):
                for item in history[-8:]:
                    if isinstance(item, dict) and item.get("role") in {"user", "assistant"} and isinstance(item.get("content"), str):
                        history_lines.append(item["role"].upper() + ": " + item["content"][:2000])
            history_text = "\n".join(history_lines)
            response = client.responses.create(
                model=model,
                instructions=instructions,
                input="CURRENT RESTOCK CASE (JSON):\n" + json.dumps(context, ensure_ascii=False) + "\n\nRECENT CHAT HISTORY:\n" + history_text + "\n\nLATEST USER QUESTION: " + message,
                max_output_tokens=700,
            )
            answer = getattr(response, "output_text", "") or "I could not generate a response. Please try again."
            self.respond(200, {"answer": answer, "model": model})
        except ImportError:
            self.respond(503, {"error": "The OpenAI Python package is missing. Run: python -m pip install -r requirements.txt"})
        except Exception as error:
            # Avoid returning provider internals, secrets, or raw exception details to the browser.
            print(f"AI request failed: {type(error).__name__}: {error}", flush=True)
            self.respond(502, {"error": "The AI request failed. Check your API key, API billing/model access and internet connection, then try again. Details are in the server terminal."})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--open", action="store_true")
    args = parser.parse_args()
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    except OSError as error:
        parser.exit(1, f"Could not start ReStock: {error}\nTry: python3 serve.py --port 8001 --open\n")
    url = f"http://localhost:{args.port}/"
    print(f"ReStock is running at {url}\nKeep this Terminal open. Press Ctrl+C to stop.\n", flush=True)
    if args.open:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nReStock stopped.")
    finally:
        server.server_close()
