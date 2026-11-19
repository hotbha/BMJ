"""Idempotently add the BMJ API proxy to the nginx server block for
api.bookmyjuice.co.in.

Safety properties:
  * never touches any other server block (`server_name _` on port 80 is untouched);
  * makes a timestamped backup before writing;
  * exits 0 with "already present" if the location exists, so re-running is a no-op;
  * the caller must run `nginx -t` and only then reload.

Usage (as root):  python3 apply-nginx.py
"""
import datetime
import re
import shutil
import sys

TARGET = "/etc/nginx/sites-available/default"
ANCHOR = "server_name api.bookmyjuice.co.in;"
MARKER = "location /api/"

BLOCK = """
    # ---- BMJ API proxy (managed by deploy/apply-nginx.py) ----
    # 127.0.0.1:8080 only: the Spring Boot container is never exposed directly.
    location /api/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 10s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
        client_max_body_size 10m;
    }
    # ---- end BMJ API proxy ----
"""


def main():
    with open(TARGET, encoding="utf-8") as fh:
        text = fh.read()

    if MARKER in text:
        print("ALREADY_PRESENT: nginx already proxies /api/ - nothing to do")
        return 0

    anchor_match = re.search(re.escape(ANCHOR), text)
    if not anchor_match:
        print(f"ANCHOR_NOT_FOUND: '{ANCHOR}' is not in {TARGET}")
        return 3

    # Insert immediately after the server_name line of the 443 block.
    insert_at = text.find("\n", anchor_match.end())
    if insert_at == -1:
        print("ANCHOR_IS_LAST_LINE: refusing to guess")
        return 3

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = f"{TARGET}.bak-{stamp}"
    shutil.copy2(TARGET, backup)

    new_text = text[: insert_at + 1] + BLOCK + text[insert_at + 1 :]
    with open(TARGET, "w", encoding="utf-8") as fh:
        fh.write(new_text)

    print(f"INSERTED: proxy block added to {TARGET}")
    print(f"BACKUP: {backup}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
