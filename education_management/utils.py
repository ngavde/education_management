import frappe
from frappe.utils import cint


def check_merit_list_requirement(doc, method):
    """Check if merit list submission is required for student applicant"""
    settings = get_education_management_settings()

    if settings.get("enable_merit_list_process") and settings.get("merit_list_mandatory"):
        # Check if merit submission exists for this applicant
        merit_submission = frappe.db.exists("Merit Score Submission", {
            "student_applicant": doc.name,
            "docstatus": 1
        })

        if not merit_submission and doc.application_status in ["Approved", "Admitted"]:
            frappe.msgprint(
                f"Merit list submission is required before approving/admitting {doc.title}",
                alert=True
            )


def get_education_management_settings():
    """Get education management settings with defaults"""
    try:
        settings = frappe.get_single("Education Management Settings")
        return {
            "enable_merit_list_process": cint(settings.enable_merit_list_process),
            "merit_list_mandatory": cint(settings.merit_list_mandatory),
            "merit_validation_required": cint(settings.merit_validation_required),
            "document_upload_mandatory": cint(settings.document_upload_mandatory),
            "auto_approve_if_documents_verified": cint(settings.auto_approve_if_documents_verified),
            "default_minimum_merit_score": settings.default_minimum_merit_score or 0,
            "max_file_size_mb": settings.max_file_size_mb or 10,
            "enable_category_wise_ranking": cint(settings.enable_category_wise_ranking),
            "enable_program_wise_ranking": cint(settings.enable_program_wise_ranking),
            "auto_generate_rankings": cint(settings.auto_generate_rankings),
            "notify_on_submission": cint(settings.notify_on_submission),
            "notify_on_validation": cint(settings.notify_on_validation),
            "validation_reminder_days": settings.validation_reminder_days or 3
        }
    except:
        # Return defaults if settings don't exist
        return {
            "enable_merit_list_process": 1,
            "merit_list_mandatory": 0,
            "merit_validation_required": 1,
            "document_upload_mandatory": 1,
            "auto_approve_if_documents_verified": 0,
            "default_minimum_merit_score": 0,
            "max_file_size_mb": 10,
            "enable_category_wise_ranking": 1,
            "enable_program_wise_ranking": 1,
            "auto_generate_rankings": 1,
            "notify_on_submission": 1,
            "notify_on_validation": 1,
            "validation_reminder_days": 3
        }


@frappe.whitelist()
def get_merit_dashboard_data():
    """Get dashboard data for merit list overview"""
    data = {
        "total_submissions": 0,
        "pending_validation": 0,
        "validated_submissions": 0,
        "rejected_submissions": 0,
        "recent_submissions": []
    }

    # Get counts
    data["total_submissions"] = frappe.db.count("Merit Score Submission", {"docstatus": 1})
    data["pending_validation"] = frappe.db.count("Merit Score Submission", {
        "docstatus": 1,
        "validation_status": "Pending"
    })
    data["validated_submissions"] = frappe.db.count("Merit Score Submission", {
        "docstatus": 1,
        "validation_status": "Validated"
    })
    data["rejected_submissions"] = frappe.db.count("Merit Score Submission", {
        "docstatus": 1,
        "validation_status": "Rejected"
    })

    # Get recent submissions
    data["recent_submissions"] = frappe.get_all(
        "Merit Score Submission",
        filters={"docstatus": 1},
        fields=[
            "name", "applicant_name", "total_merit_score", "submission_status",
            "validation_status", "submission_date"
        ],
        order_by="creation desc",
        limit=10
    )

    return data


def send_merit_notification(submission_doc, notification_type):
    """Send notifications for merit submissions"""
    settings = get_education_management_settings()

    if not settings.get(f"notify_on_{notification_type}"):
        return

    # Get notification recipients
    recipients = []

    # Add student applicant email
    if submission_doc.student_applicant:
        applicant_doc = frappe.get_doc("Student Applicant", submission_doc.student_applicant)
        if applicant_doc.student_email_id:
            recipients.append(applicant_doc.student_email_id)

    # Add validators for validation notifications
    if notification_type == "validation" and submission_doc.validated_by:
        user_doc = frappe.get_doc("User", submission_doc.validated_by)
        if user_doc.email:
            recipients.append(user_doc.email)

    if not recipients:
        return

    # Prepare notification content
    if notification_type == "submission":
        subject = f"Merit Score Submitted - {submission_doc.applicant_name}"
        message = f"""
        Dear {submission_doc.applicant_name},

        Your merit score submission has been received successfully.

        Details:
        - Merit Score: {submission_doc.total_merit_score}
        - Percentage: {submission_doc.percentage_score}%
        - Program: {submission_doc.program}
        - Submission Date: {submission_doc.submission_date}

        Your submission is now under review.

        Best regards,
        Education Management Team
        """
    else:  # validation
        subject = f"Merit Score Validation Update - {submission_doc.applicant_name}"
        status = submission_doc.validation_status
        message = f"""
        Dear {submission_doc.applicant_name},

        Your merit score submission has been {status.lower()}.

        Details:
        - Merit Score: {submission_doc.total_merit_score}
        - Status: {status}
        - Validated By: {submission_doc.validated_by}
        - Validation Date: {submission_doc.validation_date}

        Best regards,
        Education Management Team
        """

    # Send notification
    try:
        frappe.sendmail(
            recipients=recipients,
            subject=subject,
            message=message,
            reference_doctype="Merit Score Submission",
            reference_name=submission_doc.name
        )
    except Exception as e:
        frappe.log_error(f"Merit notification failed: {str(e)}", "Merit Notification Error")