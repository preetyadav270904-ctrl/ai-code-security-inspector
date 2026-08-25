import json
import ast
from typing import Tuple
from groq import Groq
from inspector import config
from inspector.models import ScanReport, Finding

SYSTEM_PROMPT = """You are a static code security analyzer. Review the provided source code for vulnerabilities (OWASP/CWE) and fatal runtime bugs.

Return ONLY a valid JSON object matching this schema:
{
  "findings": [
    {
      "title": "Short title",
      "severity": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFO",
      "issue_type": "SECURITY_VULNERABILITY" | "BUG" | "CODE_SMELL",
      "line": 1,
      "cwe_or_owasp": "CWE or OWASP code",
      "detail": "Why this is an issue",
      "fix": "Actionable fix or refactored snippet"
    }
  ]
}
If no issues are found, return {"findings": []}."""


def prepare_source(code: str, file_path: str) -> Tuple[str, int, bool]:
    lines = code.splitlines()
    total_lines = len(lines)

    valid_ast = True
    if file_path.endswith(".py"):
        try:
            ast.parse(code, filename=file_path)
        except SyntaxError:
            valid_ast = False

    formatted = "\n".join(f"{i + 1:4d} | {line}" for i, line in enumerate(lines))
    return formatted, total_lines, valid_ast


def scan_source(code: str, file_name: str = "unnamed.py") -> ScanReport:
    client = Groq(api_key=config.GROQ_API_KEY)
    indexed_code, total_lines, valid_ast = prepare_source(code, file_name)

    user_message = f"File: {file_name} (Syntax Valid: {valid_ast})\n\n{indexed_code}"

    completion = client.chat.completions.create(
        model=config.MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    raw = completion.choices[0].message.content or "{}"
    data = json.loads(raw)
    raw_findings = data.get("findings", [])

    return ScanReport(
        file_path=file_name,
        total_lines=total_lines,
        findings=[Finding(**f) for f in raw_findings],
    )