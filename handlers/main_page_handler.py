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
    user_state = utils.get_user_state(user)
    # Attempt to take the user to their last location.

    # Priority #1 Use the query parameters.
    if len(self.request.get("assignment")) > 0:
      assignment, course = utils.get_assignment_and_course_from_urlsafe_assignment_key(self.request.get("assignment"))
      if user_state.course_key != course.key or user_state.assignment_key != assignment.key:
        user_state.course_key = course.key
        user_state.assignment_key = assignment.key
        user_state.put()
    elif len(self.request.get("course")) > 0:
      course = utils.get_course_from_urlsafe_key(self.request.get("course"))
      if course != None:
        if user_state.course_key != course.key or user_state.assignment_key != None:
          user_state.course_key = course.key
          user_state.assignment_key = None
          user_state.put()

    if not course:
      # No query parameters. Use Priority #2 the user state.
      if user_state:
        if user_state.assignment_key:
          assignment = user_state.assignment_key.get()
          course = user_state.course_key.get()
        elif user_state.course_key:
          course = user_state.course_key.get()

    if not course:
      # No user state set.  Use Priority #3 any course for the user.
      course = Course.query(ancestor=utils.get_user_parent_key(user)).get()

    if course:
      if utils.get_user_parent_key(user) == course.key.parent() or \
          user.email().lower() in course.grader_emails or users.is_current_user_admin():
        self.load_page_for_course(user, course, assignment)
      else:
        utils.clear_user_state(user) # Trying to help with a user that had the rug pulled out from under them.
        self.response.out.write("Access denied.") # There are fancier ways to do this but this is fine.
        return
    else:
      self.load_courseless_page(user)


  def load_page_for_course(self, user, course, assignment):
    assignments, assignments_map = utils.get_assignments(course.key)
    students, students_map, teams = utils.get_students(course.key)
    grade_entries = utils.get_grade_entries(course.key, assignments_map, students_map)

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
    self.response.out.write(template.render({'course': course,
                                             'is_owner': course.key.parent() == utils.get_user_parent_key(user) or users.is_current_user_admin(),
                                             'assignments': assignments,
                                             'active_assignment': assignment.key.urlsafe() if assignment else "",
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
