with open("lush/lib/views/screens/forgot_password_screen.dart","r",encoding="utf-8") as f:
    c=f.read()
print("FontUtils:" + str(c.count("FontUtils")))
print("Has import:" + str("font_utils" in c))
