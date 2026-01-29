frappe.ui.form.on('Merit List Generation Tool', {
    refresh: function(frm) {
        frm.page.set_title(__('Merit List Generation Tool'));

        // Set default academic year if empty
        if (!frm.doc.academic_year) {
            frm.set_value('academic_year', frappe.defaults.get_user_default('academic_year'));
        }
    },

    generate_list: function(frm) {
        if (!frm.doc.academic_year) {
            frappe.msgprint(__('Please select an Academic Year'));
            return;
        }

        frm.call({
            method: 'generate_merit_list',
            doc: frm.doc,
            callback: function(r) {
                if (r.message) {
                    frm.reload_doc();
                }
            }
        });
    },

    refresh_ranking: function(frm) {
        if (!frm.doc.academic_year) {
            frappe.msgprint(__('Please select an Academic Year'));
            return;
        }

        frappe.confirm(
            __('This will recalculate merit rankings for all submissions. Continue?'),
            function() {
                frm.call({
                    method: 'refresh_ranking',
                    doc: frm.doc,
                    callback: function(r) {
                        if (r.message) {
                            frm.reload_doc();
                        }
                    }
                });
            }
        );
    },

    export_pdf: function(frm) {
        if (!frm.doc.merit_list_results) {
            frappe.msgprint(__('Please generate merit list first'));
            return;
        }

        frm.call({
            method: 'export_pdf',
            doc: frm.doc
        });
    },

    export_excel: function(frm) {
        if (!frm.doc.merit_list_results) {
            frappe.msgprint(__('Please generate merit list first'));
            return;
        }

        frm.call({
            method: 'export_excel',
            doc: frm.doc
        });
    },

    program: function(frm) {
        // Clear results when filter changes
        frm.set_value('merit_list_results', '');
        frm.set_value('generation_summary', '');
    },

    student_category: function(frm) {
        // Clear results when filter changes
        frm.set_value('merit_list_results', '');
        frm.set_value('generation_summary', '');
    },

    minimum_score: function(frm) {
        // Clear results when filter changes
        frm.set_value('merit_list_results', '');
        frm.set_value('generation_summary', '');
    },

    include_pending: function(frm) {
        // Clear results when filter changes
        frm.set_value('merit_list_results', '');
        frm.set_value('generation_summary', '');
    }
});