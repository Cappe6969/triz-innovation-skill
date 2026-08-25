#!/usr/bin/env python3
"""
TRIZ method router — heuristic suggestions from problem text.
Matches keyword/intent cues from references/triz-method-map.md and
returns ranked methods plus contradiction guesses.

Usage:
    python triz_router.py "problem description text"
    python triz_router.py [--lang en|it|auto] [--branch <id>] "problem description text"
    python triz_router.py --list          # list available --branch/--lang values
    python triz_router.py                  # prints usage

--lang:  en (default, English labels), it (Italian labels), auto (detect the
         language of the problem text and use the matching overlay).
--branch: restrict the domain rules to a single field branch: general (all
         domain rules run), or any registered field branch id (only that
         domain's rules run).

Standard library only — Python 3.9+.
"""

from __future__ import annotations

import sys
import re
from typing import Any

from triz_branches import detect_language, get_field_branch, get_lang_branch, list_branches


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
    # -- Mechanical TRIZ signals
    (
        ("torque", "coppia", "vibration", "vibrazione", "vibrazioni", "fatigue", "fatica", "stress", "tolerance", "tolleranza", "wear", "usura", "friction", "attrito", "gear", "ingranaggio", "bearing", "cuscinetto", "stiffness", "rigidità", "deflection", "deformazione", "crack", "cricca", "corrosion", "corrosione", "shaft", "albero", "weld", "saldatura", "thermal", "termico", "heat", "calore", "machining", "lavorazione", "spindle", "mandrino", "clearance", "gioco", "seal", "tenuta", "spring", "molla", "piston", "pistone", "hydraulic", "idraulico", "pneumatic", "pneumatico", "clutch", "frizione", "brake", "freno", "motor", "motore", "gearbox", "cambio", "bolt", "vite", "fastener", "bullone"),
        "Mechanical TRIZ",
        2, "mechanical / hardware domain keyword"
    ),
    # -- Data Science TRIZ signals
    (
        ("model", "modello", "training", "addestramento", "dataset", "feature", "caratteristica", "accuracy", "accuratezza", "precision", "precisione", "recall", "overfitting", "underfitting", "bias", "distorsione", "gradient", "gradiente", "inference", "inferenza", "prediction", "previsione", "machine learning", "deep learning", "neural", "rete neurale", "embedding", "hyperparameter", "iperparametro", "loss", "metrica", "metric", "cluster", "clustering", "classification", "classificazione", "regression", "regressione", "anomaly", "anomalia", "outlier", "drift", "validation", "validazione", "gpu", "batch", "epoch", "epoca", "weights", "pesi", "tuning", "ottimizzazione", "prompt", "llm", "transformer", "token"),
        "Data Science TRIZ",
        2, "data science / ML / AI domain keyword"
    ),
    # -- Marketing TRIZ signals
    (
        ("conversion", "conversione", "funnel", "imbuto", "campaign", "campagna", "churn", "abbandono", "retention", "fidelizzazione", "acquisition", "acquisizione", "engagement", "brand", "click", "cta", "lead", "landing page", "bounce", "rimbalzo", "audience", "pubblico", "segment", "segmento", "positioning", "posizionamento", "pricing", "prezzo", "a/b test", "persona", "market", "mercato", "growth", "crescita", "virality", "viralità", "reach", "copertura", "impression", "impressioni", "ctr", "roi", "content", "contenuto", "social", "influencer", "marketing", "advertising", "pubblicità", "onboarding", "activation", "attivazione", "upsell", "cross-sell"),
        "Marketing TRIZ",
        2, "marketing / growth domain keyword"
    ),
    # -- Supply Chain TRIZ signals
    (
        ("inventory", "scorte", "stock", "lead time", "tempi di consegna", "demand", "domanda", "forecast", "previsione", "logistics", "logistica", "warehouse", "magazzino", "supplier", "fornitore", "stockout", "esaurimento", "backorder", "capacity", "capacità", "throughput", "flusso", "replenishment", "riassortimento", "dispatch", "spedizione", "shipping", "trasporto", "freight", "cargo", "routing", "percorso", "bullwhip", "effetto frusta", "safety stock", "scorta di sicurezza", "order", "ordine", "lot", "lotto", "picking", "stoccaggio", "pallet", "container", "customs", "dogana", "distribution", "distribuzione", "supply chain", "catena di approvvigionamento", "sourcing", "approvvigionamento", "procurement", "acquisti", "fulfillment", "evasione ordini", "delivery", "consegna", "transportation", "trasporti"),
        "Supply Chain TRIZ",
        2, "supply chain / logistics domain keyword"
    ),
    # -- Energy / Power TRIZ signals
    (
        ("power grid", "rete elettrica", "smart grid", "rete intelligente",
         "inverter", "battery", "batteria", "batterie", "solar", "solare",
         "photovoltaic", "fotovoltaico", "turbine", "turbina", "wind farm",
         "parco eolico", "energy efficiency", "efficienza energetica",
         "heat loss", "dispersione termica", "power transmission",
         "trasmissione di energia", "outage", "interruzione", "blackout",
         "load balancing", "bilanciamento del carico", "peak load",
         "picco di carico", "charging", "ricarica", "substation",
         "sottostazione", "generator", "generatore", "voltage", "tensione",
         "renewable", "rinnovabile", "energy storage", "accumulo di energia",
         "storage capacity", "capacità di accumulo", "power plant",
         "centrale elettrica", "cogeneration", "cogenerazione",
         "power factor", "fattore di potenza"),
        "Energy TRIZ",
        2, "energy / power domain keyword"
    ),
    # -- Education / Learning TRIZ signals
    (
        ("student", "students", "studente", "studenti", "teacher",
         "insegnante", "school", "scuola", "university", "università",
         "curriculum", "assessment", "valutazione", "lesson", "lezione",
         "homework", "compiti", "grading", "voto", "voti", "pedagogy",
         "pedagogia", "tutoring", "tutoraggio", "exam", "esame", "syllabus",
         "distraction", "distrazione", "motivation", "motivazione",
         "attention span", "capacità di attenzione", "e-learning", "lms",
         "dropout", "abbandono scolastico", "knowledge retention", "ritenzione",
         "learning outcomes", "risultati di apprendimento", "classroom", "aula",
         "study habits", "abitudini di studio", "vocational training",
         "formazione professionale", "didactic", "didattica"),
        "Education TRIZ",
        2, "education / learning domain keyword"
    ),
    # -- Construction / Civil TRIZ signals
    (
        ("concrete", "calcestruzzo", "cement", "cemento", "steel", "acciaio",
         "beam", "trave", "foundation", "fondazione", "crane", "gru",
         "scaffolding", "ponteggio", "excavation", "scavo", "structural",
         "strutturale", "load-bearing", "portante", "rebar", "armatura",
         "prefabrication", "prefabbricazione", "construction site", "cantiere",
         "contractor", "appaltatore", "waterproofing", "impermeabilizzazione",
         "insulation", "isolamento", "facade", "facciata", "settlement",
         "assestamento", "curing", "stagionatura", "formwork", "cassero",
         "erection", "montaggio", "demolition", "demolizione", "seismic",
         "sismico", "shoring", "puntellamento", "construction", "edilizia",
         "building", "edificio", "bridge", "tunnel", "galleria"),
        "Construction TRIZ",
        2, "construction / civil engineering domain keyword"
    ),
    # -- Robotics / IoT / Embedded TRIZ signals
    (
        ("actuator", "attuatore", "sensor", "sensors", "sensore", "sensori",
         "autonomy", "autonomous", "autonomia", "firmware", "gripper", "pinza",
         "calibration", "calibrazione", "telemetry", "telemetria",
         "motion control", "controllo del movimento", "embedded", "ros",
         "edge device", "dispositivo edge", "servo", "kinematics", "cinematica",
         "path planning", "pianificazione del percorso", "obstacle", "ostacolo",
         "lidar", "imu", "end effector", "effettore finale", "robot arm",
         "braccio robotico", "odometry", "odometria", "closed loop",
         "anello chiuso", "sensor fusion", "fusione sensoriale", "localization",
         "localizzazione", "microcontroller", "microcontrollore", "robot",
         "drone", "oscillation", "oscillazione", "motor controller",
         "controllore motore", "encoder"),
        "Robotics TRIZ",
        2, "robotics / IoT / embedded domain keyword"
    ),
]

# Domain tag for each field branch: branch id -> set of domain-rule method
# names. The router uses this to skip the other domains' rules when a --branch
# is set. Built from the branch registry (each branch.json declares its
# "method") so a dropped-in branch.json is picked up automatically, matching
# the registry's own data-driven acceptance in the dispatcher.
def _load_domain_rules() -> dict[str, set[str]]:
    rules: dict[str, set[str]] = {}
    for fid in list_branches()["fields"]:
        if fid == "general":
            continue
        try:
            method = get_field_branch(fid).get("method")
        except KeyError:
            continue  # branch dir present but branch.json missing — `branches check` flags it
        if method:
            rules[fid] = {method}
    return rules


_DOMAIN_RULES = _load_domain_rules()


def _branch_keyword_rules() -> list[tuple[tuple[str, ...], str, int, str]]:
    """Extra keyword rules from each branch.json's own vocabulary.

    The static RULES table already covers most domain keywords; a branch
    keyword is added here only when it is NOT already matched for that
    branch's method, so the branch.json data stays live without double-
    counting. Both sources feed the same method, so a --branch filter treats
    them identically."""
    extra: list[tuple[tuple[str, ...], str, int, str]] = []
    for fid, methods in _DOMAIN_RULES.items():
        method = next(iter(methods))
        already = {
            kw for kw_tuple, m, _w, _why in RULES if m == method
            for kw in kw_tuple
        }
        try:
            keywords = tuple(
                kw for kw in (get_field_branch(fid).get("keywords") or [])
                if isinstance(kw, str) and kw and kw not in already
            )
        except KeyError:
            continue
        if keywords:
            extra.append(
                (keywords, method, 2, f"{fid} branch vocabulary (branch.json)")
            )
    return extra


RULES = RULES + _branch_keyword_rules()


def _valid_branches() -> tuple[str, ...]:
    """Accepted --branch ids: 'general' plus every registered field branch that
    declares a domain method."""
    return ("general", *_DOMAIN_RULES)

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


def suggest_methods(problem: str, branch: str = "general") -> dict[str, Any]:
    """Suggest TRIZ methods for a problem description.

    Args:
        problem: Free-text problem description (any language, English + Italian
                 well supported).
        branch: Field branch filter: "general" (all domain rules run), or any
                registered field branch id such as "mechanical" or
                "datascience" (only that domain's rules run). Method keys
                returned are always English.

    Returns:
        dict with keys:
        - "engineering_contradiction": str or None
        - "physical_contradiction": str or None
        - "methods": list of {"method", "score", "why"}, sorted score desc

    Raises:
        ValueError: for an unknown branch id.
    """
    if branch != "general" and branch not in _DOMAIN_RULES:
        raise ValueError(f"Unknown branch: {branch!r}")

    # When a field branch is set, skip the domain rules of every other field.
    domain_skip: set[str] = set()
    if branch != "general":
        for domain, methods in _DOMAIN_RULES.items():
            if domain != branch:
                domain_skip |= methods

    lower = problem.lower()
    scored: dict[str, tuple[int, list[str]]] = {}

    for keywords, method, weight, why_tpl in RULES:
        if method in domain_skip:
            continue
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


def _print_result(result: dict[str, Any], lang: str = "en") -> None:
    """Pretty-print the router result to stdout.

    Method keys stay English; the labels of the two contradiction lines and of
    every method name are localized when lang is "it".
    """
    labels: dict[str, str] = {}
    contradiction_labels: dict[str, str] = {}
    if lang == "it":
        it = get_lang_branch("it")
        labels = it.get("labels", {})
        contradiction_labels = it.get("contradiction_labels", {})

    eng_head = contradiction_labels.get("engineering", "Engineering Contradiction:")
    phys_head = contradiction_labels.get("physical", "Physical Contradiction:")

    if result["engineering_contradiction"]:
        print(f"{eng_head} {result['engineering_contradiction']}")
    else:
        print(f"{eng_head} (none detected)")

    if result["physical_contradiction"]:
        print(f"{phys_head} {result['physical_contradiction']}")
    else:
        print(f"{phys_head} (none detected)")

    print()
    print(f"{'Method':<55} {'Score':>5}")
    print("-" * 62)
    for m in result["methods"]:
        name = labels.get(m["method"], m["method"]) if lang == "it" else m["method"]
        print(f"{name:<55} {m['score']:>5}")
    print()
    print("Reasons:")
    for m in result["methods"]:
        if m["why"]:
            name = labels.get(m["method"], m["method"]) if lang == "it" else m["method"]
            print(f"  [{name}] {m['why']}")


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    args = sys.argv[1:]
    lang = "en"
    branch = "general"
    show_list = False
    positional: list[str] = []

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--list":
            show_list = True
            i += 1
        elif arg == "--lang" or arg.startswith("--lang="):
            if "=" in arg:
                value = arg.split("=", 1)[1]
            else:
                if i + 1 >= len(args):
                    print("Error: --lang requires a value (en, it or auto).", file=sys.stderr)
                    sys.exit(1)
                value = args[i + 1]
                i += 1
            if value not in ("en", "it", "auto"):
                print(f"Error: unknown --lang value {value!r} (expected en, it or auto).", file=sys.stderr)
                sys.exit(1)
            lang = value
        elif arg == "--branch" or arg.startswith("--branch="):
            if "=" in arg:
                value = arg.split("=", 1)[1]
            else:
                if i + 1 >= len(args):
                    print(
                        f"Error: --branch requires a value ({', '.join(_valid_branches())}).",
                        file=sys.stderr,
                    )
                    sys.exit(1)
                value = args[i + 1]
                i += 1
            if value not in _valid_branches():
                print(
                    f"Error: unknown --branch value {value!r} "
                    f"(expected {', '.join(_valid_branches())}).",
                    file=sys.stderr,
                )
                sys.exit(1)
            branch = value
        else:
            positional.append(arg)
        i += 1

    if show_list:
        print("--branch ids: " + ", ".join(_valid_branches()))
        print("--lang values: en, it, auto")
        sys.exit(0)

    if not positional:
        # House CLI convention: missing required input -> Usage on stderr, rc 1.
        print(f"Usage: python triz_router.py [--lang en|it|auto] [--branch {'|'.join(_valid_branches())}] \"problem description text\"", file=sys.stderr)
        print(file=sys.stderr)
        print("Heuristic TRIZ method router. Analyzes the problem text and suggests", file=sys.stderr)
        print("which TRIZ methods to apply, ranked by relevance score.", file=sys.stderr)
        print(file=sys.stderr)
        print("Supports English and Italian problem descriptions.", file=sys.stderr)
        sys.exit(1)

    problem = " ".join(positional)
    if lang == "auto":
        lang = detect_language(problem)
    result = suggest_methods(problem, branch=branch)
    _print_result(result, lang=lang)


if __name__ == "__main__":
    main()
