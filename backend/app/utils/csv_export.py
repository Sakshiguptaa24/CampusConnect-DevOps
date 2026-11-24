import csv
import io
from typing import List, Dict, Any


def export_to_csv(data: List[Dict[str, Any]], filename: str = "export.csv") -> str:
    """Export a list of dictionaries to CSV string."""
    if not data:
        return ""
    output = io.StringIO()
    headers = list(data[0].keys())
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    return output.getvalue()


def export_registrations_csv(registrations: list) -> str:
    """Export registrations to CSV format."""
    data = []
    for reg in registrations:
        data.append(
            {
                "Registration ID": reg.get("id", ""),
                "User Name": reg.get("user_name", ""),
                "User Email": reg.get("user_email", ""),
                "Department": reg.get("user_department", ""),
                "Event Title": reg.get("event_title", ""),
                "Status": reg.get("status", ""),
                "QR Code": reg.get("qr_code", ""),
                "Registered At": reg.get("registered_at", ""),
            }
        )
    return export_to_csv(data)


def export_attendees_csv(attendees: list) -> str:
    """Export attendees to CSV format."""
    data = []
    for att in attendees:
        data.append(
            {
                "User Name": att.get("user_name", ""),
                "User Email": att.get("user_email", ""),
                "Department": att.get("user_department", ""),
                "Status": att.get("status", ""),
                "Registered At": att.get("registered_at", ""),
            }
        )
    return export_to_csv(data)
