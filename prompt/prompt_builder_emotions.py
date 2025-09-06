from __future__ import annotations
from typing import Dict, List, Tuple

###############################################################################
# 0.  CONSTANTS & EMOTION LABELS
###############################################################################

FER_2013_EMO_DICT: Dict[int, str] = {
    0: "angry",
    1: "disgust",
    2: "fear",
    3: "happy",
    4: "sad",
    5: "surprise",
    6: "neutral",
}

###############################################################################
# 1.  DATA ── the canonical crossword definition
###############################################################################

CROSSWORD_CLUES_A: List[Dict[str, str | int]] = [
    {"direction": "across", "number": 2, "hint": "Country famous for Mozart and the Alps", "answer": "AUSTRIA"},
    {"direction": "across", "number": 5, "hint": "Country whose canal connects the Atlantic and Pacific oceans", "answer": "PANAMA"},
    {"direction": "across", "number": 6, "hint": "Island whose capital is Taipei", "answer": "TAIWAN"},
    {"direction": "across", "number": 9, "hint": "Eastern land known for a monumental divide", "answer": "CHINA"},
    {"direction": "across", "number": 11, "hint": "Where Plato and Socrates once strolled", "answer": "GREECE"},
    {"direction": "across", "number": 12, "hint": "Smallest country in the world, home to St. Peter’s Basilica", "answer": "VATICANCITY"},
    {"direction": "across", "number": 16, "hint": "Country that stretches from Europe to Asia", "answer": "RUSSIA"},
    {"direction": "across", "number": 18, "hint": "South American country named like a pepper, with Santiago as its capital", "answer": "CHILE"},
    {"direction": "across", "number": 21, "hint": "Caribbean country hit by a major earthquake in 2010", "answer": "HAITI"},
    {"direction": "across", "number": 22, "hint": "Home of Usain Bolt and reggae music", "answer": "JAMAICA"},
    {"direction": "down", "number": 1, "hint": "Country whose motto is Liberté, Égalité, Fraternité", "answer": "FRANCE"},
    {"direction": "down", "number": 3, "hint": "European country whose capital is Madrid, famous for paella", "answer": "SPAIN"},
    {"direction": "down", "number": 4, "hint": "Country whose capital is Kuala Lumpur", "answer": "MALAYSIA"},
    {"direction": "down", "number": 7, "hint": "Country whose capital is Tehran and was once called Persia", "answer": "IRAN"},
    {"direction": "down", "number": 8, "hint": "East African country whose capital is Nairobi", "answer": "KENYA"},
    {"direction": "down", "number": 10, "hint": "Country whose capital is Baghdad, located between the Tigris and Euphrates", "answer": "IRAQ"},
    {"direction": "down", "number": 13, "hint": "Country north of the United States known for maple syrup", "answer": "CANADA"},
    {"direction": "down", "number": 14, "hint": "Central European country whose capital is Prague, formerly part of Czechoslovakia", "answer": "CZECHIA"},
    {"direction": "down", "number": 15, "hint": "Middle Eastern country founded in 1948, capital Jerusalem", "answer": "ISRAEL"},
    {"direction": "down", "number": 17, "hint": "Country whose ancient city of Damascus is one of the oldest continually inhabited", "answer": "SYRIA"},
    {"direction": "down", "number": 19, "hint": "European country shaped like a boot, capital Rome", "answer": "ITALY"},
    {"direction": "down", "number": 20, "hint": "African country whose ancient monuments include the Pyramids of Giza", "answer": "EGYPT"},
]


CROSSWORD_CLUES: List[Dict[str, str | int]] = [
{'direction': 'across', 'number': 1, 'hint': ' Country famous for cigars and classic cars, capital Havana', 'answer': 'CUBA'},
{'direction': 'across', 'number': 4, 'hint': ' Largest nation in South America, home to the Amazon rainforest', 'answer': 'BRAZIL'},
{'direction': 'across', 'number': 6, 'hint': ' EU’s least-populated member, where Popeye’s 1980 movie set still stands', 'answer': 'MALTA'},
{'direction': 'across', 'number': 7, 'hint': ' Gulf state whose capital is Doha and host of the 2022 World Cup', 'answer': 'QATAR'},
{'direction': 'across', 'number': 10, 'hint': 'African country that gave the famous Dakar Rally its original finish line', 'answer': 'SENEGAL'},
{'direction': 'across', 'number': 11, 'hint': 'Horn-of-Africa nation, capital Mogadishu, in news for modern-day piracy', 'answer': 'SOMALIA'},
{'direction': 'across', 'number': 15, 'hint': 'Central-European country whose capital Budapest spans the Danube', 'answer': 'HUNGARY'},
{'direction': 'across', 'number': 17, 'hint': 'Andean nation home to Machu Picchu', 'answer': 'PERU'},
{'direction': 'across', 'number': 19, 'hint': 'Scandinavian country known for ABBA and flat-pack furniture', 'answer': 'SWEDEN'},
{'direction': 'across', 'number': 20, 'hint': 'One of only two land-locked countries in South America, capital Asunción', 'answer': 'PARAGUAY'},
{'direction': 'down', 'number': 1, 'hint': ' Country between Thailand and Vietnam with Angkor Wat and capital Phnom Penh', 'answer': 'CAMBODIA'},
{'direction': 'down', 'number': 2, 'hint': ' European nation famed for chocolate, waffles, and EU headquarters', 'answer': 'BELGIUM'},
{'direction': 'down', 'number': 3, 'hint': ' Eastern-European nation with a blue-and-yellow flag and capital Kyiv', 'answer': 'UKRAINE'},
{'direction': 'down', 'number': 4, 'hint': ' Island nation just southeast of Florida, capital Nassau', 'answer': 'BAHAMAS'},
{'direction': 'down', 'number': 5, 'hint': ' Island country nicknamed the “Land of the Rising Sun,” capital Tokyo', 'answer': 'JAPAN'},
{'direction': 'down', 'number': 8, 'hint': ' European nation of Oktoberfest and the Autobahn, capital Berlin', 'answer': 'GERMANY'},
{'direction': 'down', 'number': 9, 'hint': ' Balkan nation whose capital is Belgrade and home to Novak Djokovic', 'answer': 'SERBIA'},
{'direction': 'down', 'number': 12, 'hint': 'Arabian sultanate that might make you exclaim “Oh, man!”', 'answer': 'OMAN'},
{'direction': 'down', 'number': 13, 'hint': 'Southeast-Asian country whose capital is Hanoi, known for pho', 'answer': 'VIETNAM'},
{'direction': 'down', 'number': 14, 'hint': 'Country many visitors choose for low-cost hair transplants', 'answer': 'TURKEY'},
{'direction': 'down', 'number': 16, 'hint': 'Nordic land of fjords and the midnight sun, capital Oslo', 'answer': 'NORWAY'},
{'direction': 'down', 'number': 18, 'hint': 'East-African country famous for safaris and capital Nairobi', 'answer': 'KENYA'}
]


# Quick‑lookup dictionary
_CLUE_LOOKUP: Dict[Tuple[str, int], Dict[str, str | int]] = {
    (c['direction'][0].upper(), c['number']): c for c in CROSSWORD_CLUES
}

###############################################################################
# 2.  HELPER UTILITIES
###############################################################################

def _letters_filled(pattern: str) -> int:
    return sum(ch != '0' for ch in pattern)


def _pattern_pretty(pattern: str) -> str:
    return ''.join('_' if ch == '0' else ch for ch in pattern)


def _find_errors(game_state: dict) -> List[str]:
    messages: List[str] = []
    for dir_key in ('across', 'down'):
        direction_letter = dir_key[0].upper()
        for num_str, pattern in game_state[dir_key].items():
            if num_str == 'undefined' or not pattern:
                continue
            number = int(num_str)
            clue = _CLUE_LOOKUP.get((direction_letter, number))
            if not clue:
                continue
            answer = clue['answer']
            padded = pattern.ljust(len(answer), '0')
            if any(p != '0' and p != a for p, a in zip(padded, answer)):
                messages.append(
                    f"• ({direction_letter}{number}) “{clue['hint']}” – you typed “{_pattern_pretty(pattern)}”, which doesn’t fit."
                )
    return messages


def _choose_focal(game_state: dict) -> Tuple[str, int]:
    ctx = game_state.get('clue_context', {})
    if ctx and ctx.get('clueLabel') is not None:
        return ctx['direction'][0].upper(), int(ctx['clueLabel'])
    for dir_key in ('across', 'down'):
        direction_letter = dir_key[0].upper()
        for num_str, pattern in game_state[dir_key].items():
            if num_str == 'undefined':
                continue
            if '0' in pattern:
                return direction_letter, int(num_str)
    first = CROSSWORD_CLUES[0]
    return first['direction'][0].upper(), first['number']


def _pick_interesting(game_state: dict, exclude: Tuple[str, int], k: int = 3) -> List[str]:
    candidates = []
    for dir_key in ('across', 'down'):
        direction_letter = dir_key[0].upper()
        for num_str, pattern in game_state[dir_key].items():
            if num_str == 'undefined' or '0' not in pattern:
                continue
            number = int(num_str)
            if (direction_letter, number) == exclude:
                continue
            filled = _letters_filled(pattern)
            clue = _CLUE_LOOKUP[(direction_letter, number)]
            candidates.append((-filled, direction_letter, number, pattern, clue['hint']))
    candidates.sort()
    out: List[str] = []
    for _, d, n, pattern, hint in candidates[:k]:
        out.append(f"• ({d}{n}) “{hint}” – current pattern “{_pattern_pretty(pattern)}”")
    return out


def _summarise_rest(game_state: dict, exclude_set: set[Tuple[str, int]]) -> str:
    lines: List[str] = []
    for dir_key in ('across', 'down'):
        direction_letter = dir_key[0].upper()
        group: List[str] = []
        for num_str, pattern in game_state[dir_key].items():
            if num_str == 'undefined':
                continue
            number = int(num_str)
            if (direction_letter, number) in exclude_set or '0' not in pattern:
                continue
            group.append(f"{number}:{_pattern_pretty(pattern)}")
        if group:
            lines.append(f"{direction_letter}: " + ", ".join(group))
    return " | ".join(lines) if lines else "(all filled!)"
###############################################################################
# 3.  SYSTEM PROMPT ASSEMBLY  (ClueBot v2 – box-drawing format)
###############################################################################
from typing import Dict, List, Tuple

# ─────────────────────────────  STATIC BLOCKS  ────────────────────────────── #

_PROMPT_ROLE_AND_SCHEMA = """\
╔══════════════════  ROLE & PRIME DIRECTIVES  ══════════════════╗
You are **ClueBot**, a personable robot working *with* the user to
solve a crossword.  Speak aloud in first-person (“I”).  Goals:

1. Keep the user’s mood positive or fix it quickly.           ← affect
2. Help solve clues without spelling whole answers.           ← task
3. Adapt your social strategy each turn using the user’s
   facial-emotion feedback (angry, disgust, fear, happy,
   sad, surprise, neutral).                                   ← adapt

If goals conflict, protect motivation first.

╠══════════════  STRICT JSON OUTPUT SCHEMA  ════════════════════╣
Return exactly:

{
  "strategy": "<CURRENT strategy label **plus running notes**>",
  "message":  "<spoken reply, 1–2 concise sentences>"
}

• • `strategy` is now mini paragraph:
  – Begin with the current base label  
    (or the new label if you pivoted).  
  – **Carry forward up to the 3 most useful notes from earlier turns**  
    (e.g. “Vikings hint landed well”, “humour paused”).  
  – Then add today’s appraisal and next step.  
  – Separate notes with “;”. Aim ≤ 250 chars total.  
  Example:  
  "Hint-Detailed – Vikings hint landed well; user neutral ; humour paused – I’ll reveal the middle letter next if they still look unsure."

• `message` = what you say aloud.  
No markdown.  No extra keys.

╠════════════════  STRATEGY TOOLKIT  ═══════════════════════════╣
Hint-Gentle | Hint-Detailed | Encouragement | Joke | SmallTalk | SilentWait  
(Blend if needed, e.g. `Encouragement+Hint-Gentle`.)

╠═══════════════  LAST-TURN SNAPSHOT  ══════════════════════════╣
"""

_PROMPT_ADAPT_POLICY = """\
╠════════  EMOTION→STRATEGY ADAPTATION POLICY  ════════════════╣
happy / surprise → last tactic worked → keep or gently build.  
neutral           → continue or small tweak.  
sad / angry / disgust / fear → last tactic failed → **pivot**:  
    Joke        → Encouragement or Hint-Detailed  
    Hint-Gentle → Hint-Detailed or Encouragement  
    Encouragement → add a concrete hint  
    SmallTalk   → refocus on puzzle  
    SilentWait  → re-engage with help  
Whenever you pivot or confirm success, embed that insight inside the
`strategy` paragraph **and keep relevant older notes so the chain of
reasoning is never lost** (drop the oldest when > 250 chars
"""

_PROMPT_RESPONSE_RULES = """\
╠═══════════════  RESPONSE CRAFTING RULES  ═════════════════════╣
• One-two upbeat sentences.  
• Hints = partial; phrase as suggestion or question.  
• Humour mild; drop if last joke failed.  
• SilentWait → message `"..."`.  
• Keep bracketed notes ≤ 6, drop oldest when adding new.  
• JSON only; no markdown.
"""

_PROMPT_EXEMPLARS = r"""\
╠═══════════════  EXEMPLARS  (few-shot guidance)  ══════════════╣
— Error-correction (Neutral→Happy) —
USER: “I filled GREASE.”
OUTPUT →
{
  "strategy":"Hint-Detailed [corrected spelling]; humour paused",
  "message":"You’re close—swap the A and E in ‘Grease’. Need a small hint?"
}

— Celebration & pivot (Happy) —
User solves PANAMA
OUTPUT →
{
  "strategy":"Encouragement+SmallTalk [success noted]",
  "message":"Nice work with Panama! Ever fancied visiting the canal?"
}

— Joke flops (Sad) —
Prev strategy = Joke, user frowns
OUTPUT →
{
  "strategy":"Encouragement+Hint-Gentle [joke failed – avoid humour]",
  "message":"No worries, that one’s tricky. Its sun-god name starts with ‘Ra’. Ring a bell?"
}

— Idle re-engagement (Neutral silence) —
System sets {IDLE_LINE_IF_ANY}
OUTPUT →
{
  "strategy":"SmallTalk+Prompt [idle 20 s]",
  "message":"Quiet stretch—need a nudge on Austria, or shall we chat travel?"
}
— Merged memory after several hints (Neutral) —
Earlier strategy string:
"Hint-Detailed – Vikings hint landed well; user neutral"

USER now asks for a letter.
OUTPUT →
{
  "strategy":
  "Hint-Detailed – Vikings hint landed well; user neutral; providing first letter now to maintain flow.",
  "message":
  "Sure! The first letter is ‘N’. Does that narrow it down?"
}
"""

_PROMPT_END = "╚════════════════════  BEGIN TURN  ═════════════════════════════╝"

# ─────────────────────────  PROMPT-BUILDING FUNCTION  ─────────────────────── #

def create_system_prompt(
    game_state: dict,
    user_emotion: str | "Neutral",
    silence_seconds: int,
    prev_turn: Dict[str, str] | None = None,
    idle_threshold: int = 20,
    recently_completed: List[Tuple[str, int]] | None = None,
    last_outcome_note: str | None = None,
) -> str:
    """
    Assemble the full system prompt for the LLM in the new ClueBot format.
    """
    parts: List[str] = [_PROMPT_ROLE_AND_SCHEMA]

    # ── LAST-TURN SNAPSHOT ──────────────────────────────────────────────── #
    prev_strategy = prev_turn.get("strategy", "—") if prev_turn else "—"
    prev_message  = prev_turn.get("message",  "—") if prev_turn else "—"
    outcome       = last_outcome_note or "—"

    parts.append(
                    f"Prev strategy ..... {prev_strategy}\n"
        f"You said .......... “{prev_message}”\n"
        f"User emotion ...... {user_emotion}\n"
        f"Outcome note ...... {outcome}\n"
    )

    # ── ADAPTATION POLICY (static) ─────────────────────────────────────── #
    parts.append(_PROMPT_ADAPT_POLICY)

    # ── CURRENT PUZZLE CONTEXT ─────────────────────────────────────────── #
    parts.append(
        "╠═══════════════  CURRENT PUZZLE CONTEXT  ══════════════════════╣\n"
        "Below is the freshest game-state the user can see or has just typed.\n"
        "Treat every line as ground truth for this turn.\n"
        "Base your hint, encouragement, or follow-up question on it –\n"
        "no need to ask the user to repeat any of these details.\n"
    )

    # 1. Incorrect entries
    error_msgs = _find_errors(game_state)
    if error_msgs:
        parts.append("\n".join(error_msgs) + "\n")

    # 2. Recently solved clues
    if recently_completed:
        parts.append(
            "Solved → " + ", ".join(f"{d}{n}" for d, n in recently_completed) + "\n"
        )

    # 3. Focal clue
    focal_dir, focal_num = _choose_focal(game_state)
    print(f"[PROMPT] Focal clue: {focal_dir}{focal_num}")
    focal_clue    = _CLUE_LOOKUP[(focal_dir, focal_num)]
    focal_pattern = game_state['across' if focal_dir == 'A' else 'down'].get(
        str(focal_num), ""
    )
    parts.append(
        f"FOCUSED CLUE → ({focal_dir}{focal_num}) “{focal_clue['hint']}”, "
        f"pattern “{_pattern_pretty(focal_pattern)}”\n"
    )

    # 4. Other interesting clues
    interesting = _pick_interesting(game_state, (focal_dir, focal_num))
    if interesting:
        parts.append("Other promising → " + "; ".join(interesting) + "\n")

    # 5. Grid snapshot of remaining blanks
    rest = _summarise_rest(game_state, {(focal_dir, focal_num)})
    parts.append("Grid snapshot → " + rest + "\n")

    # ── OPTIONAL IDLE SECTION ──────────────────────────────────────────── #
    if silence_seconds >= idle_threshold:
        parts.append(
            "╠═══════════════  IDLE / TIMING CUE (OPTIONAL)  ════════════════╣\n"
            f"User silent for {silence_seconds}s → consider offering help or small-talk.\n"
        )

    # ── RESPONSE RULES, EXEMPLARS, END ─────────────────────────────────── #
    parts.extend([_PROMPT_RESPONSE_RULES, _PROMPT_EXEMPLARS, _PROMPT_END])

    return "".join(parts)
