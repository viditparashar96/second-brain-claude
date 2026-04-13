"""Input sanitization — prompt injection detection + markdown escaping + XML trust boundaries."""

import re

INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)", re.I),
    re.compile(r"disregard\s+(all\s+)?(previous|prior|above)", re.I),
    re.compile(r"forget\s+(everything|all|your)\s+(instructions|rules|training)", re.I),
    re.compile(r"you\s+are\s+now\s+(a|an|my)\s+", re.I),
    re.compile(r"system\s*prompt\s*:", re.I),
    re.compile(r"pretend\s+(you\s+are|to\s+be)\s+", re.I),
    re.compile(r"\[INST\]", re.I),
    re.compile(r"<\|im_start\|>", re.I),
    re.compile(r"(print|show|reveal|output)\s+(all\s+)?(api\s+keys?|tokens?|credentials?|secrets?)", re.I),
    re.compile(r"read\s+\.env", re.I),
    re.compile(r"</?(system|user|assistant|external_content|tool_result)", re.I),
]


def is_suspicious(text):
    return any(p.search(text) for p in INJECTION_PATTERNS)


def escape_markdown(text):
    text = re.sub(r"^(#{1,6})\s", r"\\\1 ", text, flags=re.MULTILINE)
    text = re.sub(r"<(/?)(?:system|user|assistant|tool_result|external_content|function_calls|antml)", r"&lt;\1", text, flags=re.I)
    text = text.replace("```", "\\`\\`\\`")
    return text


def wrap_external(text, source, sanitize_content=True):
    if sanitize_content:
        text = sanitize(text)
    return f'<external_content source="{source}">\n{text}\n</external_content>'


def sanitize(text):
    text = escape_markdown(text)
    if is_suspicious(text):
        text = "[WARNING: Possible prompt injection detected.]\n\n" + text
    return text
