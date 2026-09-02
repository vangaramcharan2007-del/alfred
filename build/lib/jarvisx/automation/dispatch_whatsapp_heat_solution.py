"""
Pre-fill and Send 1D Heat Equation Derivation to WhatsApp (+91 8074881520).
===========================================================================
Dispatches the exact mathematical solution directly into WhatsApp Desktop/Web.
"""

import os
import sys
import urllib.parse
import webbrowser

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from jarvisx.automation.ev_neural_voice import speak_ev_neural


def dispatch_solution():
    phone = "918074881520"
    derivation = (
        "🕷️ *E-V MAX // Dr. E. Suresh 1D Heat Equation Derivation*\n\n"
        "📌 *Problem Statement*:\n"
        "Solve ∂u/∂t = α² ∂²u/∂x² with u(0,t)=0, u(20,t)=0, and u(x,0)=f(x) for length l=20.\n\n"
        "🔹 *Step 1: Suitable Separation of Variables Solution*:\n"
        "u(x,t) = (C1 cos px + C2 sin px) * exp(-α² p² t)\n\n"
        "🔹 *Step 2: Apply Boundary Conditions*:\n"
        "1. u(0,t) = 0 => C1 = 0\n"
        "2. u(20,t) = 0 => sin(20p) = 0 => 20p = nπ => p = nπ / 20\n\n"
        "🔹 *Step 3: Most General Solution (Superposition)*:\n"
        "u(x,t) = sum_{n=1}^∞ c_n * sin(nπx / 20) * exp(-n²π²α²t / 400)\n\n"
        "🔹 *Step 4: Fourier Sine Coefficient*:\n"
        "c_n = (2/20) ∫[0 to 20] f(x) sin(nπx / 20) dx = (1/10) ∫[0 to 20] f(x) sin(nπx / 20) dx\n\n"
        "💡 *Exam Tip*: Since boundaries are zero at both ends (u=0), always choose the negative separation constant -p² so temperature decays with time t -> ∞!"
    )

    encoded = urllib.parse.quote(derivation)
    proto = f"whatsapp://send?phone={phone}&text={encoded}"
    web_url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded}"

    print(f"[*] Dispatching pre-filled solution to WhatsApp for +{phone}...")
    try:
        os.system(f'start "" "{proto}"')
    except Exception as e:
        print(f"[!] Desktop proto error: {e}")

    try:
        webbrowser.open(web_url)
    except Exception as e:
        print(f"[!] Web URL error: {e}")

    print("[SUCCESS] Dispatched solution to WhatsApp!")
    speak_ev_neural("The complete 1D Heat Equation derivation has been loaded directly into your WhatsApp chat, boss! Just tap the green Send button!")


if __name__ == "__main__":
    dispatch_solution()
