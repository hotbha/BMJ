# DEPLOYMENT_RUNBOOK.md

**Scope:** how to take the frozen `x:\BMJ` tree to a production URL and a customer-installable APK, in order, with a verification step after each stage.
**Companions:** `PRODUCTION_READINESS_REPORT.md` (what is broken and why — read §2 before starting), `B5_SMOKE_TEST_PLAN.md` (the gate), `BMJ_LAUNCH_CHECKLIST.md` (the record).
**Audience:** whoever runs this should be able to follow it without reading the source.

> **Read this first.** The tree cannot be deployed successfully as it stands. `PR-1` makes a CI build ship without the catalog; `PR-12` means the service would boot on dev defaults; `PR-17` means the catalog ships without prices. §3 exists to fix those **before** anything is shipped.

---

## 0. Prerequisites

| # | Requirement | Notes |
| :--: | :--- | :--- |
| 1 | A VPS (Ubuntu) with a public IP and root/sudo SSH | this is `PR-4`; nothing here can run without it |
| 2 | A **decided** production domain | pick one — `docs/` currently disagrees (`.com` vs `.co.in`) |
| 3 | DNS `A` record → the VPS IP | verify with `Resolve-DnsName <host>` before provisioning; TLS issuance fails without it |
| 4 | A Chargebee **test** site key for the smoke, live key only at cutover | treat the live key as a one-way door |
| 5 | JDK 21 + Docker available locally if you want to smoke before deploying | per `B5_SMOKE_TEST_PLAN.md` §2 |
| 6 | Repository secrets `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY` | consumed by `.github/workflows/deploy-vps.yml`; `H12` in `docs/HUMAN_INTERVENTION_REQUIRED.md` |
| 7 | An Android upload keystore (or an explicit sideload-only sign-off) | `PR-2` — a Product decision, not a technical one |

---

## 1. One-time host provisioning

```bash
ssh root@<VPS_HOST>
git clone <repo-url> /opt/bmj-src && cd /opt/bmj-src
sudo bash ops/provision-vps.sh
```

`provision-vps.sh` creates the `bmj` user, the app directory, the systemd unit, nginx and the `.env` template. **Two things it does not do, both of which must be done by hand:**

| Gap | Why it matters | Do this |
| :--- | :--- | :--- |
| **Phase 8's Let's Encrypt block is commented out** (`PR-5`) | the site serves `http://` only — bearer tokens in clear text | uncomment it and run `certbot --nginx -d <host>`, or run `certbot` manually |
| **No profile is set anywhere** (`PR-12`) | the service boots on `application.properties` defaults: `ddl-auto=update` mutates the live schema, `useSSL=false` sends DB traffic in clear | apply §3.1 below |

Verify before moving on:

```bash
systemctl status bmj-backend            # active (running)
curl -s localhost:8080/api/health       # {"status":"UP", ...}
sudo nginx -T | grep -E "listen (80|443)|ssl_certificate"
```

---

## 2. Secrets that must exist in `/home/bmj/bmj/.env`

The systemd unit reads `EnvironmentFile=/home/bmj/bmj/.env`, so **the file is the source of truth** — not `.env` in the repo, and not `spring.dotenv.location`.

| Variable | Notes |
| :--- | :--- |
| `DB_URL`, `DB_USERNAME`, `DB_PASSWORD`, `DB_NAME` | a dedicated MySQL user, not `root`; **treat `${VAR}` literally — plain `java -jar` does not expand `${DB_USERNAME}` inside the URL**, systemd's `EnvironmentFile` does |
| `JWT_SECRET` | rotate before launch (`PR-11`); rotating later invalidates every live token |
| `CHARGEBEE_SITE`, `CHARGEBEE_API_KEY` | test key until cutover |
| `WEBHOOK_*`, `MAIL_*`, `REDIS_*`, `SENTRY_*` | as applicable |
| **`SPRING_PROFILES_ACTIVE=prod`** | **currently missing everywhere — see §3.1** |

```bash
sudo chown bmj:bmj /home/bmj/bmj/.env
sudo chmod 600 /home/bmj/bmj/.env
sudo -u bmj test -r /home/bmj/bmj/.env && echo readable       # must print readable
```

---

## 3. The launch commit — do this **before** deploying

Small, ordered, and each item is verifiable.

### 3.1 Activate the `prod` profile (`PR-12`)

In the systemd unit inside `ops/provision-vps.sh`, and on any already-provisioned host, add:

```ini
Environment=SPRING_PROFILES_ACTIVE=prod
```

Then on the host: `sudo systemctl daemon-reload && sudo systemctl restart bmj-backend`, and confirm:

```bash
journalctl -u bmj-backend --since '-5 min' | grep -i "profile"
# expect: The following 1 profile is active: "prod"
```

**Expect the first boot under `prod` to fail if the schema drifted** — `ddl-auto=validate` will refuse to start rather than mutate the database. That refusal is the feature; fix the schema (`PR-13`), do not weaken the setting.

### 3.2 Track the untracked source (`PR-1`)

```powershell
git -C bmjServer add src/main/java/com/bookmyjuice/controllers/CatalogController.java `
                       src/main/java/com/bookmyjuice/controllers/UserProfileController.java
git -C bmjServer status --porcelain    # must show both as 'A ', not '??'
```

Verify a clean checkout really builds the catalog — this is the difference between a working and a 404 storefront:

```powershell
git clone bmjServer (Get-ChildItem $env:TEMP -Directory).FullName\clone-check
# then confirm clone-check/src/main/java/com/bookmyjuice/controllers/CatalogController.java exists
```

### 3.3 The remaining one-liners

| Item | Change |
| :--- | :--- |
| `PR-7` | `bmjServer/pom.xml` version `0.0.2-SNAPSHOT` → `1.0.0` |
| `PR-10` | keep `app.jar` deleted; add it to `.gitignore` |
| `PR-8` | delete `TestController`, or gate it `@Profile("!prod")` |
| `PR-14` | `UserProfileController` must not serialise the raw `User` entity (return a DTO / `@JsonIgnore` the secrets) |
| `PR-17` | `ItemService.java:937` `ItemPrice.list().limit(200)` → `.limit(100)` **and** paginate it like `:910-923` does for items |
| `PR-18` | **Not a code change — a Chargebee data change:** create one `ItemPrice` per `bmj-item-*` item (**write; needs go-ahead**, `D4`/`D6`). Without it `PR-17` still ships `"prices":[]`: the site's 314 ItemPrices cover **0** of the 15 catalog items (report §3.5) |
| `PR-16` | an upstream failure with an empty cache must not present as `200 []` — return an error/degraded signal |

Stage these as **one** commit so the tag points at the configuration that was actually smoked.

---

## 4. Build and publish the backend

Replicate CI exactly, so local and CI artifacts are comparable:

```powershell
cd x:\BMJ\bmjServer
.\mvnw.cmd -o -q -DskipTests package
Get-ChildItem target\*.jar | Select-Object Name,Length,LastWriteTime
Get-FileHash target\com.bookmyjuice.bmjServer-1.0.0.jar -Algorithm SHA256
```

**Record that SHA-256** — it is what `B5_SMOKE_TEST_PLAN.md` §3.3/D1 compares against the host.

Deployment itself is the workflow (do not hand-copy JARs):

```powershell
gh workflow run deploy-vps.yml --ref main
gh run watch
```

The workflow builds from source, uploads `bmjServer-<sha>.jar`, moves it to `/home/bmj/bmj/current.jar`, restarts `bmj-backend` and re-checks health. On the host, confirm the restart really installed the new bytes:

```bash
sha256sum /home/bmj/bmj/current.jar
systemctl show bmj-backend -p ExecStart
```

---

## 5. Build the release APK — the `--dart-define` is mandatory

`lush/lib/config/api_config.dart` reads `String.fromEnvironment('API_BASE_URL')` with **no default**, so an APK built without the define points at the *device's own* loopback and fails every request (`PR-3`).

```powershell
cd x:\BMJ\lush
flutter clean
flutter build apk --release `
  --dart-define=API_BASE_URL=https://<your-host>
```

For a smaller download, or Play delivery:

```powershell
flutter build apk --release --split-per-abi --dart-define=API_BASE_URL=https://<your-host>
flutter build appbundle --release           --dart-define=API_BASE_URL=https://<your-host>
```

### Verify the define is actually inside the artifact

Do not trust the build log — read the binary:

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem
$apk = 'build\app\outputs\flutter-apk\app-release.apk'
$zip = [IO.Compression.ZipFile]::OpenRead((Resolve-Path $apk))
$e   = $zip.Entries | Where-Object { $_.FullName -like 'lib/*/libapp.so' } | Select-Object -First 1
$ms  = New-Object IO.MemoryStream; $e.Open().CopyTo($ms); $zip.Dispose()
$text = [Text.Encoding]::ASCII.GetString($ms.ToArray())
$text.Contains('your-host')        # must be True
```

If that prints `False`, the APK is unbindable and will present as "app cannot load". Rebuild before shipping.

**Also required at the HTTPS cutover:** set `usesCleartextTraffic="false"` in `lush/android/app/src/main/AndroidManifest.xml` and rebuild. Leaving it `true` in a shipped build permits plaintext fallback, which defeats `PR-5`.

---

## 6. Signing the release APK (`PR-2`)

As shipped, `lush/android/app/build.gradle.kts:36-42` signs release builds with the **debug** keystore. Play rejects that, and the debug key is not yours — so switching later breaks the update path for anyone already installed. Two paths:

### 6a. A real upload key (recommended if the app will ever be distributed widely)

```powershell
keytool -genkeypair -v -keystore x:\BMJ\keys\bmj-upload.jks `
  -alias bmj-upload -keyalg RSA -keysize 4096 -validity 10950 `
  -storetype JKS
```

Create `lush/android/key.properties` (**never commit it**):

```properties
storePassword=<store-password>
keyPassword=<key-password>
keyAlias=bmj-upload
storeFile=../../keys/bmj-upload.jks
```

Replace the `release` block in `build.gradle.kts`:

```kotlin
import java.util.Properties
import java.io.FileInputStream

val keystoreProperties = Properties().apply {
    val f = rootProject.file("key.properties")
    if (f.exists()) f.inputStream().use { load(it) }
}

android {
    signingConfigs {
        if (keystoreProperties.isNotEmpty()) {
            create("release") {
                keyAlias      = keystoreProperties["keyAlias"] as String
                keyPassword   = keystoreProperties["keyPassword"] as String
                storeFile     = file(keystoreProperties["storeFile"] as String)
                storePassword = keystoreProperties["storePassword"] as String
            }
        }
    }
    buildTypes {
        release {
            signingConfig = signingConfigs.findByName("release")
                ?: signingConfigs.getByName("debug")   // still explicit, still logged
        }
    }
}
```

Add to `lush/android/.gitignore`:

```
key.properties
*.jks
*.keystore
```

Verify what actually signed the artifact:

```powershell
& "$env:LOCALAPPDATA\Android\Sdk\build-tools\<ver>\apksigner.bat" verify --print-certs `
  build\app\outputs\flutter-apk\app-release.apk
```

The certificate DN must be **yours**, not `CN=Android Debug`. **Back the keystore up offline** — losing it means no updates to installed users, ever.

### 6b. Sideload-only (acceptable for V1 named first customers, must be recorded)

Sign nothing, distribute the debug-signed APK directly, and write into `BMJ_LAUNCH_CHECKLIST.md`: *"V1 shipped debug-signed; Play distribution deferred; installing the real-key build later requires uninstall."* Do not let this remain an unstated assumption.

**Either way:** whoever installs a debug-signed build cannot be upgraded in place afterwards. That is the cost of 6b and the reason to prefer 6a.

---

## 7. Deploy, then verify (never assume)

```powershell
# 1. the gate
powershell -File x:\BMJ\ops\smoke_test.ps1 -BaseUrl "https://<your-host>" -Seeded

# 2. the flow a customer actually performs, end to end, on the real APK:
#    install -> open -> catalog lists WITH PRICES -> add to cart -> checkout ->
#    Chargebee payment page -> paid -> order appears under "my orders"
```

Host-side confirmation:

```bash
systemctl status bmj-backend --no-pager
journalctl -u bmj-backend --since '-15 min' | grep -iE "error|exception|denied" | tail -40
sudo nginx -t
```

**Only after §7 passes** close `B5` and record the evidence (§5 of the smoke plan).

---

## 8. Rollback

The service always runs `/home/bmj/bmj/current.jar`, so rollback is a file swap plus a restart — with one trap: **if `ddl-auto=validate` is active and the previous release expects an older schema, the old JAR will refuse to boot.** Decide the schema story (`PR-13`) before you need a rollback, not during one.

```bash
sudo systemctl stop bmj-backend
sudo cp /home/bmj/bmj/current.jar  /home/bmj/bmj/current.jar.failed   # keep the evidence
sudo cp /home/bmj/bmj/previous.jar /home/bmj/bmj/current.jar
sudo systemctl start bmj-backend
curl -s localhost:8080/api/health
```

Retain at least one previous known-good JAR on the host (`previous.jar`) as part of every deploy. For a database-affecting release, take a dump **before** deploying:

```bash
mysqldump --single-transaction --routines --triggers -u"$DB_USERNAME" -p "$DB_NAME" \
  | gzip > ~/bmj-predeploy-$(date +%Y%m%d-%H%M).sql.gz
```

---

## 9. Hardening and cutover

| # | Action | Item |
| :--: | :--- | :--- |
| 1 | TLS live; `http` → `https` redirect verified | `PR-5` |
| 2 | `usesCleartextTraffic="false"`; APK rebuilt with a real certificate | `PR-5` |
| 3 | Rotate Chargebee key, `JWT_SECRET` and the test account password; update `.env` | `PR-11` |
| 4 | CORS narrowed from `*` to the real origins | `PR-6` |
| 5 | Firewall: expose only 80/443 (and your SSH port); MySQL **not** public | — |
| 6 | `chargebee.sync.enable-startup-sync` decided deliberately for production | — |
| 7 | Log retention/rotation in place; no secrets in logs (`grep` for them — §3.3/D6) | — |
| 8 | Alert on `/api/health` **and** on the empty-catalog path | `PR-16` |
| 9 | Sentry (or equivalent) receiving real events from the APK | — |

**Order matters for #2:** flip cleartext off only **after** TLS works, or you will ship an app that cannot reach the backend at all.

---

## 10. Closing the launch

```powershell
# all three repos clean, then:
git -C bmjServer  tag -a v1.0.0-launch -m "V1 launch - backend"
git -C lush       tag -a v1.0.0-launch -m "V1 launch - app"
git -C .          tag -a v1.0.0-launch -m "V1 launch - docs/ops"
git push --tags
```

Before tagging, confirm the record is honest:

- [ ] `git status` clean in all three repos (working-tree artefacts removed, not ignored silently)
- [ ] Every gate in `PRODUCTION_READINESS_REPORT.md` §4 is green, or **explicitly waived in writing** with a name against it
- [ ] The deployed JAR's SHA-256 matches the tagged build
- [ ] `B5` evidence pasted, with the base URL and date
- [ ] The APK's `--dart-define` and hash recorded
- [ ] Every waiver/decision (`D1`-`D7` in the report) is written down, with the person accountable

**Anything green-by-assumption becomes a production incident.** The three failure modes this runbook exists to prevent — a missing catalog controller (`PR-1`), an inactive `prod` profile (`PR-12`) and a pricelist that arrives empty (`PR-17`) — all present as a *working* system with a green health check.