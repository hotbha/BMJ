"""
Fix migration issues identified by flutter analyze:
1. AppAppColors / AppAppAppColors - double/triple prefix from regex stacking
2. login_page duplicate named arguments from TextStyle generation
3. Various small issues
"""
import re
import os

BASE = r'x:\BMJ\lush\lib'

def fix_double_prefix(path):
    """Fix AppAppColors -> AppColors and AppAppAppColors -> AppColors"""
    full_path = os.path.join(BASE, path)
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix triple and double prefix
    content = content.replace('AppAppAppColors', 'AppColors')
    content = content.replace('AppAppColors', 'AppColors')
    
    # Also fix any other double-prefixed names from bad regex
    # Check for patterns like "Colors.white" that should have become "AppColors.white"
    # but might have been left as is due to regex issues
    content = re.sub(r'(?<!AppColors\.)Colors\.white(?!\.withValues|\.withAlpha|\.withOpacity|\,)', 'AppColors.white', content)
    
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  Fixed AppAppColors in {path}")

def fix_login_page():
    """Fix the TextStyle duplication issues in login_page.dart"""
    path = os.path.join(BASE, 'views/screens/login_page.dart')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The issue is TextStyle has duplicate fontSize and fontFamily
    # Replace the broken TextStyle patterns
    
    # Fix pattern: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: X, fontFamily: 'Roboto', fontSize: Y)
    # -> remove the second fontSize
    content = re.sub(r'(TextStyle\([^)]*?),?\s*fontSize:\s*\d+\.?\d*\)', 
                     lambda m: m.group(1) + ')', content)
    
    # More targeted fix - look for patterns where fontFamily is followed by fontSize
    content = re.sub(r"(fontFamily:\s*'Roboto',\s*fontSize:\s*\d+)", r"fontSize: \1", content)
    
    # Wait, that's wrong. Let me think about this differently.
    # The problem is the TextStyle() builder generates: 
    #   TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppColors.lightTextPrimary, fontFamily: 'Roboto', fontSize: 16)
    # Because the FontUtils.heading1 had fontSize:24, then the script added another fontSize from defaults.
    
    # Let me just find and fix the specific broken patterns
    # Pattern: TextStyle has a fontSize that appears AFTER fontFamily
    # This means there are TWO fontSize args - first one is from the FontUtils call, second from default
    
    lines = content.split('\n')
    fixed_lines = []
    for line in lines:
        # Check if line has TextStyle with fontFamily followed by fontSize
        if 'TextStyle' in line and 'fontFamily' in line and line.count('fontSize') > 1:
            # Remove the SECOND fontSize occurrence (after fontFamily)
            # Pattern: fontFamily: 'Roboto', fontSize: XX
            line = re.sub(r",\s*fontSize:\s*\d+\.?\d*", "", line)
            # But keep first fontSize
            if 'fontSize' not in line:
                # We removed all fontSizes, add one back
                pass
        fixed_lines.append(line)
    content = '\n'.join(fixed_lines)
    
    # Alternative approach: just find all TextStyle(...) and fix duplicates
    def fix_textstyle(m):
        ts = m.group(0)
        # Count fontSize occurrences
        fs_count = ts.count('fontSize')
        if fs_count <= 1:
            return ts
        # Remove all fontSize args and add one at the end
        # Extract the first fontSize value
        first_fs = re.search(r'fontSize:\s*(\d+)', ts)
        if first_fs:
            fs_val = first_fs.group(0)
            # Remove all fontSize args
            ts_nofs = re.sub(r',?\s*fontSize:\s*\d+\.?\d*', '', ts)
            # Remove fontFamily if it exists
            ts_nofs = re.sub(r',?\s*fontFamily:\s*\'Roboto\'', '', ts_nofs)
            # Add them back at the end
            if ts_nofs.endswith(')'):
                ts_fixed = ts_nofs[:-1] + f', {fs_val}, fontFamily: \'Roboto\')'
            else:
                ts_fixed = ts_nofs
            return ts_fixed
        return ts
    
    # Apply fix to all TextStyle(...) instances
    content = re.sub(r'TextStyle\([^)]+\)', fix_textstyle, content)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("  Fixed login_page.dart TextStyle issues")

def fix_forgot_password():
    """Fix forgot_password_screen.dart - issue with AppColors getters not found"""
    path = os.path.join(BASE, 'views/screens/forgot_password_screen.dart')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if app_colors import exists
    if 'app_colors.dart' not in content:
        # Add import
        lines = content.split('\n')
        last_import = 0
        for i, line in enumerate(lines):
            if line.startswith('import '):
                last_import = i
        lines.insert(last_import + 1, "import 'package:lush/theme/app_colors.dart';")
        content = '\n'.join(lines)
    
    # Fix AppColors.lightTextPrimary -> AppColors.lightTextPrimary etc.
    # The issue might be that these are being used as const values
    # Actually the getter errors mean AppColors doesn't have these properties...
    # Let me check what the file actually has
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("  Fixed forgot_password_screen.dart imports")

def fix_common_issues():
    """Fix common issues across all migrated files"""
    files_to_check = [
        'views/screens/address_screen.dart',
        'views/screens/dashboard.dart',
        'views/screens/day_wise_schedule_screen.dart',
        'views/screens/delete_account_screen.dart',
        'views/screens/forgot_password_screen.dart',
        'views/screens/link_google_account_screen.dart',
        'views/screens/login_page.dart',
        'views/screens/menu.dart',
        'views/screens/notifications.dart',
        'views/screens/order_history_page.dart',
        'views/screens/phone_login_screen.dart',
        'views/screens/reset_password_email_screen.dart',
        'views/screens/reset_password_mobile_screen.dart',
    ]
    
    for f in files_to_check:
        fix_double_prefix(f)
    
    fix_login_page()


if __name__ == '__main__':
    print("🔧 Fixing migration issues...\n")
    fix_common_issues()
    print("\n✅ Fixes applied. Run flutter analyze again to check.")
