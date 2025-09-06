from __future__ import annotations
from typing import Dict, List, Tuple

###############################################################################
# 1.  CROSSWORD DATA
###############################################################################

CROSSWORD_CLUES_A: List[Dict[str, str | int]] = [
    {"direction": "A", "number": 2, "hint": "Country famous for Mozart and the Alps", "answer": "AUSTRIA"},
    {"direction": "A", "number": 5, "hint": "Country whose canal connects the Atlantic and Pacific oceans", "answer": "PANAMA"},
    {"direction": "A", "number": 6, "hint": "Island whose capital is Taipei", "answer": "TAIWAN"},
    {"direction": "A", "number": 9, "hint": "Eastern land known for a monumental divide", "answer": "CHINA"},
    {"direction": "A", "number": 11, "hint": "Where Plato and Socrates once strolled", "answer": "GREECE"},
    {"direction": "A", "number": 12, "hint": "Smallest country in the world, home to St. Peter’s Basilica", "answer": "VATICANCITY"},
    {"direction": "A", "number": 16, "hint": "Country that stretches from Europe to Asia", "answer": "RUSSIA"},
    {"direction": "A", "number": 18, "hint": "South American country named like a pepper, with Santiago as its capital", "answer": "CHILE"},
    {"direction": "A", "number": 21, "hint": "Caribbean country hit by a major earthquake in 2010", "answer": "HAITI"},
    {"direction": "A", "number": 22, "hint": "Home of Usain Bolt and reggae music", "answer": "JAMAICA"},
    {"direction": "D", "number": 1, "hint": "Country whose motto is Liberté, Égalité, Fraternité", "answer": "FRANCE"},
    {"direction": "D", "number": 3, "hint": "European country whose capital is Madrid, famous for paella", "answer": "SPAIN"},
    {"direction": "D", "number": 4, "hint": "Country whose capital is Kuala Lumpur", "answer": "MALAYSIA"},
    {"direction": "D", "number": 7, "hint": "Country whose capital is Tehran and was once called Persia", "answer": "IRAN"},
    {"direction": "D", "number": 8, "hint": "East African country whose capital is Nairobi", "answer": "KENYA"},
    {"direction": "D", "number": 10, "hint": "Country whose capital is Baghdad, located between the Tigris and Euphrates", "answer": "IRAQ"},
    {"direction": "D", "number": 13, "hint": "Country north of the United States known for maple syrup", "answer": "CANADA"},
    {"direction": "D", "number": 14, "hint": "Central European country whose capital is Prague, formerly part of Czechoslovakia", "answer": "CZECHIA"},
    {"direction": "D", "number": 15, "hint": "Middle Eastern country founded in 1948, capital Jerusalem", "answer": "ISRAEL"},
    {"direction": "D", "number": 17, "hint": "Country whose ancient city of Damascus is one of the oldest continually inhabited", "answer": "SYRIA"},
    {"direction": "D", "number": 19, "hint": "European country shaped like a boot, capital Rome", "answer": "ITALY"},
    {"direction": "D", "number": 20, "hint": "African country whose ancient monuments include the Pyramids of Giza", "answer": "EGYPT"},
]

CROSSWORD_CLUES_B: List[Dict[str, str | int]] = [
    {'direction': 'A','number': 1,'hint':' Country famous for cigars and classic cars, capital Havana','answer':'CUBA'},
    {'direction': 'A','number': 4,'hint':' Largest nation in South America, home to the Amazon rainforest','answer':'BRAZIL'},
    {'direction': 'A','number': 6,'hint':' EU’s least-populated member, where Popeye’s 1980 movie set still stands','answer':'MALTA'},
    {'direction': 'A','number': 7,'hint':' Gulf state whose capital is Doha and host of the 2022 World Cup','answer':'QATAR'},
    {'direction': 'A','number':10,'hint':'African country that gave the famous Dakar Rally its original finish line','answer':'SENEGAL'},
    {'direction': 'A','number':11,'hint':'Horn-of-Africa nation, capital Mogadishu, in news for modern-day piracy','answer':'SOMALIA'},
    {'direction': 'A','number':15,'hint':'Central-European country whose capital Budapest spans the Danube','answer':'HUNGARY'},
    {'direction': 'A','number':17,'hint':'Andean nation home to Machu Picchu','answer':'PERU'},
    {'direction': 'A','number':19,'hint':'Scandinavian country known for ABBA and flat-pack furniture','answer':'SWEDEN'},
    {'direction': 'A','number':20,'hint':'One of only two land-locked countries in South America, capital Asunción','answer':'PARAGUAY'},
    {'direction': 'D','number': 1,'hint':' Country between Thailand and Vietnam with Angkor Wat and capital Phnom Penh','answer':'CAMBODIA'},
    {'direction': 'D','number': 2,'hint':' European nation famed for chocolate, waffles, and EU headquarters','answer':'BELGIUM'},
    {'direction': 'D','number': 3,'hint':' Eastern-European nation with a blue-and-yellow flag and capital Kyiv','answer':'UKRAINE'},
    {'direction': 'D','number': 4,'hint':' Island nation just southeast of Florida, capital Nassau','answer':'BAHAMAS'},
    {'direction': 'D','number': 5,'hint':' Island country nicknamed the “Land of the Rising Sun,” capital Tokyo','answer':'JAPAN'},
    {'direction': 'D','number': 8,'hint':' European nation of Oktoberfest and the Autobahn, capital Berlin','answer':'GERMANY'},
    {'direction': 'D','number': 9,'hint':' Balkan nation whose capital is Belgrade and home to Novak Djokovic','answer':'SERBIA'},
    {'direction': 'D','number':12,'hint':'Arabian sultanate that might make you exclaim “Oh, man!”','answer':'OMAN'},
    {'direction': 'D','number':13,'hint':'Southeast-Asian country whose capital is Hanoi, known for pho','answer':'VIETNAM'},
    {'direction': 'D','number':14,'hint':'Country many visitors choose for low-cost hair transplants','answer':'TURKEY'},
    {'direction': 'D','number':16,'hint':'Nordic land of fjords and the midnight sun, capital Oslo','answer':'NORWAY'},
    {'direction': 'D','number':18,'hint':'East-African country famous for safaris and capital Nairobi','answer':'KENYA'}
]


_CLUE_LOOKUP: Dict[Tuple[str, int], Dict[str, str | int]] = {
    (c["direction"][0].upper(), c["number"]): c for c in CROSSWORD_CLUES_A
}

###############################################################################
# 2.  HELPERS
###############################################################################

def _letters_filled(p: str) -> int:
    return sum(ch != "0" for ch in p)

def _pretty(p: str) -> str:
    return "".join("_" if ch == "0" else ch for ch in p)

def _find_errors(state: dict) -> List[str]:
    msgs: List[str] = []
    for kdir in ("across", "down"):
        for num_str, pat in state[kdir].items():
            if num_str == "undefined" or not pat:
                continue
            num = int(num_str)
            clue = _CLUE_LOOKUP[(kdir[0].upper(), num)]
            ans: str = clue["answer"]  # type: ignore
            # corrected: use pat.ljust, not p.ljust
            if any(ch != "0" and ch != a for ch, a in zip(pat.ljust(len(ans), "0"), ans)):
                msgs.append(
                    f"• ({kdir[0].upper()}{num}) {clue['hint']} – typed “{_pretty(pat)}” doesn’t fit. (internal: {ans})"
                )
    return msgs

def _choose_focal(state: dict) -> Tuple[str, int]:
    ctx = state.get("clue_context", {})
    if ctx.get("clueLabel") is not None:
        return ctx["direction"][0].upper(), int(ctx["clueLabel"])
    for kdir in ("across", "down"):
        for num_str, pat in state[kdir].items():
            if num_str != "undefined" and "0" in pat:
                return kdir[0].upper(), int(num_str)
    first = CROSSWORD_CLUES_A[0]
    return first["direction"][0].upper(), first["number"]

def _interesting(state: dict, excl: Tuple[str, int], k: int = 2) -> List[str]:
    items: list[tuple[int, str, int, str, str]] = []
    for kdir in ("across", "down"):
        for num_str, pat in state[kdir].items():
            if num_str == "undefined":
                continue
            num = int(num_str)
            if (kdir[0].upper(), num) == excl or "0" not in pat:
                continue
            clue = _CLUE_LOOKUP[(kdir[0].upper(), num)]
            items.append((-_letters_filled(pat), kdir[0].upper(), num, pat, clue["answer"]))  # type: ignore
    items.sort()
    return [f"• ({d}{n}) “{_pretty(pat)}” (int:{ans})" for _, d, n, pat, ans in items[:k]]

def _snapshot(state: dict, excl: set[Tuple[str, int]]) -> str:
    rows: List[str] = []
    for kdir in ("across", "down"):
        cells: List[str] = []
        for num_str, pat in state[kdir].items():
            if num_str == "undefined":
                continue
            num = int(num_str)
            if (kdir[0].upper(), num) in excl or "0" not in pat:
                continue
            cells.append(f"{num}:{_pretty(pat)}")
        if cells:
            rows.append(f"{kdir[0].upper()}: " + ", ".join(cells))
    return " | ".join(rows) if rows else "(all filled!)"

###############################################################################
# 3.  STATIC BLOCKS (unchanged from 2.0)
###############################################################################

_HEADER = (
    "### ROLE"
    "You are a friendly robot sitting beside the user, helping solve a **country-themed crossword**."
    "Speak in *first person* (“I”). Offer encouragement, clever hints, or ligh conversation"
    "chit-chat about geography or the puzzle itself — but **never** reveal a full answer."
    "Your replies will be spoken aloud; keep them natural and concise, like a human assistant."
)

_GUIDE = (
    "### RESPONSE GUIDELINES"
    "Reply with **one or two upbeat sentences** since you’ll be spoken aloud."
    "1. If the user has an error (and you haven’t mentioned it yet), politely tell it to the user."
    "2. If they just solved a word, celebrate briefly then consider a light geography/small-talk question."
    "3. Otherwise choose one:"
    "   • a subtle hint for the current clue (without asking permission)"
    "   • a nudge toward an interesting partly-filled clue"
    "   • or a brief geography/food/sports chit-chat (e.g., “Ever visited Chile?”)."
    "4. Do not recite the full clue; refer by number or a short nickname (e.g., “Bolt’s island”)."
    "5. Suggest switching clues only after sustained silence (> idle_threshold) or clear frustration."
    "6. Speak letters plainly: “middle letter is N”. Never show underscores in speech."
    "7. Only reveal the entire answer if the user explicitly requests full spelling; then spell slowly."
    "8. Its better to not state to many things in one reply, also not nescesary to immediately go to the next clue"
)

_EXAMPLES = (
    "### EXAMPLES"
    "**Error correction**"
    "ASSISTANT: You’ve made a mistake, grease is spelled incorrectly 😉"
    "**Celebration & pivot**"
    "(after the user finishes PANAMA)"
    "ASSISTANT: Nice work with Panama! Ever fancied visiting the canal?"
    "**Idle re-engagement**"
    "(20+ seconds silence)"
    "ASSISTANT: Quiet moment—need a hint on Austria, or shall we chat travel?"
)

###############################################################################
# 4.  ENTRY FUNCTION
###############################################################################

def create_system_prompt(
    game_state: dict,
    silence_seconds: int,
    idle_threshold: int = 20,
    recently_completed: List[Tuple[str, int]] | None = None,
    user_emotion: str = "neutral",
    prev_turn: Dict[str, str] | None = None
) -> str:
    parts: List[str] = [_HEADER, "\n### BOARD"]

    # mistakes
    errs = _find_errors(game_state)
    if errs:
        parts.append("Errors:\n" + "\n".join(errs))

    # recent solves
    if recently_completed:
        parts.append("Solved: " + ", ".join(f"{d}{n}" for d, n in recently_completed))

    # focal clue
    d, n = _choose_focal(game_state)
    clue = _CLUE_LOOKUP[(d, n)]
    print(f"[PROMPT] Focal clue: {d}{n} )")
    pattern = game_state["across" if d == "A" else "down"]
    parts.append(f"The user is currently focused at {d}{n}. Hint: {clue['hint']}. Pattern: {_pretty(pattern)}. (internal: {clue['answer']})")

    # interesting others
    picks = _interesting(game_state, (d, n))
    if picks:
        parts.append("\nTry next?\n" + "\n".join(picks))
    # snapshot internal
    
    parts.append("\nUnsolved snapshot (internal):\n" + _snapshot(game_state, {(d, n)}))

    if silence_seconds >= idle_threshold:
        parts.append("\n### IDLE\nUser has been quiet → offer help or small‑talk.")

    parts.append("\n" + _GUIDE)
    parts.append("\n" + _EXAMPLES)

    return "\n\n".join(parts)