"""Privacy Guard — redact PII ÎNAINTE de model (DSEI-V).
Log-urile păstrează categoria și nivelul, nu conținutul."""
import re

PATTERNS = {   # ordinea contează: CARD înainte de PHONE
    "CARD":  re.compile(r"\b(?:\d[ -]?){13,19}\b"),
    "PHONE": re.compile(r"\+?\d[\d\s\-]{7,}\d"),
    "EMAIL": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
}


def redact(text: str):
    """Returnează (text_redactat, categorii) — categoriile doar, niciodată conținut."""
    cats, out = [], text
    for cat, rx in PATTERNS.items():
        if rx.search(out):
            cats.append(cat)
            out = rx.sub(f"[{cat}-REDACTED]", out)
    return out, cats