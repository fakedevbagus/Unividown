# Complete Phase 3 gate

Run the entire Phase 3 acceptance gate from the repository root:

```bash
bash scripts/validate_phase3_complete.sh
```

The runner executes all earlier Phase 3 checks and then processes deterministic fixtures through video conversion, trimming, audio extraction, image optimization, GIF creation, and subtitle extraction. It downloads every result, checks for filesystem-path leakage and upload cleanup, and verifies that the core image reports optional transcription as unavailable.

Expected final line:

```text
PASS: Complete Phase 3 media fixture gate completed
```
