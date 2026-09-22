"""
Jarvis X - Universal eLab Groq AI Bridge
Local lightweight proxy that connects Chrome Console on eLab to Groq AI with zero CORS issues.
"""

import sys
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.error

PORT = 8765

class GroqBridgeHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_POST(self):
        if self.path == '/solve':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                payload = json.loads(post_data)
                groq_key = payload.get('groq_key') or os.environ.get('GROQ_API_KEY', '').strip()
                gemini_key = os.environ.get('GEMINI_API_KEY', '').strip()
                problem_desc = payload.get('problem', '')
                error_diff = payload.get('diff', '')
                session_name = payload.get('session', '')

                if not groq_key and not gemini_key:
                    self._send_json(400, {'error': 'No Groq or Gemini API key provided. Set GROQ_API_KEY or pass in request.'})
                    return

                # Construct AI Prompt
                system_instruction = (
                    "You are an elite competitive programmer writing solutions in pure standard C (C99) for SRM eLab.\n"
                    "CRITICAL eLab RULES:\n"
                    "1. Return ONLY the executable C code inside ```c ... ``` markdown block. No conversational text.\n"
                    "2. If topic is Sorting, DO NOT use library qsort(); write a manual bubble sort or insertion sort (eLab static checker fails qsort).\n"
                    "3. Pay strict attention to input format (number of testcases T, 0-indexed vs 1-indexed, spacing, exact newlines).\n"
                    "4. Use standard library: <stdio.h>, <stdlib.h>, <string.h>, <math.h>.\n"
                    "5. Handle edge cases (empty inputs, 0 values, negative numbers, extreme constraints).\n"
                )

                user_prompt = f"Topic/Session: {session_name}\n\nProblem Statement & Format:\n{problem_desc}\n"
                if error_diff:
                    user_prompt += f"\nPrevious attempt failed with diff:\n{error_diff}\nFix the logic to pass 100% of all test cases.\n"

                code = ""
                if groq_key:
                    # Call Groq API (llama-3.3-70b-versatile)
                    req_body = json.dumps({
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.1,
                        "max_tokens": 1500
                    }).encode('utf-8')

                    groq_req = urllib.request.Request(
                        "https://api.groq.com/openai/v1/chat/completions",
                        data=req_body,
                        headers={
                            "Authorization": f"Bearer {groq_key}",
                            "Content-Type": "application/json"
                        }
                    )

                    with urllib.request.urlopen(groq_req, timeout=15) as resp:
                        res = json.loads(resp.read().decode('utf-8'))
                        raw = res['choices'][0]['message']['content']
                        code = self._extract_code(raw)

                elif gemini_key:
                    # Fallback to Gemini API if key is present
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
                    req_body = json.dumps({
                        "contents": [{
                            "parts": [{"text": system_instruction + "\n\n" + user_prompt}]
                        }]
                    }).encode('utf-8')

                    gem_req = urllib.request.Request(
                        url,
                        data=req_body,
                        headers={"Content-Type": "application/json"}
                    )

                    with urllib.request.urlopen(gem_req, timeout=15) as resp:
                        res = json.loads(resp.read().decode('utf-8'))
                        raw = res['candidates'][0]['content']['parts'][0]['text']
                        code = self._extract_code(raw)

                self._send_json(200, {'status': 'ok', 'code': code})

            except urllib.error.HTTPError as e:
                err_text = e.read().decode('utf-8', errors='ignore')
                self._send_json(e.code, {'error': f"AI API Error: {err_text}"})
            except Exception as ex:
                self._send_json(500, {'error': str(ex)})
        else:
            self._send_json(404, {'error': 'Not found'})

    def _extract_code(self, raw):
        if "```c" in raw:
            return raw.split("```c")[1].split("```")[0].strip()
        elif "```" in raw:
            return raw.split("```")[1].split("```")[0].strip()
        return raw.strip()

    def _send_json(self, status, obj):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode('utf-8'))

    def log_message(self, format, *args):
        # Clean terminal logging
        sys.stdout.write(f"[GROQ-BRIDGE] {args[0]} -> {args[1]}\n")

def run():
    server = HTTPServer(('127.0.0.1', PORT), GroqBridgeHandler)
    print(f"[ALFRED] Universal AI Solver Bridge running on http://127.0.0.1:{PORT}")
    server.serve_forever()

if __name__ == '__main__':
    run()
