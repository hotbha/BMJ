"""Fix all page objects: textContains -> descriptionContains, @text -> @content-desc, TextView -> View"""
import os
import re

pages_dir = os.path.join(os.path.dirname(__file__), 'pages')
for fname in os.listdir(pages_dir):
    if not fname.endswith('.py') or fname == '__init__.py':
        continue
    fpath = os.path.join(pages_dir, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Skip base_page.py - it doesn't have textContains
    if fname == 'base_page.py':
        continue
    
    original = content
    
    # Replace textContains with descriptionContains
    content = content.replace('textContains', 'descriptionContains')
    
    # Replace @text= with @content-desc= for XPath
    content = content.replace('@text="', '@content-desc="')
    content = content.replace("@text='", "@content-desc='")
    
    # Replace android.widget.TextView with android.view.View for Flutter elements
    # (be careful not to change EditText or Button)
    content = content.replace('"android.widget.TextView"', '"android.view.View"')
    
    if content != original:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"FIXED: {fname}")
    else:
        print(f"SKIP: {fname} (no changes)")

print("\nDone!")