#!/usr/bin/env python3
"""
TRIZ method router — heuristic suggestions from problem text.
Matches keyword/intent cues from references/triz-method-map.md and
returns ranked methods plus contradiction guesses.

Usage:
    python triz_router.py "problem description text"
    python triz_router.py                  # prints usage

Standard library only — Python 3.8+.
"""

from __future__ import annotations

import sys
import json
import re
from typing import Any


def _kw_match(kw: str, text: str) -> bool:
    """Match a keyword with \\b word boundaries."""
    return bool(re.search(rf"\b{re.escape(kw)}\b", text))


# ── Rules table ──────────────────────────────────────────────────────────────
# Each rule: (keywords_tuple, method, weight, why_template)
# keywords are lowercase whole words/phrases matched with \\b boundaries.
# Extend this table to add new heuristics without restructuring the router.
RULES: list[tuple[tuple[str, ...], str, int, str]] = [
    # -- Engineering Contradiction signals
    (
        ("but", "trade-off", "tradeoff", "at the cost of",
         "however", "increases", "decreases", "more", "less",
         "ma", "però", "tuttavia", "a scapito di", "aumenta",
         "diminuisce", "più", "meno"),
        "Engineering Contradiction + 40 Inventive Principles",
        3, "contradiction cue detected (trade-off / conflict connector)"
    ),
    # -- Physical Contradiction signals
    (
        ("must be both", "must be", "present and absent", "presente e assente",
         "fast and slow", "veloce e lento", "big and small", "grande e piccolo",
         "on and off", "hot and cold", "caldo e freddo",
         "deve essere", "allo stesso tempo", "contemporaneamente",
         "opposite", "opposto", "opposti", "duplice"),
        "Physical Contradiction + Separation",
        4, "physical contradiction cue (opposite/dual-state language)"
    ),
    # -- Trimming signals
    (
        ("too many", "too complex", "troppe", "troppi", "troppo", "expensive",
         "costoso", "costosa", "remove", "rimuovere", "simplify", "semplifica",
         "redundant", "ridondante", "overhead", "bloated", "snellire",
         "eliminare", "tagliare", "dimagrire"),
        "Trimming",
        3, "complexity/bloat/redundancy cue"
    ),
    # -- Root Cause Analysis signals
    (
        ("keeps happening", "recurring", "ricorrente", "again", "ancora",
         "di nuovo", "fails", "fallisce", "root", "radice", "why", "perché",
         "intermittent", "intermittente", "persiste", "ripete", "why does"),
        "Root Cause Analysis",
        3, "recurrence / root-cause language"
    ),
    # -- Resource Analysis signals
    (
        ("no budget", "senza budget", "limited", "limitato", "limitati",
         "can't afford", "non posso permetter", "without adding",
         "senza aggiungere", "scarce", "scarso", "scarsi", "few people",
         "poche persone", "pochi soldi", "gratis", "free", "sotto budget"),
        "Resource Analysis",
        2, "resource/scarcity constraint mentioned"
    ),
    # -- Ideality / IFR signals
    (
        ("ideal", "ideale", "leapfrog", "superare", "rethink", "ripensare",
         "from scratch", "da zero", "best possible", "migliore possibile",
         "perfetto", "perfect", "senza costo", "senza attrito"),
        "Ideality / IFR",
        2, "ideal-state / reimagine language"
    ),
    # -- Function Analysis signals
    (
        ("unclear", "poco chiaro", "complex system", "sistema complesso",
         "many parts", "molte parti", "interactions", "interazioni",
         "how it works", "come funziona", "confuso", "intricato"),
        "Function Analysis",
        1, "system-clarity / understanding gap"
    ),
    # -- System Operator signals
    (
        ("future", "futuro", "evolve", "evolvere", "long term", "lungo termine",
         "context", "contesto", "bigger picture", "visione d'insieme",
         "nel tempo", "prospettiva", "scala"),
        "System Operator (9 Windows)",
        1, "time-scale / context / evolution language"
    ),
    # -- Smart Little People signals
    (
        ("stuck", "bloccato", "bloccata", "no idea", "nessuna idea",
         "creative block", "blocco creativo", "non so come", "impasse"),
        "Smart Little People",
        1, "stuck / creative-block signal"
    ),
    # -- FOS (Function-Oriented Search) signals
    (
        ("someone must have solved", "how do others", "is there a field that",
         "how do they", "has anyone solved", "cross-industry", "cross industry",
         "other industries", "another field", "chi ha risolto", "come fanno",
         "qualcuno ha già"),
        "Function-Oriented Search (FOS)",
        3, "cross-industry solution search cue"
    ),
    # -- MOS (Method-Oriented Search) signals
    (
        ("we have a technology", "where can we apply", "find problems for",
         "new application", "apply this to", "abbiamo una tecnologia",
         "dove possiamo applicare"),
        "Method-Oriented Search (MOS)",
        3, "technology-to-problem matching cue"
    ),
    # -- Business TRIZ signals
    (
        ("pricing", "prezzo", "prezzi", "customer", "cliente", "clienti",
         "market", "mercato", "revenue", "ricavi", "fatturato", "team",
         "process", "processo", "org", "workflow", "flusso", "business",
         "vendite", "marketing", "concorrenza",
         "vendita", "costo", "margine", "utenti", "fidelizzazione"),
        "Business TRIZ",
        2, "business / org / market domain keyword"
    ),
    # -- Software TRIZ signals
    (
        ("app", "code", "codice", "latency", "latenza", "api", "database",
         "deploy", "architecture", "architettura", "bug", "notification",
         "notifica", "notifiche", "server", "frontend", "backend", "software",
         "programma", "algoritmo", "ui", "ux", "interfaccia",
         "sito", "web", "pagina", "login", "accesso", "caricamento", "dati",
         "errore", "connessione"),
        "Software TRIZ",
        2, "software / architecture domain keyword"
    ),
    # -- Rehabilitation TRIZ signals
    (
        ("patient", "paziente", "pazienti", "exercise", "esercizio", "esercizi",
         "therapy", "terapia", "rehab", "riabilitazione", "adherence",
         "aderenza", "aderire", "clinic", "clinica", "physio", "fisioterapia",
         "fisioterapista", "infortunio", "recupero", "cura", "trattamento",
         "dolore", "movimento", "muscolo", "ginocchio", "schiena",
         "allenamento", "protocollo"),
        "Rehabilitation TRIZ",
        2, "rehabilitation / physio / clinical domain keyword"
    ),
    # -- Workflow/Task signals (Italian)
    (
        ("attività", "task", "compito", "passaggio", "ritardo", "attesa"),
        "Business TRIZ",
        1, "workflow/task cue"
    ),
    # -- Su-Field + 76 Standard Solutions signals
    (
        ("interaction", "interferes", "doesn't act on", "damages", "harmful",
         "weak effect", "too strong", "contact", "interagisce", "danneggia",
         "does not act", "doesn't affect", "does not affect", "barely acts",
         "agisce a malapena"),
        "Su-Field + 76 Standard Solutions",
        4, "interaction / Su-Field cue (harmful, weak, or missing interaction)"
    ),
    # -- Evolution Trends + S-curve signals
    (
        ("leapfrog", "next generation", "where is this going", "mature",
         "plateau", "diminishing returns", "reinvent", "obsolete", "evolve",
         "reinvent the category", "next-gen", "next gen", "saturated",
         "s-curve", "s curve", "lifecycle", "life cycle"),
        "Evolution Trends + S-curve",
        4, "evolution / maturity / leapfrog cue"
    ),
    # -- Scientific Effects signals
    (
        ("how do i", "mechanism", "without a", "is there a way to",
         "achieve", "what effect", "how to achieve", "is there a way",
         "is there an effect", "physical effect", "chemical effect"),
        "Scientific Effects",
        3, "function-first / mechanism-search cue"
    ),
    # -- ARIZ signals
    (
        ("still stuck", "tried everything", "hard problem",
         "nothing works", "very hard contradiction", "deep dive",
         "tried all", "can't solve", "cannot solve", "impossible to solve",
         "dead end", "vicolo cieco", "irrisolvibile"),
        "ARIZ (escalation)",
        5, "stuck / hard-contradiction / escalation cue"
    ),
]

# ── Contradiction detection cues (separate from method scoring) ─────────────
# Italian + English contradiction connectors (bare whole words — matched with \\b)
_CONTRADICTION_CONNECTORS = [
    "but", "however", "trade-off", "tradeoff", "although",
    "ma", "però", "tuttavia", "eppure", "sebbene", "benché",
]

# Physical-contradiction topic words (presence/absence, opposing states)
_PHYSICAL_TOPICS = [
    ("present", "absent"), ("presente", "assente"),
    ("fast", "slow"), ("veloce", "lento"), ("veloce", "lenta"),
    ("big", "small"), ("grande", "piccolo"), ("grande", "piccola"),
    ("on", "off"), ("acceso", "spento"), ("accesa", "spenta"),
    ("hot", "cold"), ("caldo", "freddo"), ("calda", "fredda"),
    ("light", "heavy"), ("leggero", "pesante"), ("leggera", "pesante"),
    ("strong", "weak"), ("forte", "debole"),
    ("open", "closed"), ("aperto", "chiuso"), ("aperta", "chiusa"),
    ("loud", "quiet"), ("rumoroso", "silenzioso"),
    ("visible", "hidden"), ("visibile", "nascosto"), ("visibile", "nascosta"),
    ("rigid", "flexible"), ("rigido", "flessibile"), ("rigida", "flessibile"),
    ("transparent", "opaque"), ("trasparente", "opaco"), ("trasparente", "opaca"),
    ("thick", "thin"), ("spesso", "sottile"), ("spessa", "sottile"),
    ("dense", "sparse"), ("denso", "rado"), ("densa", "rada"),
    ("precise", "imprecise"), ("preciso", "impreciso"), ("precisa", "imprecisa"),
    ("cheap", "expensive"), ("economico", "costoso"), ("economica", "costosa"),
]

_ANNOYANCE_WORDS = [
    "annoy", "annoying", "irritating", "frustrating", "bothersome",
    "fastidios", "fastidiosa", "fastidioso", "irritante", "seccante",
    "noioso", "noiosa", "invasivo", "invasiva", "molesto", "molesta",
]

_DEFAULT_FALLBACK = [
    {"method": "Function Analysis", "score": 0, "why": "default fallback — no specific cues matched"},
    {"method": "Root Cause Analysis", "score": 0, "why": "default fallback — no specific cues matched"},
    {"method": "Engineering Contradiction + 40 Inventive Principles", "score": 0, "why": "default fallback — no specific cues matched"},
    {"method": "Resource Analysis", "score": 0, "why": "default fallback — no specific cues matched"},
    {"method": "Ideality / IFR", "score": 0, "why": "default fallback — no specific cues matched"},
]


def _detect_engineering_contradiction(lower: str, problem: str) -> str | None:
    """Try to produce a one-line 'improve X / worsens Y' guess using word boundaries."""
    # Find connectors with word-boundary matching
    connector_pos = -1
    found_conn = ""
    for c in _CONTRADICTION_CONNECTORS:
        m = re.search(rf"\b{re.escape(c)}\b", lower)
        if m:
            pos = m.start()
            if connector_pos == -1 or pos < connector_pos:
                connector_pos = pos
                found_conn = c

    if connector_pos == -1:
        return None

    # Extract text before and after the connector
    before_raw = problem[:connector_pos].strip().rstrip(".,;:!?")
    after_raw = problem[connector_pos + len(found_conn):].strip().lstrip(".,;:!? ")

    # Extract nearest noun-phrase subject: last 2-3 whole words before, first 2-3 after
    def _subject_words(text: str, count: int, from_end: bool = True) -> str:
        words = text.split()
        if not words:
            return ""
        if from_end:
            selected = words[-min(count, len(words)):]
        else:
            selected = words[:min(count, len(words))]
        return " ".join(selected)

    before_subject = _subject_words(before_raw, 3, from_end=True)
    after_subject = _subject_words(after_raw, 3, from_end=False)

    # Truncate each to 40 chars, never split mid-word
    if len(before_subject) > 40:
        before_subject = before_subject[:40].rstrip().rsplit(" ", 1)[0]
    if len(after_subject) > 40:
        after_subject = after_subject[:40].rstrip().rsplit(" ", 1)[0]

    if before_subject and after_subject:
        return f"improve [{before_subject}] / worsens [{after_subject}]"

    # Fallback: no valid pre-connector subject — do NOT emit improve/worsens framing
    short_text = problem[:80].rstrip()
    if len(short_text) > 60:
        short_text = short_text[:60].rstrip().rsplit(" ", 1)[0]
    return f"trade-off near: {short_text}"


def _detect_physical_contradiction(lower: str) -> str | None:
    """Try to produce a one-line 'must be A and not-A' guess."""
    # Check explicit paired opposites with word boundaries
    for a, b in _PHYSICAL_TOPICS:
        if _kw_match(a, lower) and _kw_match(b, lower):
            return f"element must be both {a} and {b}"

    # Check annoyance/presence patterns — common in notification/adherence problems
    has_annoyance = any(_kw_match(w, lower) for w in _ANNOYANCE_WORDS)
    has_but = any(_kw_match(c, lower) for c in _CONTRADICTION_CONNECTORS)

    if has_but and has_annoyance:
        # Look for the subject that's annoying / must be both present and absent
        for subject in ["notification", "notifica", "notifiche", "message",
                        "messaggio", "reminder", "promemoria", "alert", "avviso",
                        "allarme", "email", "popup", "suono", "sound"]:
            if subject in lower:
                return f"'{subject}' must be present (to help) and absent (to avoid annoyance)"
        return "element must be present (useful) and absent (avoids annoyance)"

    # Check must-be / deve-essere patterns (no has_but gate — R3)
    for must_word in ["must be", "deve essere", "devono essere", "should be",
                      "dovrebbe", "dovrebbero"]:
        if must_word in lower:
            return f"physical contradiction suspected near '{must_word}'"

    return None


def suggest_methods(problem: str) -> dict[str, Any]:
    """Suggest TRIZ methods for a problem description.

    Args:
        problem: Free-text problem description (any language, English + Italian
                 well supported).

    Returns:
        dict with keys:
        - "engineering_contradiction": str or None
        - "physical_contradiction": str or None
        - "methods": list of {"method", "score", "why"}, sorted score desc
    """
    lower = problem.lower()
    scored: dict[str, tuple[int, list[str]]] = {}

    for keywords, method, weight, why_tpl in RULES:
        for kw in keywords:
            if _kw_match(kw, lower):
                prev = scored.get(method)
                if prev is None:
                    scored[method] = (weight, [why_tpl])
                else:
                    total, reasons = prev
                    # Accumulate weight but cap per-method at 10
                    new_total = min(total + weight, 10)
                    if why_tpl not in reasons:
                        reasons.append(why_tpl)
                    scored[method] = (new_total, reasons)

    eng_cont = _detect_engineering_contradiction(lower, problem)
    phys_cont = _detect_physical_contradiction(lower)

    # Boost Physical Contradiction score when a physical contradiction is detected
    if phys_cont is not None:
        method_key = "Physical Contradiction + Separation"
        prev = scored.get(method_key)
        if prev is None:
            scored[method_key] = (4, ["physical contradiction explicitly detected"])
        else:
            total, reasons = prev
            reasons.append("physical contradiction explicitly detected")
            scored[method_key] = (min(total + 2, 10), reasons)

    # Boost Engineering Contradiction score when detected
    if eng_cont is not None:
        method_key = "Engineering Contradiction + 40 Inventive Principles"
        prev = scored.get(method_key)
        if prev is None:
            scored[method_key] = (3, ["engineering contradiction explicitly detected"])
        else:
            total, reasons = prev
            if "engineering contradiction explicitly detected" not in reasons:
                reasons.append("engineering contradiction explicitly detected")
            scored[method_key] = (min(total + 1, 10), reasons)

    # If we have a physical contradiction, also suggest Resource Analysis,
    # Ideality, and System Operator (decision table + spec coverage)
    if phys_cont is not None:
        for booster in ["Resource Analysis", "Ideality / IFR",
                        "System Operator (9 Windows)"]:
            if booster not in scored:
                scored[booster] = (1, ["suggested companion to Physical Contradiction"])

    # Build methods list
    if scored:
        methods = [
            {"method": m, "score": sc, "why": "; ".join(rs)}
            for m, (sc, rs) in scored.items()
        ]
        methods.sort(key=lambda x: x["score"], reverse=True)
    else:
        methods = list(_DEFAULT_FALLBACK)

    return {
        "engineering_contradiction": eng_cont,
        "physical_contradiction": phys_cont,
        "methods": methods,
    }


def _print_result(result: dict[str, Any]) -> None:
    """Pretty-print the router result to stdout."""
    if result["engineering_contradiction"]:
        print(f"Engineering Contradiction: {result['engineering_contradiction']}")
    else:
        print("Engineering Contradiction: (none detected)")

    if result["physical_contradiction"]:
        print(f"Physical Contradiction:   {result['physical_contradiction']}")
    else:
        print("Physical Contradiction:   (none detected)")

    print()
    print(f"{'Method':<55} {'Score':>5}")
    print("-" * 62)
    for m in result["methods"]:
        print(f"{m['method']:<55} {m['score']:>5}")
    print()
    print("Reasons:")
    for m in result["methods"]:
        if m["why"]:
            print(f"  [{m['method']}] {m['why']}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python triz_router.py \"problem description text\"")
        print()
        print("Heuristic TRIZ method router. Analyzes the problem text and suggests")
        print("which TRIZ methods to apply, ranked by relevance score.")
        print()
        print("Supports English and Italian problem descriptions.")
        sys.exit(0)

    problem = " ".join(sys.argv[1:])
    result = suggest_methods(problem)
    _print_result(result)


if __name__ == "__main__":
    main()
