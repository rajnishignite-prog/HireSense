"""
modules/exporter.py
===================
Handles exporting screening results to downloadable formats.

Currently supports:
  - CSV export (via build_csv)

Each function returns raw bytes or a string buffer that Streamlit's
st.download_button can consume directly.
"""

import csv
import io


def build_csv(results: list[dict]) -> str:
    """
    Convert a ranked list of candidate results into a CSV string.

    Expected structure of each result dict:
        {
            "rank":     int,
            "name":     str,
            "score":    float,
            "insights": {
                "recommendation": str,
                "strengths":      list[str],
                "gaps":           list[str],
            }
        }

    Args:
        results: List of candidate dicts, already sorted and ranked.

    Returns:
        A UTF-8 CSV string ready for st.download_button.
    """
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    # Header row
    writer.writerow([
        "Rank",
        "Candidate",
        "Score (0-100)",
        "Recommendation",
        "Strengths",
        "Gaps",
    ])

    # Data rows
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