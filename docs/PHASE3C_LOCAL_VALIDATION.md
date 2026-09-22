# Phase 3C local validation — processing results UI

Run the complete gate from the repository root:

```bash
bash scripts/validate_phase3c_local.sh
```

The runner reuses the Phase 3B backend lifecycle gate, builds and starts the complete stack, verifies both updated UI routes, confirms the audio page uses the dedicated audio endpoint, and verifies status polling/result-download wiring.

Expected final line:

```text
PASS: Phase 3C processing results UI validation completed
```
