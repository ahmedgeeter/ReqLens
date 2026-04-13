import re
import pandas as pd
from core.schema import REQ_TYPES, PRIORITIES


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def check_empty_text(df: pd.DataFrame) -> set[int]:
    return {i for i, row in df.iterrows() if not str(row["text"]).strip()}


def check_invalid_types(df: pd.DataFrame) -> set[int]:
    return {i for i, row in df.iterrows() if row["req_type"] not in REQ_TYPES}


def check_invalid_priorities(df: pd.DataFrame) -> set[int]:
    return {i for i, row in df.iterrows() if row["priority"] not in PRIORITIES}


def check_duplicates(df: pd.DataFrame) -> set[int]:
    seen: dict[str, int] = {}
    dupes: set[int] = set()
    for i, row in df.iterrows():
        key = _normalize(str(row["text"]))
        if not key:
            continue
        if key in seen:
            dupes.add(seen[key])
            dupes.add(i)
        else:
            seen[key] = i
    return dupes


def summarize_issues(df: pd.DataFrame) -> dict:
    empty = check_empty_text(df)
    bad_type = check_invalid_types(df)
    bad_priority = check_invalid_priorities(df)
    dupes = check_duplicates(df)
    invalid = empty | bad_type | bad_priority
    return {
        "empty_text": empty,
        "invalid_type": bad_type,
        "invalid_priority": bad_priority,
        "duplicates": dupes,
        "invalid_rows": invalid,
    }
