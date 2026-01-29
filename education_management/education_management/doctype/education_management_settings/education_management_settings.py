import frappe
from frappe.model.document import Document
from frappe.utils import cint


class EducationManagementSettings(Document):
    def validate(self):
        self.validate_file_size()

    def validate_file_size(self):
        if self.max_file_size_mb and self.max_file_size_mb <= 0:
            frappe.throw("Maximum file size must be greater than 0")

        if self.max_file_size_mb and self.max_file_size_mb > 100:
            frappe.throw("Maximum file size cannot exceed 100 MB")

    def on_update(self):
        # Clear cache when settings are updated
        frappe.clear_cache()


@frappe.whitelist()
def get_merit_list_settings():
    """Get education management settings for merit list"""
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
        "auto_generate_rankings": cint(settings.auto_generate_rankings)
    }


@frappe.whitelist()
def is_merit_list_enabled():
    """Check if merit list process is enabled"""
    try:
        settings = frappe.get_single("Education Management Settings")
        return cint(settings.enable_merit_list_process)
    except:
        return 0


@frappe.whitelist()
def is_merit_list_mandatory():
    """Check if merit list is mandatory for admission"""
    try:
        settings = frappe.get_single("Education Management Settings")
        return cint(settings.merit_list_mandatory) and cint(settings.enable_merit_list_process)
    except:
        return 0