frappe.ui.form.on('Merit Score Submission', {
    refresh: function(frm) {
        // Add validation buttons if submitted and pending validation
        if (frm.doc.docstatus === 1 && frm.doc.validation_status === 'Pending') {
            // Add Validate button
            frm.add_custom_button(__('Validate'), function() {
                validate_merit_submission(frm, 'approve');
            }, __('Actions'));

            // Add Reject button
            frm.add_custom_button(__('Reject'), function() {
                validate_merit_submission(frm, 'reject');
            }, __('Actions'));
        }

        // Add document verification buttons if submitted and documents are pending
        if (frm.doc.docstatus === 1 && frm.doc.document_verification_status === 'Pending') {
            // Add Verify Documents button
            frm.add_custom_button(__('Verify Documents'), function() {
                update_document_verification(frm, 'Verified');
            }, __('Documents'));

            // Add Reject Documents button
            frm.add_custom_button(__('Reject Documents'), function() {
                update_document_verification(frm, 'Rejected');
            }, __('Documents'));
        }

        // Show validation info if already validated
        if (frm.doc.validation_status === 'Validated') {
            frm.dashboard.add_comment(__('Validated by {0} on {1}', [
                frm.doc.validated_by,
                frappe.datetime.str_to_user(frm.doc.validation_date)
            ]), 'green');
        }

        // Show rejection info if rejected
        if (frm.doc.validation_status === 'Rejected') {
            frm.dashboard.add_comment(__('Rejected'), 'red');
        }

        // Make fields read-only after validation unless settings allow modification
        if (frm.doc.validation_status === 'Validated') {
            check_modification_permission(frm);
        }

        // Make status fields read-only after submission for non-authorized users
        if (frm.doc.docstatus === 1) {
            frm.set_df_property('document_verification_status', 'read_only', 1);
            frm.set_df_property('validation_status', 'read_only', 1);
        }
    }
});

function validate_merit_submission(frm, action) {
    let title = action === 'approve' ? 'Validate Merit Submission' : 'Reject Merit Submission';
    let prompt_text = action === 'approve' ?
        'Are you sure you want to validate this merit submission?' :
        'Please provide reason for rejection:';

    if (action === 'reject') {
        frappe.prompt([
            {
                label: 'Rejection Reason',
                fieldname: 'reason',
                fieldtype: 'Small Text',
                reqd: 1
            }
        ], function(values) {
            submit_validation(frm, action, values.reason);
        }, title, __('Reject'));
    } else {
        frappe.confirm(prompt_text, function() {
            submit_validation(frm, action);
        });
    }
}

function submit_validation(frm, action, comments) {
    frappe.call({
        method: 'education_management.education_management.doctype.merit_score_submission.merit_score_submission.validate_merit_submission',
        args: {
            submission_name: frm.doc.name,
            action: action,
            comments: comments
        },
        callback: function(r) {
            if (r.message) {
                frm.reload_doc();
                frappe.show_alert({
                    message: action === 'approve' ?
                        __('Merit submission validated successfully') :
                        __('Merit submission rejected'),
                    indicator: action === 'approve' ? 'green' : 'red'
                });
            }
        }
    });
}

function update_document_verification(frm, status) {
    frappe.confirm(
        __('Are you sure you want to {0} the documents?', [status.toLowerCase()]),
        function() {
            frappe.call({
                method: 'education_management.education_management.doctype.merit_score_submission.merit_score_submission.update_document_verification',
                args: {
                    submission_name: frm.doc.name,
                    status: status
                },
                callback: function(r) {
                    if (r.message) {
                        frm.reload_doc();
                        frappe.show_alert({
                            message: __('Document verification updated to {0}', [status]),
                            indicator: status === 'Verified' ? 'green' : 'red'
                        });
                    }
                }
            });
        }
    );
}

function check_modification_permission(frm) {
    // Check if modification is allowed after validation
    frappe.call({
        method: 'education_management.utils.get_education_management_settings',
        callback: function(r) {
            if (r.message && !r.message.allow_score_modification_after_validation) {
                // Make score fields read-only
                let score_fields = [
                    'total_merit_score', 'maximum_possible_score',
                    'subject_scores', 'supporting_documents'
                ];

                score_fields.forEach(function(field) {
                    frm.set_df_property(field, 'read_only', 1);
                });

                // Show message about modification restriction
                frm.dashboard.add_comment(
                    __('Score modification is disabled after validation. Enable in Education Management Settings if needed.'),
                    'blue'
                );
            }
        }
    });
}