"""Compare local deploy/ artefacts with the VPS copies, ignoring line endings.

For each file: hash of the file as-is, and hash after CRLF -> LF normalisation.
If the normalised local hash equals the VPS hash, the content is identical and only the
line endings differ (the server ran `sed -i 's/\\r$//'` on some of them).
"""
import hashlib
import pathlib
import sys

LOCAL = pathlib.Path(r"X:\BMJ\deploy")

# hashes measured on the VPS (full sha256, first 16 chars shown in the report)
VPS = {
    "docker-compose.prod.yml": "eac3d0cf2b45189a",
    "Dockerfile.runtime": "8666a281cc3d4a6e",
    "bmj-stack.service": "3fc08a8a8dd39b12",
    "apply-nginx.py": "31997a6d4f7ca95b",
    "install-services.sh": "5f2af6c7f484449f",
    "fix-env.sh": "f6c4ebb46e9ef01a",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


ok = True
for name, vps_hash in VPS.items():
    path = LOCAL / name
    if not path.exists():
        print(f"{name:<26} MISSING LOCALLY")
        ok = False
        continue
    raw = path.read_bytes()
    norm = raw.replace(b"\r\n", b"\n")
    h_raw, h_norm = sha(raw), sha(norm)
    verdict = ("EXACT" if h_raw.startswith(vps_hash)
               else "EOL-ONLY" if h_norm.startswith(vps_hash)
               else "CONTENT-DIFFERS")
    if verdict == "CONTENT-DIFFERS":
        ok = False
    print(f"{name:<26} vps={vps_hash}  local_raw={h_raw[:16]}  local_lf={h_norm[:16]}  -> {verdict}")

print()
print("all identical after EOL normalisation" if ok else "AT LEAST ONE FILE HAS REAL CONTENT DRIFT")
sys.exit(0 if ok else 1)
