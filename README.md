# Cosmetz 3.5 (Interactive Scout + Creative + Thermal Benchmark Edition)

Cosmetz is a Windows optimization suite focused on **interactive control + safety checks + deep versatility + benchmark comparison**.

## New in 3.5

- Interactive menu for every operation and every step:
  - Run / Skip / Fallback / Details
- Animated terminal background effect in Rich-enabled terminals.
- Optimization modes:
  - **Aggressive** (all available steps)
  - **Balanced** (low + medium risk)
  - **Peaceful** (low-risk but still effective steps)
- Internet/doc safety scout before each step:
  - Internet connectivity check
  - Docs reachability check for referenced Windows command area
  - Can block medium/high-risk steps when checks fail
- Broad platform detection:
  - CPU/GPU/RAM/core tier
  - Architecture
  - Manufacturer/model
  - Laptop/desktop inference
- Expanded RAM optimization suite.
- Bigger GitHub scouting across more queries and pages.
- **New Creative Workstation Boost** for creators:
  - Stability/performance-focused settings for editing, rendering, and content workflows
  - Includes memory, power, and creator-friendly system tuning paths
- **Thermal-guarded benchmarking with FPS chart + % increase**:
  - Baseline benchmark capture
  - Optional optimization pack run
  - Post-optimization benchmark capture
  - Before/after chart and delta percentage
  - **Temperature monitoring during benchmark with automatic cutoff at 90°C**

## Benchmarking details

- Uses built-in **WinSAT** to collect system scores (CPU, memory, graphics, D3D, disk).
- Derives an estimated FPS metric from graphics-related score for before/after comparison.
- Includes optional user-permission prompt to install external benchmark software via `winget` (best effort), then falls back to WinSAT if installation fails.
- Polls temperatures during benchmark using available sensors (best effort) and aborts run if the temperature reaches/exceeds 90°C.

## Workflows

1. Explain Plan
2. Quick Optimize
3. Gaming Boost
4. RAM + Memory Suite
5. Creative Workstation Boost
6. Deep Repair
7. Network Toolkit
8. Driver + OEM Assistant
9. Heavy App Analyzer
10. Massive GitHub Scout
11. Benchmark FPS Chart + Compare
12. Revert Tweaks
13. Re-run Setup

## Safety controls

- Dry-run preview mode
- Granular category toggles (registry, BCD, service, network, storage, visual, memory)
- Step-level confirmations
- Fallback paths when category is disabled or user skips a step
- Internet/document guard checks for each step (optional)

## Install

```powershell
pip install rich psutil
```

## Run

```powershell
python cosmetz.py
```

or launch:

```text
Cosmetz.bat
```
