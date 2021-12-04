import re

REMOVE_RE = re.compile(r'( +|\[(?!sound:).*?\])(?![^{]*})')

def remove_syntax(text):
    text = REMOVE_RE.sub('', text)
    text = text.replace('{', '')
    text = text.replace('}', '')
    return text
