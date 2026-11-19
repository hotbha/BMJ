# Deployment Parity Report

**Date:** 2026-11-19 · **Method:** read-only (git queries, `sha256sum`, `docker inspect`, `docker exec`)
**Host:** `api.bookmyjuice.co.in` · **Verified build:** `865fb16`

---

## Verdict

### **A — VPS matches GitHub**

The running container holds a JAR that is **byte-identical** to the artefact built from the current
GitHub `main`. Every deployment artefact on the server is content-identical to the committed copy.
**No redeployment is necessary.**

Evidence chain, in the order it was established:

1. Local `main` and GitHub `main` are the same commit, and the working tree is clean.
2. The JAR in `target/` was built from that clean tree → `bd559ef8…8049dc`.
3. The VPS `app.jar` and the container's `/app/app.jar` are **both** `bd559ef8…8049dc`.
4. Therefore the running binary is the one produced from GitHub HEAD.

---

## 1. GitHub HEAD (`bookmyjuice/bmjServer`)

| Item | Value |
|---|---|
| Branch | `main` |
| **GitHub HEAD** (`git ls-remote origin main`) | **`865fb168d211102995a06ae702d8e49be09fd5b3`** |
| Local HEAD | `865fb168d211102995a06ae702d8e49be09fd5b3` |
| Tracking | `## main...origin/main` — in sync |
| Working tree | **clean** (no modified, no untracked) |

Commit `865fb16` = `fix(security): refuse to start without webhook credentials`; its parents are
`fd07e48` (400 for malformed payloads), `00e2a19` (3 subscription handlers), `051ee6b` (identity
self-heal).

## 2. VPS deployed build

| Item | Value |
|---|---|
| `/home/bmj/bmj/app.jar` | **`bd559ef8d5282444134943c3b9b28ffca3f012e3b7aa422aa22f1dd81b8049dc`** |
| Size | 64,167,585 bytes |
| Previous build kept for rollback (`app.jar.prev`) | `ac69f64898ddc98f408bb2162449712b0fad0d901ab96fa5682c0011004bbb11` (= `7975aeb`) |

## 3. Running container build

| Item | Value |
|---|---|
| Container | `bmj-api` (`Up`, restarts=0) |
| `/app/app.jar` inside the container | **`bd559ef8d5282444134943c3b9b28ffca3f012e3b7aa422aa22f1dd81b8049dc`** |
| Image | `bmj-backend:vps` = `sha256:c484fca5176c76f5c32c73f328a65fcbdf687dd34f5b4918c622fc1d452e42af` |
| Image built | `2026-11-19T13:45:24Z` |
| Port binding | `127.0.0.1:8080` only (nginx fronts it) |

Host JAR = container JAR = locally built JAR = one hash.

**Content check:** the artefact contains the classes introduced by the most recent commits —
`WebhookEventCoverage`, `WebhookPayloadValidationFilter`, `CustomerIdentityResolver`,
`IdentityLinker`, `WebhookRetryService`, `DriftDetectionService` — so it is not an older build that
merely reports a matching version string.

## 4. Deployment artifacts

| Artefact | VPS sha256 (16) | Local sha256 (16) | Verdict |
|---|---|---|---|
| `docker-compose.prod.yml` | `eac3d0cf2b45189a` | `e47755d53eb065ac` → LF-normalised `eac3d0cf2b45189a` | **identical (EOL only)** |
| `Dockerfile.runtime` | `8666a281cc3d4a6e` | `8666a281cc3d4a6e` | **exact** |
| `bmj-stack.service` | `3fc08a8a8dd39b12` | `d5c591d0beadacce` → LF `3fc08a8a8dd39b12` | **identical (EOL only)** |
| `apply-nginx.py` | `31997a6d4f7ca95b` | `31997a6d4f7ca95b` | **exact** |
| `install-services.sh` | `5f2af6c7f484449f` | `9f3bdbaccbcd1685` → LF `5f2af6c7f484449f` | **identical (EOL only)** |
| `fix-env.sh` | `f6c4ebb46e9ef01a` | `798ea4be51f83c22` → LF `f6c4ebb46e9ef01a` | **identical (EOL only)** |

**Why four differ on the raw hash:** the deployment procedure runs `sed -i 's/\r$//'` on the server to
strip Windows line endings before use. Converting the local copies the same way reproduces the VPS hash
**exactly**, so no content drift exists — this was verified by comparison, not assumed.

`docker compose --env-file .env -f docker-compose.prod.yml config --quiet` → **valid**.

Files present on the server that are intentionally *not* in git: `.env` (secrets, mode 600),
`.env.bak-*` (key-rotation backups), `app.jar`, `app.jar.prev`, `deploy.log`, `rebuild.log`.

## 5. `.env` fingerprint (hash only, no values)

| Item | Value |
|---|---|
| sha256 (16) | **`324d5f7dc45d6174`** |
| Lines | 12 |
| Mode | `600` (owner read/write only) |
| In git | **no** — correctly untracked |

The file holds the twelve required keys (`DB_*`, `CHARGEBEE_SITE`, `CHARGEBEE_API_KEY`,
`WEBHOOK_USERNAME`, `WEBHOOK_PASSWORD`, `ADMIN_USER`, `ADMIN_PASSWORD`, `JWT_SECRET`,
`MAIL_PASSWORD`). One caveat carried over from `POST_DEPLOYMENT_SYNC_REPORT.md` §9: `WEBHOOK_PASSWORD`
still holds the pre-rotation value, so the fingerprint above encodes a value Chargebee no longer sends.
That is a **configuration** mismatch, not a code/deployment mismatch, and does not affect parity.

## 6. Documentation artifacts (`hotbha/BMJ`)

| Item | Value |
|---|---|
| Branch | `feat/v1-launch-freeze` |
| HEAD (local) | **`931960ca90b0e12cf54275d0063aed3af8a3727e`** |
| HEAD (remote) | `931960ca90b0e12cf54275d0063aed3af8a3727e` — in sync |
| Backend pointer recorded in the docs repo | `160000 commit 865fb168…` — **the deployed commit** |
| Flutter pointer recorded | `160000 commit e3a1f8f…` (app material work remains uncommitted by design) |

Documentation / deployment commits relevant to this build:

| Commit | Content |
|---|---|
| `931960c` | `docs(sync): post-deployment validation of the live synchronisation system` |
| `7d57e8a` | `docs(deploy): verification report for build 865fb16 on the VPS` |
| `bd95610` | `docs(status): record the sync implementation` + backend pointer bump |
| `7033680` | `docs(chargebee): live account audit, sync design set, investigation record` |
| `86940ca` | `docs(deploy): VPS deployment runbook, webhook activation checklist and deploy artifacts` |

## 7. Verdict detail

| Question | Answer |
|---|---|
| Does the VPS run the commit GitHub has? | **Yes** — `bd559ef8…` is the artefact built from `865fb16`, and GitHub HEAD is `865fb16` |
| Is the VPS behind GitHub? | **No** — zero commits between the deployed build and `main` |
| Does the VPS contain untracked local changes? | **No code changes.** Only expected runtime state: `.env`, `.env.bak-*`, `app.jar.prev`, `deploy.log`, `rebuild.log` |
| Are the deployment artefacts the committed ones? | **Yes** — 2 exact, 4 identical after line-ending normalisation |
| Is the docs repo pinned to the deployed backend? | **Yes** — gitlink = `865fb16` |

### Redeployment is unnecessary.

Nothing needs to be rebuilt, uploaded or restarted for parity reasons. The only outstanding change on
the server is the `WEBHOOK_PASSWORD` value discussed above, which is a configuration edit in `.env`
plus a container restart — not a deployment.

## 8. Observations for future deployments

1. **The JAR carries no provenance metadata.** There is no `git.properties` or
   `META-INF/build-info.properties` in the artefact, so "which commit is this jar?" can only be
   answered by hash comparison against a known build. Adding `git-commit-id-maven-plugin` would make
   the artefact self-identifying (`/actuator/info` could then expose the commit).
2. **Windows line endings leak into the deployed artefacts.** Four files needed `sed -i 's/\r$//'`
   on the server, which makes byte-comparison against the repo fail until normalised. Committing these
   files with LF endings (or adding a `.gitattributes` rule) would make parity checks a single
   `sha256sum` comparison.
3. **`app.jar.prev` is the rollback asset** and is currently the `7975aeb` build. It should be
   refreshed whenever a new build is accepted, otherwise the rollback target drifts further from
   HEAD.

