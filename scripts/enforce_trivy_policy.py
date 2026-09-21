#!/usr/bin/env python3
import json
import os
import sys
from datetime import date
from pathlib import Path


def annotation(level: str, title: str, message: str) -> None:
    def escape(value: str) -> str:
        return value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    print(f"::{level} title={escape(title)}::{escape(message)}")


def load_findings(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    for result in data.get("Results") or []:
        for vulnerability in result.get("Vulnerabilities") or []:
            if vulnerability.get("Severity") in {"HIGH", "CRITICAL"}:
                yield vulnerability


def main() -> int:
    if len(sys.argv) < 3:
        raise SystemExit("usage: enforce_trivy_policy.py POLICY IMAGE=REPORT [IMAGE=REPORT ...]")

    policy_path = Path(sys.argv[1])
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    exceptions = {
        (item["image"], item["package"], item["id"]): item
        for item in policy.get("exceptions", [])
    }
    today = date.today()
    blocked = 0
    excepted = 0
    rows = []

    for spec in sys.argv[2:]:
        image, report_name = spec.split("=", 1)
        for finding in load_findings(Path(report_name)):
            vuln_id = finding["VulnerabilityID"]
            package = finding["PkgName"]
            installed = finding.get("InstalledVersion", "unknown")
            fixed = finding.get("FixedVersion") or "unfixed"
            exception = exceptions.get((image, package, vuln_id))
            title = f"Trivy {image} {finding['Severity']} {vuln_id}"
            detail = f"package={package} installed={installed} fixed={fixed}"

            if exception:
                expiry = date.fromisoformat(exception["expires"])
                if today <= expiry:
                    excepted += 1
                    annotation("warning", title, f"temporary exception until {expiry}: {detail}")
                    rows.append((image, vuln_id, package, "temporary exception", str(expiry)))
                    continue
                detail += f" exception expired={expiry}"

            blocked += 1
            annotation("error", title, detail)
            rows.append((image, vuln_id, package, "blocked", "-"))

    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as summary:
            summary.write("## Trivy image policy\n\n")
            summary.write("| Image | CVE | Package | Decision | Expires |\n|---|---|---|---|---|\n")
            for row in rows:
                summary.write("| " + " | ".join(row) + " |\n")
            summary.write(f"\nBlocked: **{blocked}** · Temporary exceptions: **{excepted}**\n")

    print(f"Blocked findings: {blocked}; active temporary exceptions: {excepted}")
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
