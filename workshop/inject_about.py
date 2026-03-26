#!/usr/bin/env python3
"""Inject 'About this codelab' card and copy buttons into the claat-exported index.html."""

import sys
import re
from datetime import date

AUTHOR = "Saoussen Chaabnia"
UPDATED = date.today().strftime("%b %d, %Y")

CARD_HTML = f"""
    <div style="background:#fff;padding:40px 48px 32px;border-bottom:1px solid #e0e0e0;">
      <div style="max-width:800px;margin:0 auto;">
        <div style="border:1px solid #dadce0;border-radius:8px;padding:32px;font-family:'Google Sans',Roboto,sans-serif;">
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
      </div>
    </div>
"""

COPY_BUTTON_JS = """
<style>
  .code-copy-wrapper { position: relative; }
  .code-copy-btn {
    position: absolute; top: 8px; right: 8px;
    background: #fff; border: 1px solid #dadce0; border-radius: 4px;
    padding: 4px 8px; font-size: 12px; cursor: pointer;
    display: none; align-items: center; gap: 4px;
    color: #5f6368; font-family: Roboto, sans-serif;
    z-index: 10;
  }
  .code-copy-wrapper:hover .code-copy-btn { display: flex; }
  .code-copy-btn:hover { background: #f1f3f4; }
  .code-copy-btn.copied { color: #1e8e3e; border-color: #1e8e3e; }
</style>
<script>
document.addEventListener('DOMContentLoaded', function() {
  function addCopyButtons() {
    document.querySelectorAll('pre code[class*="language-bash"], pre code[class*="language-python"], pre code[class*="language-json"], pre code[class*="language-dockerfile"]').forEach(function(code) {
      var pre = code.parentElement;
      if (pre.parentElement && pre.parentElement.classList.contains('code-copy-wrapper')) return;
      var wrapper = document.createElement('div');
      wrapper.className = 'code-copy-wrapper';
      pre.parentNode.insertBefore(wrapper, pre);
      wrapper.appendChild(pre);
      var btn = document.createElement('button');
      btn.className = 'code-copy-btn';
      btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" height="14" width="14" viewBox="0 0 24 24" fill="currentColor"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg> Copy';
      btn.addEventListener('click', function() {
        var text = code.innerText;
        navigator.clipboard.writeText(text).then(function() {
          btn.innerHTML = '&#10003; Copied';
          btn.classList.add('copied');
          setTimeout(function() {
            btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" height="14" width="14" viewBox="0 0 24 24" fill="currentColor"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg> Copy';
            btn.classList.remove('copied');
          }, 2000);
        });
      });
      wrapper.appendChild(btn);
    });
  }
  // Run immediately and retry after web components load
  addCopyButtons();
  setTimeout(addCopyButtons, 1000);
  setTimeout(addCopyButtons, 3000);
});
</script>
"""

def inject(html_path: str) -> None:
    with open(html_path, encoding="utf-8") as f:
        content = f.read()

    # 1. Inject "About" card at the top of the first <google-codelab-step>
    pattern = r'(<google-codelab-step[^>]*>)'
    match = re.search(pattern, content)
    if not match:
        print("ERROR: could not find <google-codelab-step> in HTML", file=sys.stderr)
        sys.exit(1)
    insert_pos = match.end()
    content = content[:insert_pos] + CARD_HTML + content[insert_pos:]

    # 2. Inject copy button CSS+JS before </body>
    content = content.replace('</body>', COPY_BUTTON_JS + '\n</body>')

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Injected About card and copy buttons into {html_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path/to/index.html>")
        sys.exit(1)
    inject(sys.argv[1])
