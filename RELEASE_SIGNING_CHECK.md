# Release Signing Check

> **Date:** 2026-10-30 · **Scope:** Android release signing only · **No UI or logic changes.**

## 1. What the repository shipped before this pass

| Item | Finding | Severity |
| :--- | :--- | :--- |
| Release signing config | `android/app/build.gradle.kts` had `signingConfig = signingConfigs.getByName("debug")` with a `// TODO: Add your own signing config` — **every release build was debug-signed** | 🔴 blocker |
| `key.properties` | absent (`android/key.properties` and repo root both missing) | 🔴 blocker |
| `keystore_name.jks` | **tracked in git**, PKCS12, alias `your_alias`, created 2025-02-08, **opens with password `android`** | 🔴 blocker |
| `clientkeystore` | **tracked in git**, PKCS12, alias `client`, created 2025-02-08, **opens with password `android`** | 🔴 blocker |
| `.gitignore` | contained no rule for `*.jks` or `key.properties` | 🟡 |

Both keystores are extractable from the repository by anyone with read access, with a publicly known password. They must be treated as **compromised**: remove from git, never reuse, and generate fresh keys.

## 2. What was changed

| # | Change | File |
| :-: | :--- | :--- |
| 1 | Generated a new 4096-bit RSA upload key, validity 10,000 days, alias `bmj-upload`, stored **outside the repository** at `X:\BMJ\_secrets\bmj-upload.jks` | new file (not in git) |
| 2 | Wrote `android/key.properties` (gitignored) with `storeFile` / `storePassword` / `keyAlias` / `keyPassword`; the password is a generated 28-character random string and is **not** reproduced in any document | `android/key.properties` |
| 3 | Wired real release signing with a safe fallback: if `key.properties` is missing the build falls back to debug signing, so contributors are not blocked | `android/app/build.gradle.kts` |
| 4 | Added `*.jks`, `key.properties`, `*.err` to `.gitignore` | `.gitignore` |

The Gradle diff:

```kotlin
// top of android/app/build.gradle.kts
import java.io.FileInputStream
import java.util.Properties

val keystoreProperties = Properties()
val keystorePropertiesFile = rootProject.file("key.properties")
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(FileInputStream(keystorePropertiesFile))
}

// inside android { }
signingConfigs {
    if (keystorePropertiesFile.exists()) {
        create("release") {
            keyAlias = keystoreProperties["keyAlias"] as String
            keyPassword = keystoreProperties["keyPassword"] as String
            storeFile = file(keystoreProperties["storeFile"] as String)
            storePassword = keystoreProperties["storePassword"] as String
        }
    }
}
buildTypes {
    release {
        signingConfig = if (keystorePropertiesFile.exists()) {
            signingConfigs.getByName("release")
        } else {
            signingConfigs.getByName("debug")   // contributor fallback only
        }
    }
}
```

### Bug found and fixed during the first attempt

The first AAB build failed with:

```
Execution failed for task ':app:validateSigningRelease'.
> Keystore file 'X:\BMJ\lush\android\app\X:BMJ_secretsbmj-upload.jks' not found
```

Cause: `java.util.Properties` treats `\` as an escape character, so `X:\BMJ\_secrets\…` was collapsed. Fix: write the path with forward slashes (`X:/BMJ/_secrets/bmj-upload.jks`), which Gradle accepts on Windows. Worth knowing before anyone regenerates `key.properties`.

## 3. Verification (evidence)

| Check | Result | Evidence |
| :--- | :--- | :--- |
| Release keystore exists | ✅ | `X:\BMJ\_secrets\bmj-upload.jks`, alias `bmj-upload`, 4096-bit RSA, 10,000-day validity |
| Debug keystore not used for release | ✅ | AAB signer certificate is `CN=BookMyJuice, OU=Beta, O=BookMyJuice, L=Hyderabad, ST=Telangana, C=IN` — not `CN=Android Debug` |
| `key.properties` configured | ✅ | 4 keys present: `storeFile`, `storePassword`, `keyAlias`, `keyPassword` |
| Build produces a signed release artifact | ✅ | `flutter build appbundle --release` → `build\app\outputs\bundle\release\app-release.aab`, **82.4 MB**, Gradle `bundleRelease` 43.9 s |
| Signature is valid | ✅ | `jarsigner -verify -verbose -certs app-release.aab` reports the certificate above across entries |
| Release APK signs with the same key | ✅ | see `AAB_RELEASE_REPORT.md` (`apksigner verify --print-certs`) |

## 4. Actions still required by a human (cannot be automated safely)

1. **Remove the compromised keystores from git**: `git rm --cached keystore_name.jks clientkeystore` (and delete the files). They are in git history, so treat both keys as public forever.
2. **Back up** `X:\BMJ\_secrets\bmj-upload.jks` **and** the password from `android/key.properties` to a password manager. Losing them means losing the ability to update the app under this upload key.
3. **CI secret injection**: the runner must receive `key.properties` (or the four values) from a secret store, not from the repo.
4. **Play App Signing**: enrol the app; the file above then becomes the *upload* key and Google holds the app-signing key.
5. **Decide the key's fate**: this is a **beta upload key**. Keeping it as the production upload key is acceptable; rotating it later requires a Play "upload key reset" request.
