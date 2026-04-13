from dataclasses import dataclass, field
import pandas as pd

REQ_TYPES = ["Functional", "Non-Functional", "Constraint"]
PRIORITIES = ["High", "Medium", "Low"]
REVIEW_STATUSES = ["Pending", "Reviewed", "Accepted"]

COLUMNS = ["req_id", "text", "req_type", "priority", "source_phrase", "review_status"]


@dataclass
class RequirementRecord:
    req_id: str = ""
    text: str = ""
    req_type: str = "Functional"
    priority: str = "Medium"
    source_phrase: str = ""
    review_status: str = "Pending"


def assign_ids(records: list[RequirementRecord]) -> None:
    for i, r in enumerate(records, start=1):
        r.req_id = f"REQ-{i:03d}"


def to_dataframe(records: list[RequirementRecord]) -> pd.DataFrame:
    rows = [
        {
            "req_id": r.req_id,
            "text": r.text,
            "req_type": r.req_type,
            "priority": r.priority,
            "source_phrase": r.source_phrase,
            "review_status": r.review_status,
        }
        for r in records
    ]
    return pd.DataFrame(rows, columns=COLUMNS)
