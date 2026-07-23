"""Database Backup & Export Utility Script for IssueRadar AI."""

import argparse
import json
from datetime import datetime, timezone


def export_backup(output_file: str | None = None) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    target = output_file or f"issueradar_backup_{timestamp}.json"

    backup_payload = {
        "metadata": {
            "version": "1.0",
            "timestamp": timestamp,
            "system": "IssueRadar AI Production DB Exporter",
        },
        "tables": [
            "users",
            "repositories",
            "issues",
            "scores",
            "analyses",
            "saved_searches",
            "bookmarks",
            "notifications",
            "sync_jobs",
        ],
    }

    with open(target, "w", encoding="utf-8") as f:
        json.dump(backup_payload, f, indent=2)

    print(f"Successfully generated database backup manifest: {target}")
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IssueRadar AI Database Backup Utility")
    parser.add_argument("--out", type=str, help="Output file path for backup manifest")
    args = parser.parse_args()
    export_backup(args.out)
