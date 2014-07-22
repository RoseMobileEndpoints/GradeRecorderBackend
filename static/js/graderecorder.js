/**
 * @fileoverview
 * Provides methods for the UI and interaction with the Grade Recorder Endpoints API.
 *
 * @author fisherds@google.com (Dave Fisher)
 * @author danielholevoet@google.com (Dan Holevoet)
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
  $('#display-add-student-modal').click(function() {
    $('#add-student-modal').on('shown.bs.modal', function () {
      $("input[name='first_name']").focus();
    }).modal('show');
  });

  $('#display-add-assignment-modal').click(function() {
    $('#add-assignment-modal').on('shown.bs.modal', function () {
      $("input[name='assignment_name']").focus();
    }).modal('show');
  });

	$('#display-add-grade-entry-modal').click(function() {
		$('#add-grade-entry-modal').on('shown.bs.modal', function () {
		  // TODO: Attempt to guess the next student needing a grade.
		  if (rh.gr.currentAssignmentKey.length > 0) {
		    $("select[name=assignment_key]").val(rh.gr.currentAssignmentKey);
		  }
      $("input[name='score']").focus();
    }).modal('show');
	});
};


rh.gr.updateTable = function() {
  var table = $('#grade-entry-table').DataTable();
  table.search(rh.gr.currentAssignmentKey).draw();
};


// Navigation of grade entries.
$(document).ready(function(){
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
	})
});
