"""Read build metadata from inside a Spring Boot jar (read-only).

If the build embeds git.properties or META-INF/build-info.properties, the jar can be
tied to a commit without relying on file timestamps.
"""
import sys
import zipfile

JAR = sys.argv[1] if len(sys.argv) > 1 else \
    r"X:\BMJ\bmjServer\target\com.bookmyjuice.bmjServer-0.0.2-SNAPSHOT.jar"

WANTED = ("META-INF/build-info.properties", "BOOT-INF/classes/git.properties",
          "git.properties", "META-INF/MANIFEST.MF")

with zipfile.ZipFile(JAR) as z:
    names = z.namelist()
    print(f"entries: {len(names)}")
    found = [n for n in names if n in WANTED]
    if not found:
        print("no git/build info files embedded")
        print("marker classes present:",
              ", ".join(sorted(n for n in names if "WebhookEventCoverage" in n or
                               "WebhookPayloadValidationFilter" in n or
                               "CustomerIdentityResolver" in n)[:5]))
    for name in found:
        print(f"--- {name} ---")
        text = z.read(name).decode("utf-8", errors="ignore")
        for line in text.splitlines():
            if any(k in line.lower() for k in ("git.", "build.version", "build.time", "commit")):
                print("   ", line.strip())
