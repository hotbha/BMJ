# Phone Debug & Checkpoints Workflow

> **Test the Flutter app on your physical phone while debugging the Spring Boot backend with breakpoints ("checkpoints") running in Docker.**

---

## Overview

This workflow enables two things simultaneously:

1. **Flutter on your phone** — the app connects to the backend via your machine's LAN IP
2. **VS Code breakpoints in Java code** — the "Remote Attach" debugger connects to Docker's JDWP port 5005

The architecture looks like this:

```
Phone (Flutter App)
    │  HTTP requests ──> http://YOUR_MACHINE_IP:8080
    ▼
Your Machine (Windows)
    ├── Docker Container (Spring Boot Backend)
    │     ├── Port 8080 (API)
    │     └── Port 5005 (JDWP Debug)
    │
    └── VS Code Java Debugger
          └── Attaches to localhost:5005
                └── Breakpoints pause execution here
```

---

## Prerequisites

- [ ] Docker Desktop running (`docker ps` works)
- [ ] Android phone connected via USB **OR** on same WiFi network
- [ ] USB Debugging enabled on phone
- [ ] `adb devices` shows your phone (for USB connection)
- [ ] VS Code with **Extension Pack for Java** and **Flutter** extensions installed
- [ ] Phone and computer on the **same WiFi network** (for wireless debugging)

---

## Step-by-Step Workflow

### Step 1: Start Docker Services

```bash
# From the project root (x:\BMJ)
docker-compose up -d
```

This starts:
- `bmj-mysql` — database
- `bmj-redis` — cache
- `bmj-backend` — Spring Boot with JDWP debug port 5005 exposed

> Verify: `docker ps` should show all 3 containers running. The backend container shows port `0.0.0.0:5005->5005/tcp`.

---

### Step 2: Get Your Machine's LAN IP

**Option A — PowerShell script:**
```powershell
.\ops\find_active_ip.ps1
```
Output: `192.168.x.x`

**Option B — VS Code Task:**
1. `Ctrl+Shift+P` → "Tasks: Run Task"
2. Select **"Flutter: Show Detected IP"**
3. The IP will appear in the terminal pane in green

**Option C — npm script:**
```bash
npm run phone:ip
```

**Option D — Makefile:**
```bash
make phone-ip
```

> ⚠️ **Important:** If you see a `172.x.x.x` or `169.254.x.x` IP, that's not your LAN IP. Make sure you're connected to WiFi (not a VM network).

---

### Step 3: Attach VS Code Debugger to Docker (💡 Makes Checkpoints Work)

This is the **critical step** that enables breakpoints in your Java code.

1. Open the **Run and Debug** panel in VS Code (`Ctrl+Shift+D`)
2. From the configuration dropdown at the top, select **"Docker: Attach Debugger (Backend)"**
3. Click the green **Start Debugging** button (or press `F5`)

![Debug Config Dropdown](https://code.visualstudio.com/assets/docs/editor/debugging/debugging_dropdown.png)

**What happens:** VS Code connects to `localhost:5005`, which Docker forwards to the Spring Boot container's JDWP agent. The debugger is now attached — any breakpoint you set will be hit.

**To verify:**
- The bottom status bar turns orange (debug mode)
- The Debug toolbar appears with Continue/Step Over/Step Into buttons
- The DEBUG CONSOLE tab shows connected messages

> **Troubleshooting:** If you get "Connection refused" on port 5005, make sure Docker is running:
> ```bash
> docker ps | findstr bmj-backend
> docker logs bmj-backend --tail 20
> ```

---

### Step 4: Run Flutter on Your Phone

You have **3 options** — pick whichever is most convenient.

#### Option A: VS Code Launch Config (Recommended)

1. In the **Run and Debug** panel (`Ctrl+Shift+D`)
2. Select **"Flutter App (Phone Debug)"** from the dropdown
3. Click **Start Debugging** (F5)
4. VS Code will **prompt you to enter your machine's LAN IP** (the one from Step 2):
   ```
   Enter your machine's LAN IP address
   (run .\ops\find_active_ip.ps1 to get it)
   ┌──────────────────────────────────┐
   │ 192.168.1.100                    │
   └──────────────────────────────────┘
   ```
5. The Flutter app builds and launches on your phone with `API_BASE_URL=http://192.168.1.100:8080`

#### Option B: PowerShell Helper Script

```powershell
# From the project root
.\ops\build_flutter_for_phone.ps1
```

This auto-detects your IP and runs `flutter run` with the correct `--dart-define`.

For more options:
```powershell
.\ops\build_flutter_for_phone.ps1 -Port 8080        # Custom port
.\ops\build_flutter_for_phone.ps1 -UseEmulator       # For emulator (uses 10.0.2.2)
.\ops\build_flutter_for_phone.ps1 -RunOnly           # Just print the command, don't run
```

#### Option C: VS Code Task (Auto-Detected IP)

1. `Ctrl+Shift+P` → "Tasks: Run Task"
2. Select **"Flutter: Run on Phone (Debug)"**
3. The task auto-detects your IP and runs Flutter

---

### Step 5: Set Breakpoints and Test

1. Open any Java file (e.g., `bmjServer/src/main/java/.../controller/AuthController.java`)
2. Click in the **gutter** (left margin) next to a line number to set a breakpoint — a red dot appears
3. On your phone, use the Flutter app to trigger an API call (e.g., tap "Sign In")
4. When the backend hits your breakpoint:
   - VS Code highlights the line in yellow
   - Execution is **paused**
   - The **VARIABLES** pane shows local variables, method arguments, stack trace
   - You can inspect any variable with your mouse (hover)
5. Debug actions:
   - `F5` — Continue execution
   - `F10` — Step Over (next line in same method)
   - `F11` — Step Into (go into method call)
   - `Shift+F11` — Step Out (finish current method and return)
6. The API response flows back to the phone

---

## One-Click Everything: Compound Config

VS Code has a **compound** launch config that does Step 3 + Step 4 in one click:

1. In the **Run and Debug** panel, select **"Full Stack (Docker + Phone Debug)"**
2. Press `F5`
3. Enter your machine's LAN IP when prompted
4. VS Code:
   - ✅ Attaches Java debugger to Docker port 5005
   - ✅ Runs Flutter on your phone with the correct IP
   - ✅ All in a single session

---

## Reference: Commands & Scripts

### Quick Commands

| What | Command |
|------|---------|
| Start Docker | `docker-compose up -d` |
| Stop Docker | `docker-compose down` |
| View backend logs | `docker-compose logs -f backend` |
| Find your IP | `.\ops\find_active_ip.ps1` |
| Run Flutter on phone | `.\ops\build_flutter_for_phone.ps1` |
| Show debug command | `npm run phone:debug` |
| Build APK for phone | `npm run phone:build` |
| Show IP via npm | `npm run phone:ip` |
| Show IP via Makefile | `make phone-ip` |
| Debug instructions via Makefile | `make phone-debug` |

### npm Scripts (from `package.json`)

```bash
npm run phone:debug      # Print flutter run command with your IP
npm run phone:build      # Auto-detect IP and build/run for phone
npm run phone:ip          # Show your machine's LAN IP
```

### Makefile Targets (from `Makefile`)

```bash
make phone-ip              # Show your machine's LAN IP
make phone-debug           # Print full debug instructions with your IP
```

---

## Configuration Files Reference

These files have been updated to support the phone debug workflow:

| File | What Changed |
|------|-------------|
| `.vscode/launch.json` | Added `"Docker: Attach Debugger (Backend)"` (Remote Attach on port 5005), `"Flutter App (Phone Debug)"` with dynamic IP prompt, `"Full Stack (Docker + Phone Debug)"` compound config |
| `.vscode/tasks.json` | Added `"Flutter: Run on Phone (Debug)"` (auto-detects IP), `"Flutter: Show Detected IP"` |
| `docker-compose.yml` | Added documentation comments explaining the 5-step workflow |
| `package.json` | Added `phone:debug`, `phone:build`, `phone:ip` scripts |
| `Makefile` | Added `phone-ip`, `phone-debug` targets |
| `ops/build_flutter_for_phone.ps1` | Helper script that auto-detects IP and runs Flutter |
| `ops/find_active_ip.ps1` | Utility to detect your machine's LAN IP |

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| **Phone can't connect** (network error in Flutter) | Wrong IP or firewall | Run `.\ops\find_active_ip.ps1`, ensure phone on same WiFi, check Windows Firewall allows port 8080 |
| **Debugger: "Connection refused" on port 5005** | Docker not running or port not exposed | `docker ps | findstr bmj-backend` — if missing, run `docker-compose up -d` |
| **Breakpoints not hit** | Wrong debug config selected | Make sure you selected **"Docker: Attach Debugger (Backend)"** not "Spring Boot Backend (Debug)" |
| **Breakpoints not hit** | Code changed after container started | Docker container runs its own copy of the code. Restart with `docker-compose restart backend` |
| **"Could not find a connected device"** | Phone not detected | Run `adb devices` to verify. If empty, check USB debugging and cable. |
| **Build fails with `API_BASE_URL` error** | Special characters in IP | Make sure IP has no spaces. Use format `192.168.1.100` only. |
| **Phone gets 404 errors** | Wrong API path | Check that `ApiConfig.baseUrl` resolves correctly. The default fallback `10.0.2.2` is for emulator only. |
| **IP changes frequently** | DHCP assignment | Use a static IP on your machine, or re-run `.\ops\build_flutter_for_phone.ps1` each time |

---

## How It Works: Technical Details

### The Debug Port Chain

```
VS Code Java Debugger
       │  attach to localhost:5005
       ▼
Windows Host
       │  docker-compose port mapping: "5005:5005"
       ▼
Docker Container (bmj-backend)
       │  JVM arg: -agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5005
       ▼
Spring Boot Application
       │  Breakpoint hit → JVM suspends thread → Debugger notified
       ▼
VS Code shows paused state → You inspect variables → Continue
```

### The API URL Flow

```
Phone makes HTTP request
       │
       ▼
Flutter app: ApiConfig.baseUrl
       │  Resolved from: --dart-define=API_BASE_URL
       │  (or falls back to 10.0.2.2 for emulator)
       ▼
URL: http://YOUR_MACHINE_IP:8080/api/...
       │  Your machine receives the request on WiFi interface
       ▼
Docker port mapping: 8080:8080
       │
       ▼
Spring Boot handles the request → Breakpoint hits → You debug!
```

---

## Related Files

- `lush/lib/config/api_config.dart` — How API_BASE_URL is resolved
- `.vscode/launch.json` — VS Code debug configurations
- `.vscode/tasks.json` — VS Code tasks for phone debugging
- `docker-compose.yml` — Docker service definitions
- `bmjServer/Dockerfile.dev` — Development Dockerfile with JDWP
- `ops/find_active_ip.ps1` — IP detection utility
- `ops/build_flutter_for_phone.ps1` — Phone build/run helper

---

## Cross-Reference Verification

### `docs/auth_flows.md` cross-reference — **CONCLUDED ✅** (2026-05-27)

Verification result: **No contradictions, no duplicates, no phantoms.**

- `PHONE_DEBUG_CHECKPOINTS.md` is a pure operational/CI workflow guide
- `auth_flows.md` documents auth state machine flows and BLoC event chains
- These two docs serve independent purposes and do not overlap in content
- No stale or outdated cross-references detected
