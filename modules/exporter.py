"""
modules/exporter.py
===================
Handles exporting screening results to downloadable CSV.
"""

import csv
import io


def build_csv(results: list[dict]) -> str:
    """
    Convert ranked candidate results into a CSV string.

    Args:
        results: List of candidate dicts (already sorted and ranked).

    Returns:
        UTF-8 CSV string ready for st.download_button.
    """
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    writer.writerow(["Rank", "Candidate", "Score (0-100)", "Recommendation", "Strengths", "Gaps"])

    for r in results:
        insights = r.get("insights", {})
        writer.writerow([
            r.get("rank",  "—"),
            r.get("name",  "Unknown"),
            r.get("score", 0),
            insights.get("recommendation", "—"),
            " | ".join(insights.get("strengths", [])),
            " | ".join(insights.get("gaps",      [])),
        ])

    return buffer.getvalue()