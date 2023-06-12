import re

REMOVE_RE = re.compile(r"( +|\[(?!sound:).*?\])(?![^{]*})")


def remove_syntax(text):
    if not any(c in text for c in "{}[]"):
        return text
    text = REMOVE_RE.sub("", text)
    text = text.replace("{", "")
    text = text.replace("}", "")
    return text
