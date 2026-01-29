import frappe
from frappe.model.document import Document
from frappe.utils import flt, today, cstr
import json


class MeritListGenerationTool(Document):
    @frappe.whitelist()
    def generate_merit_list(self):
        """Generate merit list based on filter criteria"""
        # Build filters
        filters = self.get_filters()

        # Get merit submissions
        submissions = self.get_merit_submissions(filters)

        # Generate HTML table
        html_content = self.generate_html_table(submissions)

        # Update the results field
        self.merit_list_results = html_content

        # Update summary
        self.generation_summary = self.generate_summary(submissions)

        self.save()

        frappe.msgprint(f"Merit list generated successfully with {len(submissions)} entries")
        return submissions

    def get_filters(self):
        """Build filters based on form inputs"""
        filters = {
            "academic_year": self.academic_year,
            "docstatus": 1
        }

        if not self.include_pending:
            filters["validation_status"] = "Validated"
            filters["submission_status"] = "Approved"

        if self.program:
            filters["program"] = self.program

        if self.student_category:
            filters["student_category"] = self.student_category

        if self.minimum_score:
            filters["total_merit_score"] = [">=", self.minimum_score]

        return filters

    def get_merit_submissions(self, filters):
        """Get merit submissions based on filters"""
        fields = [
            "name", "student_applicant", "applicant_name", "total_merit_score",
            "percentage_score", "merit_rank", "category_rank", "merit_grade",
            "program", "student_category", "submission_status", "validation_status"
        ]

        submissions = frappe.get_all(
            "Merit Score Submission",
            filters=filters,
            fields=fields,
            order_by="total_merit_score desc, percentage_score desc"
        )

        # Apply maximum results limit
        if self.maximum_results and self.maximum_results > 0:
            submissions = submissions[:self.maximum_results]

        return submissions

    def generate_html_table(self, submissions):
        """Generate HTML table for merit list"""
        if not submissions:
            return "<p>No merit submissions found matching the criteria.</p>"

        html = """
        <table class="table table-striped table-bordered">
            <thead>
                <tr>
                    <th>Merit Rank</th>
                    <th>Category Rank</th>
                    <th>Applicant Name</th>
                    <th>Student Applicant</th>
                    <th>Program</th>
                    <th>Category</th>
                    <th>Merit Score</th>
                    <th>Percentage</th>
                    <th>Grade</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
        """

        for submission in submissions:
            html += f"""
                <tr>
                    <td>{submission.merit_rank or '-'}</td>
                    <td>{submission.category_rank or '-'}</td>
                    <td>{submission.applicant_name or ''}</td>
                    <td><a href="/app/student-applicant/{submission.student_applicant}">{submission.student_applicant}</a></td>
                    <td>{submission.program or ''}</td>
                    <td>{submission.student_category or 'General'}</td>
                    <td>{submission.total_merit_score}</td>
                    <td>{submission.percentage_score:.2f}%</td>
                    <td>{submission.merit_grade or ''}</td>
                    <td>
                        <span class="indicator {'green' if submission.validation_status == 'Validated' else 'orange'}">
                            {submission.submission_status}
                        </span>
                    </td>
                </tr>
            """

        html += """
            </tbody>
        </table>
        """

        return html

    def generate_summary(self, submissions):
        """Generate summary of merit list generation"""
        total_submissions = len(submissions)
        validated_count = len([s for s in submissions if s.validation_status == "Validated"])
        pending_count = total_submissions - validated_count

        # Category wise breakdown
        category_breakdown = {}
        for submission in submissions:
            category = submission.student_category or "General"
            if category not in category_breakdown:
                category_breakdown[category] = 0
            category_breakdown[category] += 1

        summary = f"""Generation Date: {today()}
Total Entries: {total_submissions}
Validated Entries: {validated_count}
Pending Validation: {pending_count}

Category-wise Breakdown:
"""

        for category, count in category_breakdown.items():
            summary += f"- {category}: {count} entries\n"

        if self.minimum_score:
            summary += f"\nMinimum Score Filter: {self.minimum_score}"

        if self.maximum_results:
            summary += f"\nResults Limited to: {self.maximum_results}"

        return summary

    @frappe.whitelist()
    def refresh_ranking(self):
        """Refresh merit rankings for all submissions"""
        from education_management.education_management.doctype.merit_score_submission.merit_score_submission import get_merit_ranking

        filters = self.get_filters()

        # Remove some filters that are not needed for ranking
        ranking_filters = {
            "academic_year": filters.get("academic_year")
        }

        if filters.get("program"):
            ranking_filters["program"] = filters["program"]

        # Generate rankings
        get_merit_ranking(
            program=ranking_filters.get("program"),
            academic_year=ranking_filters.get("academic_year")
        )

        frappe.msgprint("Merit rankings refreshed successfully")

        # Regenerate the list with updated rankings
        return self.generate_merit_list()

    @frappe.whitelist()
    def export_pdf(self):
        """Export merit list as PDF"""
        # This would be implemented based on your PDF generation requirements
        frappe.msgprint("PDF export functionality to be implemented")

    @frappe.whitelist()
    def export_excel(self):
        """Export merit list as Excel"""
        # This would be implemented based on your Excel generation requirements
        frappe.msgprint("Excel export functionality to be implemented")