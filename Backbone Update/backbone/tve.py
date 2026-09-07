"""06 TVE — Truth Vector Engine: detectare manipulare pe 6 axe (DSEI-VI)."""
from dataclasses import dataclass

AXES = ("EMOT", "URG", "AUTH", "SOC", "REC", "SCARC")   # emotional, urgency,
# authority, social proof, reciprocity, scarcity


@dataclass(frozen=True)
class TVEScore:
    axes: dict
    flagged: bool
    def __getitem__(self, k): return self.axes[k]


def flag_rule(axes: dict) -> bool:
    """Flag dacă orice axă ≥ 0.7 SAU media ≥ 0.5."""
    vals = [float(axes[k]) for k in AXES]
    return any(v >= 0.7 for v in vals) or (sum(vals) / len(vals)) >= 0.5


# Scorer lexical ilustrativ. Producție = detectorul tău NLP antrenat
# (32 teste în repo-ul tve-core). Regula de flag e nucleul testabil.
LEX = {
    "EMOT":  ("doar tu", "nimeni nu", "singur", "only you", "no one else"),
    "URG":   ("acum", "imediat", "urgent", "hurry", "now or never"),
    "AUTH":  ("autoritate", "doctorul a zis", "expert says", "trust me i am"),
    "SOC":   ("toata lumea", "toti prietenii", "everyone does", "millions"),
    "REC":   ("ti-am dat", "imi datorezi", "you owe", "i gave you"),
    "SCARC": ("ultima șansă", "ultima sansa", "only few left", "se termină"),
}


def score(content: str) -> TVEScore:
    low = content.lower()
    axes = {}
    for k, words in LEX.items():
        hits = sum(w in low for w in words)
        axes[k] = min(1.0, 0.15 + 0.55 * hits) if hits else 0.0
    return TVEScore(axes=axes, flagged=flag_rule(axes))