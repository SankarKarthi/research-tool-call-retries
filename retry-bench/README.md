# Tool-call retry benchmark

Hand-written Harbor & Co. support agent. Same loop, prompts, model, tasks, and fault schedule across three retry layers:

| Config | Policy |
|--------|--------|
| A | No retry — tool errors go straight back to the model |
| B | Naive retry — every error retried up to 3 times |
| C | Smart retry — classify first, then pick a per-type policy |

## Setup

```powershell
$py = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
& $py -m pip install -r requirements.txt
$env:GROQ_API_KEY = "gsk_..."
& $py data\build_fixtures.py
```

## Run

No-retry first (config A), with injected faults, seed 1:

```powershell
& $py -m bench.runner --configs A --seeds 1
```

No-fault ceiling for A:

```powershell
& $py -m bench.runner --configs A --seeds 1 --no-fault --tag A_nofault
```

Then naive and smart:

```powershell
& $py -m bench.runner --configs B --seeds 1 --tag B_faults
& $py -m bench.runner --configs C --seeds 1 --tag C_faults
```

Full protocol from the LLD (A/B/C × 3 seeds × 40 tasks):

```powershell
& $py -m bench.runner --configs A,B,C
```

Smoke a few tasks without spending the full budget:

```powershell
& $py -m bench.runner --configs A --seeds 1 --tasks T001,T011,T019 --limit 3
```

Results land in `results/` as JSONL event logs, a per-task CSV, and a summary JSON.

## Tests

```powershell
& $py -m pytest -q
```
