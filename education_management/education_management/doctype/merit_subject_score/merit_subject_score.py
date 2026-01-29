import frappe
from frappe.model.document import Document
from frappe.utils import flt


class MeritSubjectScore(Document):
    def validate(self):
        self.calculate_percentage()
        self.validate_score()
        self.calculate_grade()

    def calculate_percentage(self):
        if self.score and self.maximum_score:
            self.percentage = flt(self.score / self.maximum_score * 100, 2)

    def validate_score(self):
        if self.score and self.maximum_score:
            if self.score > self.maximum_score:
                frappe.throw(f"Score for {self.subject} cannot be greater than maximum score")

            if self.score < 0:
                frappe.throw(f"Score for {self.subject} cannot be negative")

    def calculate_grade(self):
        if self.percentage:
            percentage = flt(self.percentage)
            if percentage >= 95:
                self.grade = "A+"
            elif percentage >= 90:
                self.grade = "A"
            elif percentage >= 85:
                self.grade = "B+"
            elif percentage >= 80:
                self.grade = "B"
            elif percentage >= 75:
                self.grade = "C+"
            elif percentage >= 70:
                self.grade = "C"
            elif percentage >= 60:
                self.grade = "D"
            else:
                self.grade = "F"