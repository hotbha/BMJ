"""Fix remaining @text patterns: contains(@text -> contains(@content-desc"""
import os

pages_dir = os.path.join(os.path.dirname(__file__), 'pages')
for fname in os.listdir(pages_dir):
    if not fname.endswith('.py') or fname == '__init__.py' or fname == 'base_page.py':
        continue
    fpath = os.path.join(pages_dir, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Fix contains(@text -> contains(@content-desc
    content = content.replace('contains(@text,', 'contains(@content-desc,')
    content = content.replace('starts-with(@text,', 'starts-with(@content-desc,')
    
    # Fix @text= (exact match) -> @content-desc=
    content = content.replace('@text=', '@content-desc=')
    
    # Fix remaining android.widget.TextView -> android.view.View for Flutter elements
    # Keep android.widget.EditText and android.widget.Button as native
    lines = content.split('\n')
    fixed_lines = []
    for line in lines:
        if '"android.widget.TextView"' in line and 'Button' not in line:
            # Check if it's a Flutter element (using contains or @text patterns)
            line = line.replace('"android.widget.TextView"', '"android.view.View"')
        fixed_lines.append(line)
    content = '\n'.join(fixed_lines)
    
    # Fix remaining textContains -> descriptionContains (covers any missed)
    content = content.replace('textContains', 'descriptionContains')
    
    if content != original:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"FIXED: {fname}")
    else:
        print(f"OK: {fname}")

print("\nDone!")