import re
from collections import Counter, defaultdict

STOP = set("""
a i o u v s z k na do se je že žeho žejo že? ať aby kdo která které který kteří
ať je jsou jsem jsme jste bych by bys byla byl bylo byli byly
to ten ta ty toto tato tady tam kde kdy proč jak protože
""".split())

def tokenize(text:str):
    text = text.lower()
    text = re.sub(r"[^a-zá-ž0-9\s]+", " ", text)
    toks = [t for t in text.split() if len(t) > 2 and t not in STOP]
    return toks

def keyword_summary(answers):
    # answers: list of dict/rows with fields: week, display_name, role, answer_text
    all_text = " ".join([a["answer_text"] or "" for a in answers])
    toks = tokenize(all_text)
    freq = Counter(toks)
    top = [w for w,_ in freq.most_common(20)]
    return top

def theme_hints(answers):
    # very light rule-based flags
    flags = defaultdict(int)
    text = " ".join([a["answer_text"] or "" for a in answers]).lower()
    for key, patterns in {
        "kontrola": ["kontrol", "drž", "pust", "řízení"],
        "důvěra": ["důvěr", "věř", "nedůvěr"],
        "strach": ["boj", "strach", "obav"],
        "loajalita": ["loajal", "vděk", "dluž", "zklam"],
        "identita": ["identit", "já ", "role", "vlastník"],
        "tabu": ["nesmí", "neříká", "zakáz", "tabu", "neotevír"]
    }.items():
        for p in patterns:
            if p in text:
                flags[key] += 1
    return dict(sorted(flags.items(), key=lambda kv: kv[1], reverse=True))

def draft_facilitator_notes(answers):
    # Produces short notes: keywords + themes
    kw = keyword_summary(answers)
    th = theme_hints(answers)
    lines = []
    if kw:
        lines.append("Klíčová slova (heuristika): " + ", ".join(kw[:12]))
    if th:
        lines.append("Naznačená témata: " + ", ".join([f"{k}({v})" for k,v in list(th.items())[:6]]))
    lines.append("Pozn.: Toto je pouze heuristické shrnutí bez interpretace a bez klinických závěrů.")
    return "\n".join(lines)
