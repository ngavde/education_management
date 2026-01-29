import frappe
from frappe.model.document import Document
from frappe.utils import flt, now


class MeritScoreValidation(Document):
    def validate(self):
        self.calculate_differences()
        self.calculate_verified_percentage()

    def on_submit(self):
        self.update_merit_submission()

    def calculate_differences(self):
        if self.verified_total_score and self.original_total_score:
            self.score_difference = flt(self.verified_total_score - self.original_total_score, 2)

        if self.verified_percentage and self.original_percentage:
            self.percentage_difference = flt(self.verified_percentage - self.original_percentage, 2)

    def calculate_verified_percentage(self):
        if self.verified_total_score:
            # Get maximum score from merit submission
            merit_doc = frappe.get_doc("Merit Score Submission", self.merit_submission)
            if merit_doc.maximum_possible_score:
                self.verified_percentage = flt(self.verified_total_score / merit_doc.maximum_possible_score * 100, 2)

    def update_merit_submission(self):
        """Update the merit submission based on validation decision"""
        merit_doc = frappe.get_doc("Merit Score Submission", self.merit_submission)

        if self.final_decision == "Approved":
            # Update scores if they were changed during validation
            if self.verified_total_score and self.score_difference != 0:
                merit_doc.total_merit_score = self.verified_total_score
                merit_doc.percentage_score = self.verified_percentage

            merit_doc.validation_status = "Validated"
            merit_doc.validated_by = self.validator
            merit_doc.validation_date = now()
            merit_doc.submission_status = "Approved"
            merit_doc.document_verification_status = "Verified"

            if self.validation_comments:
                merit_doc.admin_remarks = self.validation_comments

        elif self.final_decision == "Rejected":
            merit_doc.validation_status = "Rejected"
            merit_doc.submission_status = "Rejected"
            merit_doc.admin_remarks = self.validation_comments or "Merit submission rejected during validation"

        merit_doc.save()

    @frappe.whitelist()
    def approve_validation(self):
        """Approve the merit validation"""
        self.final_decision = "Approved"
        self.validation_status = "Validated"
        self.save()
        self.submit()
        return "Merit validation approved successfully"

    @frappe.whitelist()
    def reject_validation(self):
        """Reject the merit validation"""
        self.final_decision = "Rejected"
        self.validation_status = "Rejected"
        self.save()
        self.submit()
        return "Merit validation rejected"


@frappe.whitelist()
def create_validation_record(merit_submission):
    """Create a new merit score validation record"""
    # Check if validation record already exists
    existing = frappe.db.exists("Merit Score Validation", {"merit_submission": merit_submission})
    if existing:
        return frappe.get_doc("Merit Score Validation", existing)

    # Create new validation record
    merit_doc = frappe.get_doc("Merit Score Submission", merit_submission)

    validation_doc = frappe.new_doc("Merit Score Validation")
    validation_doc.merit_submission = merit_submission
    validation_doc.validator = frappe.session.user
    validation_doc.verified_total_score = merit_doc.total_merit_score  # Start with original score
    validation_doc.save()

    return validation_doc


@frappe.whitelist()
def get_pending_validations():
    """Get list of pending merit validations"""
    return frappe.get_all(
        "Merit Score Validation",
        filters={"validation_status": ["in", ["Pending", "In Progress"]]},
        fields=[
            "name", "merit_submission", "applicant_name", "validation_date",
            "validation_status", "original_total_score"
        ],
        order_by="validation_date desc"
    )