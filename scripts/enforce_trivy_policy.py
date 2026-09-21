#!/usr/bin/env python3
import fnmatch
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
        finding_class = result.get("Class", "unknown")
        for vulnerability in result.get("Vulnerabilities") or []:
            if vulnerability.get("Severity") in {"HIGH", "CRITICAL"}:
                yield finding_class, vulnerability


def active(item, today: date) -> bool:
    return today <= date.fromisoformat(item["expires"])


def find_exact_exception(exceptions, image: str, package: str, vuln_id: str):
    for item in exceptions:
        if item["image"] == image and item["id"] == vuln_id and fnmatch.fnmatchcase(package, item["package"]):
            return item
    return None


def find_unfixed_os_exception(exceptions, image: str, package: str, finding_class: str, fixed: str):
    if finding_class != "os-pkgs" or fixed != "unfixed":
        return None
    for item in exceptions:
        if item["image"] == image and fnmatch.fnmatchcase(package, item["package"]):
            return item
    return None


def main() -> int:
    if len(sys.argv) < 3:
        raise SystemExit("usage: enforce_trivy_policy.py POLICY IMAGE=REPORT [IMAGE=REPORT ...]")

    policy = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    exact_exceptions = policy.get("exceptions", [])
    unfixed_os_exceptions = policy.get("unfixed_os_package_exceptions", [])
    today = date.today()
    blocked = []
    excepted = []
    rows = []

    for spec in sys.argv[2:]:
        image, report_name = spec.split("=", 1)
        for finding_class, finding in load_findings(Path(report_name)):
            vuln_id = finding["VulnerabilityID"]
            package = finding["PkgName"]
            installed = finding.get("InstalledVersion", "unknown")
            fixed = finding.get("FixedVersion") or "unfixed"
            exception = find_exact_exception(exact_exceptions, image, package, vuln_id)
            if not exception:
                exception = find_unfixed_os_exception(
                    unfixed_os_exceptions, image, package, finding_class, fixed
                )

            key = f"{image}:{finding['Severity']}:{vuln_id}:{package}:installed={installed}:fixed={fixed}"
            if exception and active(exception, today):
                expiry = exception["expires"]
                excepted.append(key)
                rows.append((image, vuln_id, package, "temporary exception", expiry))
                continue

            blocked.append(key)
            rows.append((image, vuln_id, package, "blocked", "-"))

    if excepted:
        annotation(
            "warning",
            f"Trivy temporary exceptions: {len(excepted)}",
            "Worker OS findings have no fixed version and are accepted until 2026-10-21; see docs/SECURITY_EXCEPTIONS.md and the job summary.",
        )
    if blocked:
        annotation("error", f"Trivy blocked {len(blocked)} findings", "; ".join(blocked))

    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as summary:
            summary.write("## Trivy image policy\n\n")
            summary.write("| Image | CVE | Package | Decision | Expires |\n|---|---|---|---|---|\n")
            for row in rows:
                summary.write("| " + " | ".join(row) + " |\n")
            summary.write(f"\nBlocked: **{len(blocked)}** · Temporary exceptions: **{len(excepted)}**\n")

    print(f"Blocked findings: {len(blocked)}; active temporary exceptions: {len(excepted)}")
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
