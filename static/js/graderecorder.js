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

  $('#display-add-assignment-modal').click(function() {
    $('#add-assignment-modal').modal('show');
  });


  $('#display-add-student-modal').click(function() {
    $('#add-student-modal').modal('show');
  });

	$('#display-add-grade-entry-modal').click(function() {
		// Prepare the grade entry modal
	  // TODO: Select the assignment based on what the user is viewing.

		$('#add-grade-entry-modal').modal('show');
	});
};

rh.gr.updateTable = function() {

  console.log("Consider: Filter instead of search")
  console.log("TODO: Use the KEY instead!" + rh.gr.currentAssignmentKey)

  var table = $('#grade-entry-table').DataTable();
  table.search(assignments_name_map[rh.gr.currentAssignmentKey]).draw();
}

// Navigation of grade entries.
$(document).ready(function(){
  rh.gr.enableButtons();
	rh.gr.currentAssignmentKey = $('.sidebar-link:first-child').attr('id');
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
