# AAB Release Report

> **Date:** 2026-10-30 · **Command:** `flutter build appbundle --release --dart-define=API_BASE_URL=https://api.bookmyjuice.example`

## 1. Artifacts

| Artifact | Path | Size | Build time |
| :--- | :--- | ---: | ---: |
| **Android App Bundle** | `build\app\outputs\bundle\release\app-release.aab` | **82.4 MB** | 43.9 s (`bundleRelease`, incremental) |
| Release APK (same signing config) | `build\app\outputs\flutter-apk\app-release.apk` | 88.6 MB | 28.9 s |

Version shipped: `1.0.0+1` · `applicationId com.bookmyjuice.app` · `minSdk 24` · `targetSdk 36`.

## 2. Signing

```
jarsigner -verify -verbose -certs app-release.aab
→ X.509, CN=BookMyJuice, OU=Beta, O=BookMyJuice, L=Hyderabad, ST=Telangana, C=IN
```

```
apksigner verify --print-certs app-release.apk
→ V2 Signer:    CN=BookMyJuice, OU=Beta, O=BookMyJuice, L=Hyderabad, ST=Telangana, C=IN
  SHA-256:      b58e6f520d7f4dcbcacebcbfdfdb9f5d87a865db812a7021cd4f709c174df006
  SHA-1:        bd338422d9985ad51d8538935e73ca32c2126bdf
```

Not the debug key: the emulator rejected an in-place update with
`INSTALL_FAILED_UPDATE_INCOMPATIBLE: Existing package com.bookmyjuice.app signatures do not match`,
which is the platform confirming the new certificate differs from the previously installed debug-signed build. Uninstalling and reinstalling the release APK then succeeded.

## 3. Installability

| Step | Result |
| :--- | :--- |
| `adb uninstall com.bookmyjuice.app` | Success (removed the old debug-signed install) |
| `adb install -r app-release.apk` | **Success** |
| `adb shell am start -n com.bookmyjuice.app/.MainActivity` | Started; `mCurrentFocus=com.bookmyjuice.app/.MainActivity` after 12 s |
| First-run experience | Android 14 notification permission dialog rendered: “Allow BookMyJuice to send you notifications?” with Allow / Don’t allow |
| After tapping Allow | `POST_NOTIFICATIONS: granted=true` |

An `.aab` is not directly installable by design (it is a publishing format); installability is therefore proven with the APK produced from the **same** signing config and the same `--dart-define`. When the bundle is uploaded, Play regenerates split APKs from it.

## 4. Permissions in the shipped manifest

```
aapt2 dump permissions app-release.apk
package: com.bookmyjuice.app
uses-permission: android.permission.INTERNET              ← added this sprint (was missing in release)
uses-permission: android.permission.POST_NOTIFICATIONS    ← added this sprint
uses-permission: android.permission.ACCESS_NETWORK_STATE
uses-permission: android.permission.WAKE_LOCK
uses-permission: android.permission.VIBRATE
uses-permission: com.google.android.providers.gsf.permission.READ_GSERVICES
uses-permission: com.google.android.finsky.permission.BIND_GET_INSTALL_REFERRER_SERVICE
uses-permission: com.google.android.gms.permission.AD_ID
uses-permission: android.permission.ACCESS_ADSERVICES_ATTRIBUTION
```

Runtime grant state after first launch: `INTERNET: granted=true`, `POST_NOTIFICATIONS: granted=true`.

`AD_ID` comes in with Firebase Analytics — it must be declared in the Play **data safety** form.

## 5. Size

82.4 MB bundle is large for a juice app and comes from bundled fonts (Plus Jakarta, Inter, Font Awesome ×3, Material icons) plus the Firebase/patrol dependency set. Play delivery splits by ABI/density so the install size will be far below the universal 88.6 MB APK. If the beta download size matters, the cheapest wins are auditing the bundled font families and excluding unused Font Awesome variants — no design change required.

## 6. Notes / caveats

- The build used the **placeholder** API host `https://api.bookmyjuice.example`; it must be replaced with the real beta host (see `PRODUCTION_ENDPOINT_AUDIT.md` §5) before upload.
- `key.properties` points at `X:/BMJ/_secrets/bmj-upload.jks` (outside the repo). CI must supply its own.
- Kotlin compiler warnings appear from the `patrol` plugin (`portStr == null` always false). Non-fatal, third-party.
- First cold release build took 754.5 s; incremental AAB builds are ~44 s. Budget CI accordingly (Gradle cache).
