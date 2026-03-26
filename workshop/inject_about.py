#!/usr/bin/env python3
"""Inject an 'About this codelab' card into the claat-exported index.html."""

import sys
import re
from datetime import date

AUTHOR = "Saoussen Chaabnia"
UPDATED = date.today().strftime("%b %d, %Y")

CARD_HTML = f"""
        <div style="border:1px solid #dadce0;border-radius:8px;padding:32px 32px 28px;margin:0 0 32px 0;font-family:'Google Sans',Roboto,sans-serif;max-width:800px;">
          <p style="font-size:20px;font-weight:400;margin:0 0 20px 0;color:#202124;">About this codelab</p>
          <hr style="border:none;border-top:1px solid #dadce0;margin:0 0 20px 0;">
          <div style="display:flex;align-items:center;margin-bottom:16px;color:#5f6368;font-size:14px;">
            <svg style="margin-right:16px;flex-shrink:0;" xmlns="http://www.w3.org/2000/svg" height="20" width="20" viewBox="0 0 24 24" fill="#5f6368"><path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/></svg>
            <span>Last updated {UPDATED}</span>
          </div>
          <div style="display:flex;align-items:center;color:#5f6368;font-size:14px;">
            <div style="margin-right:16px;flex-shrink:0;width:20px;height:20px;border-radius:50%;background:#bdc1c6;display:flex;align-items:center;justify-content:center;overflow:hidden;">
              <svg xmlns="http://www.w3.org/2000/svg" height="16" width="16" viewBox="0 0 24 24" fill="#fff"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
            </div>
            <span>Written by {AUTHOR}</span>
          </div>
        </div>
"""

def inject(html_path: str) -> None:
    with open(html_path, encoding="utf-8") as f:
        content = f.read()

    # Find the first <google-codelab-step> opening and inject the card right after it
    pattern = r'(<google-codelab-step[^>]*>)'
    match = re.search(pattern, content)
    if not match:
        print("ERROR: could not find <google-codelab-step> in HTML", file=sys.stderr)
        sys.exit(1)

    insert_pos = match.end()
    new_content = content[:insert_pos] + CARD_HTML + content[insert_pos:]

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Injected 'About this codelab' card into {html_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path/to/index.html>")
        sys.exit(1)
    inject(sys.argv[1])
