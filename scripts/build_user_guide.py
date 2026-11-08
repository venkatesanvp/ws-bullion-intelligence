"""Publish the reviewed user guide as local HTML and Markdown; no external dependencies."""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def render(text):
    blocks = []
    for block in text.strip().split('\n\n'):
        if block.startswith('# '):
            blocks.append('<h1>' + escape(block[2:]) + '</h1>')
        elif block.startswith('## '):
            blocks.append('<h2>' + escape(block[3:]) + '</h2>')
        else:
            blocks.append('<p>' + escape(block).replace('\n', ' ') + '</p>')
    return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Bullion research user guide</title><style>body{font:18px/1.6 system-ui;max-width:900px;margin:32px auto;padding:0 20px;color:#162d38}h2{margin-top:2em}a{color:#075766}</style><main><a href="/user-guide.md">Open or download the Markdown guide</a>' + '\n'.join(blocks) + '</main></html>\n'


def main():
    text = (ROOT / 'docs/06-user-guide/BULLION_INTELLIGENCE_USER_GUIDE.md').read_text(encoding='utf-8-sig')
    for name, content in [('user-guide.md', text), ('user-guide.html', render(text))]:
        (ROOT / 'frontend/public' / name).write_text(content, encoding='utf-8')


if __name__ == '__main__':
    main()
