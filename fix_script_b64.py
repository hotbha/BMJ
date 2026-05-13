with open("lush/lib/views/screens/forgot_password_screen.dart","r",encoding="utf-8") as f:
    c=f.read()

c = c.replace("import 'package:lush/utils/font_utils.dart';", "")

with open("lush/lib/views/screens/forgot_password_screen.dart","w",encoding="utf-8") as f:
    f.write(c)

print("done")