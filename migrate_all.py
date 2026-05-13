"""
Comprehensive migration script for Requirement 1: Theme Alignment.
Migrates all remaining files from legacy LushTheme/FontUtils/raw Colors to AppColors/AppTextStyles.
"""
import re
import os

BASE = r'x:\BMJ\lush\lib'

# ============================================================
# REPLACEMENT MAPPINGS
# ============================================================

LUSH_THEME_MAP = {
    'LushTheme.orangeAccent': 'AppColors.primaryOrange',
    'LushTheme.white': 'AppColors.white',
    'LushTheme.nearlyWhite': 'AppColors.offWhite',
    'LushTheme.darkerText': 'AppColors.lightTextPrimary',
    'LushTheme.lightText': 'AppColors.lightTextSecondary',
    'LushTheme.grey': 'AppColors.grey',
    'LushTheme.appbarColor': 'AppColors.primaryOrange',
    'LushTheme.nearlyBlue': 'AppColors.info',
    'LushTheme.nearlyDarkBlue': 'AppColors.secondaryTealDark',
    'LushTheme.background': 'AppColors.lightBackground',
}

# Files that need LushTheme->AppColors migration (and add app_colors import)
LUSH_THEME_FILES = {
    # file_path: has_app_colors_already
    'views/screens/menu.dart': False,
    'views/screens/notifications.dart': False,
    'views/screens/order_history_page.dart': False,
    'views/screens/dashboard.dart': True,  # already has app_colors import
}

# Files that need FontUtils->TextStyle migration (and remove font_utils import, add app_colors import)
FONT_UTILS_FILES = [
    'views/screens/notifications.dart',  # also in LushTheme list
    'views/screens/login_page.dart',
    'views/screens/phone_login_screen.dart',
    'views/screens/reset_password_email_screen.dart',
    'views/screens/forgot_password_screen.dart',
    'utils/text_utils.dart',
]

# Files that need more specific care (partially migrated, need color cleanup)
COLOR_ONLY_FILES = [
    'views/screens/day_wise_schedule_screen.dart',
    'views/screens/delete_account_screen.dart',
    'views/screens/link_google_account_screen.dart',
    'views/screens/reset_password_mobile_screen.dart',
    'views/screens/address_screen.dart',
]

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def read_file(path):
    full = os.path.join(BASE, path)
    with open(full, 'r', encoding='utf-8') as f:
        return f.read(), full

def write_file(full_path, content):
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)

def add_import(content, import_line, after_any_import=True):
    """Add an import line if not already present, after existing imports."""
    if import_line in content:
        return content
    if after_any_import:
        # Find the last import line
        lines = content.split('\n')
        last_import_idx = -1
        for i, line in enumerate(lines):
            if line.startswith('import '):
                last_import_idx = i
        if last_import_idx >= 0:
            lines.insert(last_import_idx + 1, import_line)
            return '\n'.join(lines)
    # Fallback: add after first line
    lines = content.split('\n')
    lines.insert(1, import_line)
    return '\n'.join(lines)

def remove_import(content, import_pattern):
    """Remove an import line matching a pattern."""
    lines = content.split('\n')
    new_lines = [l for l in lines if import_pattern not in l]
    return '\n'.join(new_lines)

def replace_lush_theme(content):
    """Replace LushTheme.XXX with AppColors.XXX"""
    for old, new in LUSH_THEME_MAP.items():
        content = content.replace(old, new)
    # Handle special cases
    content = content.replace('LushTheme.nearlyBlue.withAlpha(25)', 'AppColors.info.withValues(alpha:0.1)')
    content = content.replace('LushTheme.nearlyBlue.withAlpha(50)', 'AppColors.info.withValues(alpha:0.2)')
    content = content.replace("LushTheme.white.withAlpha(242)", "AppColors.white.withValues(alpha:0.95)")
    content = content.replace("LushTheme.grey.withAlpha(76)", "AppColors.grey.withValues(alpha:0.3)")
    content = content.replace("LushTheme.grey.withAlpha(50)", "AppColors.grey.withValues(alpha:0.2)")
    # Handle LushTheme.fontName - remove from TextStyle
    content = re.sub(r',\s*fontFamily:\s*LushTheme\.fontName', '', content)
    content = content.replace("fontFamily: LushTheme.fontName", "")
    return content

def replace_font_utils(content):
    """Replace FontUtils.XXX(...) with TextStyle(...)"""
    # FontUtils.heading1(color: X, fontSize: Y, fontWeight: Z) -> TextStyle(fontSize: Y, fontWeight: Z, color: X, fontFamily: 'Roboto')
    # FontUtils.bodyText(color: X, fontSize: Y) -> TextStyle(fontSize: Y, color: X, fontFamily: 'Roboto')
    # etc.
    
    # Pattern: FontUtils.heading1(...) -> TextStyle(...)
    # Capture the function name and the arguments
    patterns = [
        (r'FontUtils\.heading1\(([^)]*)\)', 'heading1'),
        (r'FontUtils\.bodyText\(([^)]*)\)', 'bodyText'),
        (r'FontUtils\.buttonText\(([^)]*)\)', 'buttonText'),
        (r'FontUtils\.hintText\(([^)]*)\)', 'hintText'),
        (r'FontUtils\.captionText\(([^)]*)\)', 'captionText'),
    ]
    
    for regex, func_name in patterns:
        def make_replacer(fn):
            def replacer(m):
                args_str = m.group(1)
                # Parse the named arguments
                args = {}
                for kv in re.findall(r'(\w+):\s*([^,)]+)', args_str):
                    key = kv[0].strip()
                    val = kv[1].strip()
                    args[key] = val
                
                default_sizes = {
                    'heading1': ('24', 'FontWeight.bold'),
                    'bodyText': ('16', 'FontWeight.normal'),
                    'buttonText': ('16', 'FontWeight.w600'),
                    'hintText': ('14', 'FontWeight.normal'),
                    'captionText': ('12', 'FontWeight.normal'),
                }
                default_font_sizes = {
                    'heading1': 24, 'bodyText': 16, 'buttonText': 16,
                    'hintText': 14, 'captionText': 12,
                }
                
                result_parts = []
                # fontSize
                fs = args.get('fontSize', str(default_font_sizes.get(fn, 14)))
                result_parts.append(f'fontSize: {fs}')
                # fontWeight - for heading1 default is bold, for buttonText default is w600
                if fn == 'heading1':
                    fw = args.get('fontWeight', 'FontWeight.bold')
                elif fn == 'buttonText':
                    fw = args.get('fontWeight', 'FontWeight.w600')
                else:
                    fw = args.get('fontWeight', 'FontWeight.normal')
                if fw != 'FontWeight.normal' or fn in ('heading1', 'buttonText'):
                    result_parts.append(f'fontWeight: {fw}')
                # color
                if 'color' in args:
                    result_parts.append(f'color: {args["color"]}')
                # fontFamily
                result_parts.append("fontFamily: 'Roboto'")
                
                return f'TextStyle({", ".join(result_parts)})'
            return replacer
        
        content = re.sub(regex, make_replacer(func_name), content)
    
    return content

def replace_raw_colors(content):
    """Replace raw Colors.XXX with AppColors equivalents where appropriate."""
    replacements = [
        # Colors.grey[200] -> AppColors.lightDivider
        (r'Colors\.grey\[200\]', 'AppColors.lightDivider'),
        (r'Colors\.grey\[300\]', 'AppColors.lightDivider'),
        (r'Colors\.grey\[400\]', 'AppColors.lightTextDisabled'),
        (r'Colors\.grey\[500\]', 'AppColors.grey'),
        (r'Colors\.grey\[600\]', 'AppColors.lightTextSecondary'),
        (r'Colors\.grey\[700\]', 'AppColors.darkGrey'),
        (r'Colors\.grey\.withValues\(alpha:\s*0\.\d+\)', 'AppColors.grey'),
        # Colors.red -> AppColors.error
        (r'Colors\.red(?!\[)', 'AppColors.error'),
        # Colors.red[700] -> AppColors.error
        (r'Colors\.red\[700\]', 'AppColors.error'),
        # Colors.red[400] -> AppColors.error
        (r'Colors\.red\[400\]', 'AppColors.error'),
        # Colors.green -> AppColors.success
        (r'Colors\.green(?!\[)', 'AppColors.success'),
        (r'Colors\.green\[700\]', 'AppColors.success'),
        # Colors.blue -> AppColors.info 
        (r'Colors\.blue(?!\[)', 'AppColors.info'),
        (r'Colors\.blue\[700\]', 'AppColors.info'),
        (r'Colors\.blue\[800\]', 'AppColors.info'),
        # Colors.amber -> AppColors.primaryOrange
        (r'Colors\.amber(?!\[)', 'AppColors.primaryOrange'),
        (r'Colors\.amber\[700\]', 'AppColors.primaryOrangeDark'),
        (r'Colors\.amber\[800\]', 'AppColors.primaryOrangeDark'),
        # Colors.orange -> AppColors.primaryOrange
        (r'Colors\.orange(?!\[)', 'AppColors.primaryOrange'),
        (r'Colors\.orange\[700\]', 'AppColors.primaryOrangeDark'),
        # Colors.deepPurple -> AppColors.secondaryTeal
        (r'Colors\.deepPurple(?!\[)', 'AppColors.secondaryTeal'),
        # Colors.black87 -> AppColors.lightTextPrimary
        (r'Colors\.black87', 'AppColors.lightTextPrimary'),
        (r'Colors\.black(?!87)', 'AppColors.nearlyBlack'),
        # Colors.white -> AppColors.white 
        (r'Colors\.white(?!\.)', 'AppColors.white'),
        (r'Colors\.transparent', 'Colors.transparent'),  # Keep transparent
    ]
    # Fix: Replace Colors.white that's NOT part of Colors.white.withValues or AppColors.white
    # We need to be careful - only replace standalone Colors.white
    content = re.sub(r'(?<!AppColors\.)Colors\.white(?!\.withValues|\.withAlpha)', 'AppColors.white', content)
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    return content

# ============================================================
# FILE-SPECIFIC MIGRATION FUNCTIONS
# ============================================================

def migrate_menu():
    content, path = read_file('views/screens/menu.dart')
    
    # 1. Remove theme.dart import
    content = remove_import(content, 'theme.dart')
    
    # 2. Add app_colors + app_text_styles imports
    content = add_import(content, "import 'package:lush/theme/app_colors.dart';")
    content = add_import(content, "import 'package:lush/theme/app_text_styles.dart';")
    
    # 3. Replace LushTheme references
    content = replace_lush_theme(content)
    
    # 4. Replace raw Colors references
    content = replace_raw_colors(content)
    
    write_file(path, content)
    print(f"✅ Migrated menu.dart")

def migrate_notifications():
    content, path = read_file('views/screens/notifications.dart')
    
    # 1. Remove legacy imports
    content = remove_import(content, 'theme.dart')
    content = remove_import(content, 'font_utils.dart')
    
    # 2. Add new imports
    content = add_import(content, "import 'package:lush/theme/app_colors.dart';")
    content = add_import(content, "import 'package:lush/theme/app_text_styles.dart';")
    
    # 3. Replace LushTheme
    content = replace_lush_theme(content)
    
    # 4. Replace FontUtils
    content = replace_font_utils(content)
    
    # 5. Replace raw Colors
    content = replace_raw_colors(content)
    
    write_file(path, content)
    print(f"✅ Migrated notifications.dart")

def migrate_order_history_page():
    content, path = read_file('views/screens/order_history_page.dart')
    
    # 1. Remove theme.dart import
    content = remove_import(content, 'theme.dart')
    
    # 2. Add new imports
    content = add_import(content, "import 'package:lush/theme/app_colors.dart';")
    content = add_import(content, "import 'package:lush/theme/app_text_styles.dart';")
    
    # 3. Replace LushTheme
    content = replace_lush_theme(content)
    
    # 4. Replace raw Colors
    content = replace_raw_colors(content)
    
    write_file(path, content)
    print(f"✅ Migrated order_history_page.dart")

def migrate_login_page():
    content, path = read_file('views/screens/login_page.dart')
    
    # 1. Check what imports exist
    has_app_colors = "app_colors.dart" in content
    has_app_text_styles = "app_text_styles.dart" in content
    
    # 2. Remove font_utils import  
    content = remove_import(content, 'font_utils.dart')
    
    # 3. Add new imports if needed
    if not has_app_colors:
        content = add_import(content, "import 'package:lush/theme/app_colors.dart';")
    if not has_app_text_styles:
        content = add_import(content, "import 'package:lush/theme/app_text_styles.dart';")
    
    # 4. Replace FontUtils
    content = replace_font_utils(content)
    
    # 5. Replace raw Colors
    content = replace_raw_colors(content)
    
    write_file(path, content)
    print(f"✅ Migrated login_page.dart")

def migrate_phone_login_screen():
    content, path = read_file('views/screens/phone_login_screen.dart')
    
    content = remove_import(content, 'font_utils.dart')
    content = add_import(content, "import 'package:lush/theme/app_colors.dart';")
    content = add_import(content, "import 'package:lush/theme/app_text_styles.dart';")
    content = replace_font_utils(content)
    content = replace_raw_colors(content)
    
    write_file(path, content)
    print(f"✅ Migrated phone_login_screen.dart")

def migrate_reset_password_email_screen():
    content, path = read_file('views/screens/reset_password_email_screen.dart')
    
    content = remove_import(content, 'font_utils.dart')
    content = add_import(content, "import 'package:lush/theme/app_colors.dart';")
    content = add_import(content, "import 'package:lush/theme/app_text_styles.dart';")
    content = replace_font_utils(content)
    content = replace_raw_colors(content)
    
    write_file(path, content)
    print(f"✅ Migrated reset_password_email_screen.dart")

def migrate_text_utils():
    content, path = read_file('utils/text_utils.dart')
    
    # Remove font_utils import
    content = remove_import(content, 'font_utils.dart')
    
    # Replace FontUtils calls within text_utils.dart
    # This file wraps FontUtils methods, so we need to replace the calls
    # but keep the wrapper methods intact.
    content = replace_font_utils(content)
    
    write_file(path, content)
    print(f"✅ Migrated text_utils.dart")

def migrate_forgot_password_screen():
    content, path = read_file('views/screens/forgot_password_screen.dart')
    
    # Check if app_colors is already imported
    has_app_colors = 'app_colors.dart' in content
    
    # Check for FontUtils usage
    has_font_utils = 'FontUtils' in content
    
    if has_font_utils:
        content = add_import(content, "import 'package:lush/theme/app_colors.dart';")
        content = add_import(content, "import 'package:lush/theme/app_text_styles.dart';")
        content = replace_font_utils(content)
    
    # Replace raw Colors
    content = replace_raw_colors(content)
    
    write_file(path, content)
    print(f"✅ Migrated forgot_password_screen.dart")

def migrate_day_wise_schedule_screen():
    content, path = read_file('views/screens/day_wise_schedule_screen.dart')
    
    has_app_colors = 'app_colors.dart' in content
    if not has_app_colors:
        content = add_import(content, "import 'package:lush/theme/app_colors.dart';")
    
    content = replace_raw_colors(content)
    
    write_file(path, content)
    print(f"✅ Migrated day_wise_schedule_screen.dart")

def migrate_delete_account_screen():
    content, path = read_file('views/screens/delete_account_screen.dart')
    
    has_app_colors = 'app_colors.dart' in content
    if not has_app_colors:
        content = add_import(content, "import 'package:lush/theme/app_colors.dart';")
    
    content = replace_raw_colors(content)
    
    write_file(path, content)
    print(f"✅ Migrated delete_account_screen.dart")

def migrate_link_google_account_screen():
    content, path = read_file('views/screens/link_google_account_screen.dart')
    
    has_app_colors = 'app_colors.dart' in content
    if not has_app_colors:
        content = add_import(content, "import 'package:lush/theme/app_colors.dart';")
    
    # Check for FontUtils
    if 'FontUtils' in content:
        content = add_import(content, "import 'package:lush/theme/app_text_styles.dart';")
        content = remove_import(content, 'font_utils.dart')
        content = replace_font_utils(content)
    
    content = replace_raw_colors(content)
    
    write_file(path, content)
    print(f"✅ Migrated link_google_account_screen.dart")

def migrate_reset_password_mobile_screen():
    content, path = read_file('views/screens/reset_password_mobile_screen.dart')
    
    has_app_colors = 'app_colors.dart' in content
    if not has_app_colors:
        content = add_import(content, "import 'package:lush/theme/app_colors.dart';")
    
    # Check for FontUtils
    if 'FontUtils' in content:
        content = add_import(content, "import 'package:lush/theme/app_text_styles.dart';")
        content = remove_import(content, 'font_utils.dart')
        content = replace_font_utils(content)
    
    content = replace_raw_colors(content)
    
    write_file(path, content)
    print(f"✅ Migrated reset_password_mobile_screen.dart")

def migrate_dashboard():
    content, path = read_file('views/screens/dashboard.dart')
    
    # Already has app_colors and app_text_styles imported
    # Remove theme.dart import
    content = remove_import(content, 'theme.dart')
    
    # Replace LushTheme references
    content = replace_lush_theme(content)
    
    # Replace raw Colors references
    content = replace_raw_colors(content)
    
    write_file(path, content)
    print(f"✅ Migrated dashboard.dart")

def migrate_address_screen():
    content, path = read_file('views/screens/address_screen.dart')
    
    # Check what's needed
    if 'AppColors' not in content:
        content = add_import(content, "import 'package:lush/theme/app_colors.dart';")
    
    if 'FontUtils' in content:
        content = remove_import(content, 'font_utils.dart')
        content = add_import(content, "import 'package:lush/theme/app_text_styles.dart';")
        content = replace_font_utils(content)
    
    content = replace_raw_colors(content)
    
    write_file(path, content)
    print(f"✅ Migrated address_screen.dart")

# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("🚀 Starting migration of all remaining files...\n")
    
    migrate_menu()
    migrate_notifications()
    migrate_order_history_page()
    migrate_login_page()
    migrate_phone_login_screen()
    migrate_reset_password_email_screen()
    migrate_text_utils()
    migrate_forgot_password_screen()
    migrate_day_wise_schedule_screen()
    migrate_delete_account_screen()
    migrate_link_google_account_screen()
    migrate_reset_password_mobile_screen()
    migrate_dashboard()
    migrate_address_screen()
    
    print("\n🎉 All migrations complete! Run 'flutter analyze' to check for errors.")
