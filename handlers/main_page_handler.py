import logging

from google.appengine.api import users
import main
from models import UserState, Course
import utils
import webapp2


class GradeRecorderPage(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if not user:
      template = main.jinja_env.get_template("templates/no_courses.html")
      self.response.out.write(template.render({'login_url': users.create_login_url(self.request.uri)}))
      return
    assignment = None
    course = None
    user_state = UserState.get_by_id(user.email().lower())
    # Attempt to take the user to their last location.

    # Priority #1 Use the query parameters.
    if len(self.request.get("assignment")) > 0:
      assignment, course = utils.get_assignment_and_course_from_urlsafe_assignment_key(self.request.get("assignment"))
      if user_state.course != course or user_state.assignment != assignment:
        user_state.course = course
        user_state.assignment = assignment
        user_state.put()
    elif len(self.request.get("course")) > 0:
      course = utils.get_course_from_urlsafe_key(self.request.get("course"))
      if user_state.course != course or user_state.assignment != None:
        user_state.course = course
        user_state.assignment = None
        user_state.put()

    if not course:
      # No query parameters. Use Priority #2 the user state.
      if user_state:
        assignment = user_state.assignment_key.get()
        course = user_state.course_key.get()

    if not course:
      # No user state set.  Use Priority #3 any course for the user.
      course = Course.query(ancestor=utils.get_parent_key(user)).get()

    if course:
      self.load_page_for_course(user, course, assignment)
    else:
      self.load_courseless_page(user)

  def load_page_for_course(self, course, user):
    assignments, assignments_map = utils.get_assignments(user)
    students, students_map, teams = utils.get_students(user)
    grade_entries = utils.get_grade_entries(user, assignments_map, students_map)

    # Optional adding some meta data about the assignments for the badge icon.
    assignment_badge_data = {}
    for assignment in assignments:
      assignment_badge_data[assignment.key] = [0, 0]  # Accumulator for [Total Count, Total Score]
    for grade_entry in grade_entries:
      try:
        grade_as_float = float(grade_entry.score)
        assignment_badge_data[grade_entry.assignment_key][0] += 1
        assignment_badge_data[grade_entry.assignment_key][1] += grade_as_float
      except ValueError:
        continue
    for assignment in assignments:
      metadata = assignment_badge_data[assignment.key]
      if metadata[0] > 0:
        metadata.append(metadata[1] / metadata[0])  # Average = Total Score / Total Count
      else:
        metadata.append("na")  # Average is NA
    template = main.jinja_env.get_template("templates/graderecorder.html")
    self.response.out.write(template.render({'assignments': assignments,
                                             'active_assignment': self.request.get('active_assignment'),
                                             'students': students,
                                             'teams': teams,
                                             'grade_entries': grade_entries,
                                             'assignment_badge_data': assignment_badge_data,
                                             'user_email': user.email(),
                                             'logout_url': users.create_logout_url("/")}))

  def load_courseless_page(self, user):
    template = main.jinja_env.get_template("templates/no_courses.html")
    self.response.out.write(template.render({'user_email': user.email(),
                                             'logout_url': users.create_logout_url("/")}))
