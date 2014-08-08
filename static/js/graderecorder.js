/**
 * @fileoverview
 * Provides methods for the UI and interaction with the Grade Recorder Endpoints API.
 *
 * @author fisherds@google.com (Dave Fisher)
 */

/** namespace. */
var rh = rh || {};
rh.gr = rh.gr || {};

/**
 * Current assignment id being viewed.
 * @type {string}
 */
rh.gr.currentAssignmentKey = null;

/**
 * Enables the button callbacks in the UI.
 */
rh.gr.enableButtons = function() {
	$('#add-student-modal').on('shown.bs.modal', function() {
		$("input[name='first_name']").focus();
	});

	$('#add-assignment-modal').on('shown.bs.modal', function() {
		$("input[name='assignment_name']").focus();
	});

	$('#add-grade-entry-modal').on('shown.bs.modal', function() {
		// CONSIDER: Attempt to guess the next student needing a grade.
		if (rh.gr.currentAssignmentKey.length > 0) {
			$("select[name=assignment_key]").val(rh.gr.currentAssignmentKey);
		}
		$("input[name='score']").focus();
	});

	// Within Grade entry modal.
	$('.btn-toggle').click(function() {
		// Change which button is active primary vs default
		$(this).find('.btn').toggleClass('active');
		if ($(this).find('.btn-primary').size() > 0) {
			$(this).find('.btn').toggleClass('btn-primary');
		}
		$(this).find('.btn').toggleClass('btn-default');
	});

	$("#add-grade-by-student").click(function() {
		$("#grade-entry-type-input").val("SingleGradeEntry");
		$("#grade-entry-by-student-form-group").show();
		$("#grade-entry-by-team-form-group").hide();
	});

	$("#add-grade-by-team").click(function() {
		$("#grade-entry-type-input").val("TeamGradeEntry");
		$("#grade-entry-by-student-form-group").hide();
		$("#grade-entry-by-team-form-group").show();
	});

	$("#bulk-import-file-upload-button").click(
			function() {
				$("#bulk-import-file-upload-chooser")
						.attr("accept", "text/csv").trigger("click");
			});

	$(".edit-student").click(function() {
		firstName = $(this).find(".first-name").html();
		lastName = $(this).find(".last-name").html();
		roseUsername = $(this).find(".rose-username").html();
		team = $(this).find(".team").html();
		$("#add-student-modal input[name=first_name]").val(firstName);
		$("#add-student-modal input[name=last_name]").val(lastName);
		$("#add-student-modal input[name=rose_username]").val(roseUsername);
		$("#add-student-modal input[name=team]").val(team);
		$("#add-student-modal-title").html("Update student info");
		localStorage.showStudentEditDeleteTable = "yes";
	});

	$(".delete-student").click(function() {
		firstName = $(this).find(".first-name").html();
		lastName = $(this).find(".last-name").html();
		entityKey = $(this).find(".entity-key").html();
		$("#delete-student-name").html(firstName + " " + lastName);
		$("input[name=student_to_delete_key]").val(entityKey);

		if (entityKey == "AllStudents") {
			$("#delete-student-modal-title").html("Delete ALL Students!");
			$("#delete-student-modal .single-delete-text").hide();
		} else {
			localStorage.showStudentEditDeleteTable = "yes";
			$("#delete-student-modal .all-delete-text").hide();
		}
	});
};

rh.gr.updateTable = function() {
	var table = $('#grade-entry-table').DataTable();
	table.search(rh.gr.currentAssignmentKey).draw();
};

// Navigation of grade entries.
$(document).ready(function() {
	rh.gr.enableButtons();
	rh.gr.currentAssignmentKey = $('.sidebar-link.active').attr('id');
	rh.gr.updateTable();
	$('.sidebar-link').click(function() {
		// Update the sidebar
		$('.sidebar-link').removeClass('active');
		$(this).addClass('active');
		// Update the list of grades shown in the table.
		rh.gr.currentAssignmentKey = $(this).attr('id');
		rh.gr.updateTable();
		$(".row-offcanvas").removeClass("active");
	});

	if (localStorage.showStudentEditDeleteTable) {
		$("#select-student-to-edit-modal").modal("show");
	    localStorage.removeItem("showStudentEditDeleteTable");
	};
});
