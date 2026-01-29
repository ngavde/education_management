from frappe import _


def get_data():
    return [
        {
            "label": _("Merit List Management"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Merit Score Submission",
                    "description": _("Submit and manage merit scores for admission"),
                },
                {
                    "type": "doctype",
                    "name": "Merit Score Validation",
                    "description": _("Validate and approve merit score submissions"),
                },
                {
                    "type": "doctype",
                    "name": "Merit List Generation Tool",
                    "description": _("Generate merit lists and rankings"),
                },
            ]
        },
        {
            "label": _("Configuration"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Education Management Settings",
                    "description": _("Configure merit list process settings"),
                },
            ]
        },
        {
            "label": _("Reports & Analytics"),
            "items": [
                {
                    "type": "report",
                    "name": "Merit List Report",
                    "description": _("Comprehensive merit list with rankings"),
                    "is_query_report": True,
                },
                {
                    "type": "report",
                    "name": "Merit Validation Report",
                    "description": _("Track merit validation status"),
                    "is_query_report": True,
                },
            ]
        }
    ]