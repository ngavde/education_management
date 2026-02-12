import frappe
from frappe.model.document import Document
from frappe.utils import flt, nowdate, now


class MeritScoreSubmission(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from education_management.education_management.doctype.merit_subject_score.merit_subject_score import MeritSubjectScore
        from frappe.types import DF

        academic_year: DF.Link | None
        admin_remarks: DF.SmallText | None
        amended_from: DF.Link | None
        applicant_name: DF.Data | None
        category_rank: DF.Int
        document_verification_status: DF.Literal["Pending", "Verified", "Rejected"]
        maximum_possible_score: DF.Float
        merit_grade: DF.Literal["", "A+", "A", "B+", "B", "C+", "C", "D", "F"]
        merit_rank: DF.Int
        naming_series: DF.Literal["EDU-MRT-.YYYY.-"]
        percentage_score: DF.Percent
        program: DF.Link | None
        student_applicant: DF.Link
        student_category: DF.Link | None
        subject_scores: DF.Table[MeritSubjectScore]
        submission_date: DF.Date | None
        submission_status: DF.Literal["Draft", "Submitted", "Under Review", "Approved", "Rejected"]
        supporting_documents: DF.Attach | None
        teacher_comments: DF.SmallText | None
        total_merit_score: DF.Float
        validated_by: DF.Link | None
        validation_date: DF.Datetime | None
        validation_status: DF.Literal["Pending", "Validated", "Rejected"]
    # end: auto-generated types
    def validate(self):
        self.check_validation_update_permission()
        self.calculate_percentage()
        self.validate_scores()
        self.calculate_grade()

    def check_validation_update_permission(self):
        """Prevent updates after validation unless allowed in settings"""
        if not self.is_new():
            # Get the original document to compare changes
            original_doc = frappe.get_doc("Merit Score Submission", self.name)

            # Prevent Document Verification Status changes after submission
            if (self.docstatus == 1 and
                self.document_verification_status != original_doc.document_verification_status and
                not getattr(self.flags, 'updating_verification', False) and
                not frappe.session.user == "Administrator"):

                # Check if user has specific role permissions
                if not (frappe.has_permission("Merit Score Submission", "write") and
                       (frappe.get_roles() and any(role in ["Academics User", "System Manager", "Administrator"] for role in frappe.get_roles()))):
                    frappe.throw(
                        "Document Verification Status cannot be changed after submission. Only authorized users can update verification status.",
                        frappe.ValidationError
                    )

            # Prevent Validation Status changes after submission
            if (self.docstatus == 1 and
                self.validation_status != original_doc.validation_status and
                not getattr(self.flags, 'updating_validation', False) and
                not frappe.session.user == "Administrator"):

                # Check if user has specific role permissions
                if not (frappe.has_permission("Merit Score Submission", "write") and
                       (frappe.get_roles() and any(role in ["Academics User", "System Manager", "Administrator"] for role in frappe.get_roles()))):
                    frappe.throw(
                        "Validation Status cannot be changed after submission. Only authorized users can update validation status.",
                        frappe.ValidationError
                    )

            # Prevent Submission Status changes after submission
            if (self.docstatus == 1 and
                self.submission_status != original_doc.submission_status and
                not getattr(self.flags, 'updating_validation', False) and
                not frappe.session.user == "Administrator"):

                # Check if user has specific role permissions
                if not (frappe.has_permission("Merit Score Submission", "write") and
                       (frappe.get_roles() and any(role in ["Academics User", "System Manager", "Administrator"] for role in frappe.get_roles()))):
                    frappe.throw(
                        "Submission Status cannot be changed after submission. Only authorized users can update submission status through proper workflow.",
                        frappe.ValidationError
                    )

            # Prevent updates after validation unless allowed in settings
            if self.validation_status == "Validated":
                from education_management.utils import get_education_management_settings
                settings = get_education_management_settings()

                if not settings.get("allow_score_modification_after_validation"):
                    # Allow only certain fields to be updated
                    allowed_fields = ['admin_remarks', 'teacher_comments', 'validation_status', 'validated_by', 'validation_date', 'document_verification_status']

                    for field in self.meta.get_fieldnames():
                        if field not in allowed_fields and self.get(field) != original_doc.get(field):
                            frappe.throw(
                                f"Cannot modify '{self.meta.get_field(field).label}' after validation. "
                                "Enable 'Allow Score Modification After Validation' in Education Management Settings to allow changes.",
                                frappe.ValidationError
                            )

    def on_submit(self):
        self.submission_status = "Submitted"
        self.save()

    def on_cancel(self):
        self.submission_status = "Draft"
        self.save()

    def calculate_percentage(self):
        if self.total_merit_score and self.maximum_possible_score:
            self.percentage_score = flt(self.total_merit_score / self.maximum_possible_score * 100, 2)

    def validate_scores(self):
        if self.total_merit_score and self.maximum_possible_score:
            if self.total_merit_score > self.maximum_possible_score:
                frappe.throw("Total Merit Score cannot be greater than Maximum Possible Score")

            if self.total_merit_score < 0:
                frappe.throw("Total Merit Score cannot be negative")

        # Validate subject scores sum
        if self.subject_scores:
            subject_total = sum([flt(row.score) for row in self.subject_scores])
            if abs(subject_total - flt(self.total_merit_score)) > 0.01:
                frappe.throw(f"Sum of subject scores ({subject_total}) does not match total merit score ({self.total_merit_score})")

    def calculate_grade(self):
        if self.percentage_score:
            percentage = flt(self.percentage_score)
            if percentage >= 95:
                self.merit_grade = "A+"
            elif percentage >= 90:
                self.merit_grade = "A"
            elif percentage >= 85:
                self.merit_grade = "B+"
            elif percentage >= 80:
                self.merit_grade = "B"
            elif percentage >= 75:
                self.merit_grade = "C+"
            elif percentage >= 70:
                self.merit_grade = "C"
            elif percentage >= 60:
                self.merit_grade = "D"
            else:
                self.merit_grade = "F"

    def validate_documents(self):
        """Method to validate supporting documents"""
        if self.supporting_documents and self.document_verification_status == "Pending":
            self.document_verification_status = "Under Review"

    def approve_validation(self, validator=None):
        """Method to approve merit score validation"""
        self.flags.updating_validation = True
        self.validation_status = "Validated"
        self.validated_by = validator or frappe.session.user
        self.validation_date = now()
        self.document_verification_status = "Verified"
        self.submission_status = "Approved"
        self.save()

    def reject_validation(self, reason=None):
        """Method to reject merit score validation"""
        self.flags.updating_validation = True
        self.validation_status = "Rejected"
        self.submission_status = "Rejected"
        if reason:
            self.admin_remarks = reason
        self.save()


@frappe.whitelist()
def get_merit_ranking(program=None, academic_year=None, student_category=None):
    """Generate merit ranking based on filters"""
    filters = {
        "docstatus": 1,
        "validation_status": "Validated",
        "submission_status": "Approved"
    }

    if program:
        filters["program"] = program
    if academic_year:
        filters["academic_year"] = academic_year
    if student_category:
        filters["student_category"] = student_category

    submissions = frappe.get_all(
        "Merit Score Submission",
        filters=filters,
        fields=[
            "name", "student_applicant", "applicant_name", "total_merit_score",
            "percentage_score", "program", "student_category"
        ],
        order_by="total_merit_score desc, percentage_score desc"
    )

    # Calculate ranks
    overall_rank = 1
    category_ranks = {}

    for submission in submissions:
        # Overall merit rank
        frappe.db.set_value("Merit Score Submission", submission.name, "merit_rank", overall_rank)
        overall_rank += 1

        # Category-wise rank
        category = submission.student_category or "General"
        if category not in category_ranks:
            category_ranks[category] = 1

        frappe.db.set_value("Merit Score Submission", submission.name, "category_rank", category_ranks[category])
        category_ranks[category] += 1

    frappe.db.commit()
    return submissions


@frappe.whitelist()
def validate_merit_submission(submission_name, action, comments=None):
    """Validate or reject merit submission"""
    doc = frappe.get_doc("Merit Score Submission", submission_name)

    if action == "approve":
        doc.approve_validation()
        frappe.msgprint("Merit submission validated successfully")
    elif action == "reject":
        doc.reject_validation(comments)
        frappe.msgprint("Merit submission rejected")

    return doc


@frappe.whitelist()
def update_document_verification(submission_name, status):
    """Update document verification status"""
    # Check permissions first
    if not frappe.has_permission("Merit Score Submission", "write"):
        frappe.throw("Insufficient permissions to update document verification status")

    # Update the status directly in database to bypass document validation
    frappe.db.set_value("Merit Score Submission", submission_name, {
        "document_verification_status": status,
        "modified": frappe.utils.now(),
        "modified_by": frappe.session.user
    })
    frappe.db.commit()

    # Get updated document
    doc = frappe.get_doc("Merit Score Submission", submission_name)

    frappe.msgprint(f"Document verification status updated to {status}")
    return doc


def on_submit_merit_score(doc, method):
    """Handle merit score submission events"""
    from education_management.utils import send_merit_notification

    # Send notification
    send_merit_notification(doc, "submission")


def on_cancel_merit_score(doc, method):
    """Handle merit score cancellation"""
    # Reset any linked validation records
    validations = frappe.get_all("Merit Score Validation", {
        "merit_submission": doc.name,
        "docstatus": 0
    })

    for validation in validations:
        frappe.delete_doc("Merit Score Validation", validation.name)