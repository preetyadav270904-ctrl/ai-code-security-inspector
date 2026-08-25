from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, computed_field


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class IssueType(str, Enum):
    VULNERABILITY = "SECURITY_VULNERABILITY"
    BUG = "BUG"
    SMELL = "CODE_SMELL"


class Finding(BaseModel):
    title: str
    severity: Severity
    issue_type: IssueType
    line: Optional[int] = None
    cwe_or_owasp: Optional[str] = Field(
        None, description="e.g. CWE-89 or OWASP A03:2021"
    )
    detail: str
    fix: str


class ScanReport(BaseModel):
    file_path: str
    total_lines: int
    findings: List[Finding] = []

    @computed_field
    @property
    def passed(self) -> bool:
        return not any(
            f.severity in (Severity.CRITICAL, Severity.HIGH) for f in self.findings
        )

    @computed_field
    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.CRITICAL)

    @computed_field
    @property
    def high_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.HIGH)


class CodePayload(BaseModel):
    source: str = Field(..., min_length=1)
    file_name: str = "snippet.py"