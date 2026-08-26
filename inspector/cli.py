import sys
import argparse
from pathlib import Path
from inspector.core import scan_source


def main():
    parser = argparse.ArgumentParser(description="AI Code Security Scanner CLI")
    parser.add_argument("target", help="Path to file to scan")
    parser.add_argument(
        "--fail-on-warnings",
        action="store_true",
        help="Exit with non-zero if MEDIUM or LOW issues are found",
    )
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.is_file():
        print(f"Error: File not found: {args.target}", file=sys.stderr)
        sys.exit(2)

    content = target_path.read_text(encoding="utf-8")
    print(f"Scanning {target_path.name}...")

    report = scan_source(content, file_name=target_path.name)

    print("\n" + "=" * 50)
    print(f"File: {report.file_path} ({report.total_lines} lines)")
    print(f"Status: {'PASSED' if report.passed else 'FAILED'}")
    print(f"Critical: {report.critical_count} | High: {report.high_count}")
    print("=" * 50)

    for idx, item in enumerate(report.findings, start=1):
        print(f"\n[{item.severity.value}] #{idx}: {item.title}")
        if item.line:
            print(f"  Line   : {item.line}")
        if item.cwe_or_owasp:
            print(f"  Ref    : {item.cwe_or_owasp}")
        print(f"  Detail : {item.detail}")
        print(f"  Fix    : {item.fix}")

    if not report.passed:
        sys.exit(1)

    if args.fail_on_warnings and len(report.findings) > 0:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()