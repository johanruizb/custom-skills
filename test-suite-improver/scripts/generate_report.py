#!/usr/bin/env python3
"""Generate an HTML test suite report from a Markdown file.

Uses the `markdown` package when importable (optional dependency);
otherwise falls back to a small built-in converter covering headings,
lists, bold, inline code, and fenced code blocks.
"""
import html
import re
import sys
from pathlib import Path

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Test Suite Report</title>
<style>
  body {{ font-family: -apple-system, sans-serif; max-width: 960px; margin: 2em auto; padding: 0 1em; line-height: 1.6; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
  th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
  th {{ background: #f4f4f4; }}
  h1, h2, h3 {{ color: #333; }}
  code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
  pre {{ background: #f8f8f8; padding: 1em; border-radius: 5px; overflow-x: auto; }}
</style>
</head>
<body>
{body}
</body>
</html>"""


def _inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return text


def builtin_markdown(text):
    out, in_code, in_list = [], False, False
    for line in text.splitlines():
        if line.startswith("```"):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append("<pre><code>" if not in_code else "</code></pre>")
            in_code = not in_code
            continue
        if in_code:
            out.append(html.escape(line, quote=False))
            continue
        match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if match:
            if in_list:
                out.append("</ul>")
                in_list = False
            level = len(match.group(1))
            out.append(f"<h{level}>{_inline(match.group(2))}</h{level}>")
            continue
        match = re.match(r"^\s*[-*]\s+(.*)$", line)
        if match:
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{_inline(match.group(1))}</li>")
            continue
        if in_list and not line.strip():
            out.append("</ul>")
            in_list = False
            continue
        if line.strip():
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<p>{_inline(line)}</p>")
    if in_list:
        out.append("</ul>")
    if in_code:
        out.append("</code></pre>")
    return "\n".join(out)


def markdown_to_html(md_path, output_path):
    content = Path(md_path).read_text()
    try:
        import markdown
        body = markdown.markdown(content)
    except ImportError:
        body = builtin_markdown(content)
    Path(output_path).write_text(TEMPLATE.format(body=body))
    print(f"Report saved to {output_path}")


def _self_check():
    rendered = builtin_markdown(
        "# Title\n\n- item **bold**\n- `code`\n\n```py\nx < 1\n```\n"
    )
    assert "<h1>Title</h1>" in rendered
    assert "<li>item <strong>bold</strong></li>" in rendered
    assert "<li><code>code</code></li>" in rendered
    assert "<pre><code>" in rendered and "x &lt; 1" in rendered
    print("self-check ok")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        markdown_to_html(sys.argv[1], sys.argv[2])
    else:
        _self_check()
