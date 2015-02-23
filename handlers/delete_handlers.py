from google.appengine.api import users
from google.appengine.ext import ndb
import utils
import webapp2

class DeleteCourseAction(webapp2.RequestHandler):
  def post(self):
    user = users.get_current_user()
    course_key = ndb.Key(urlsafe=self.request.get('course_to_delete_key'))
    if utils.get_user_parent_key(user) == course_key.parent() or users.is_current_user_admin():
      utils.delete_all_course_entities(course_key)
      course_key.delete()
      utils.clear_user_state(user)
    self.redirect("/")


class RemoveUserAsGraderAction(webapp2.RequestHandler):
  def post(self):
    user = users.get_current_user()
    email_to_remove = user.email().lower()
    course_key = ndb.Key(urlsafe=self.request.get('course_key'))
    course = course_key.get()
    if email_to_remove in course.grader_emails:
      course.grader_emails.remove(email_to_remove)
      course.put()
      utils.clear_user_state(user)
    self.redirect("/")


class DeleteStudentAction(webapp2.RequestHandler):
  def post(self):
    user = users.get_current_user()
    if self.request.get('student_to_delete_key') == "AllStudents":
      utils.remove_all_students(user)
    else:
      student_key = ndb.Key(urlsafe=self.request.get('student_to_delete_key'))
      utils.remove_all_grades_for_student(user, student_key)
      student_key.delete();
    self.redirect(self.request.referer)


class DeleteAssignmentAction(webapp2.RequestHandler):
  def post(self):
    user = users.get_current_user()
    assignment_key = ndb.Key(urlsafe=self.request.get('assignment_to_delete_key'))
    utils.remove_all_grades_for_assignment(user, assignment_key)
    assignment_key.delete();
    self.redirect(self.request.referer)


class DeleteGradeEntryAction(webapp2.RequestHandler):
  def post(self):
    grade_entry_key = ndb.Key(urlsafe=self.request.get('grade_entry_to_delete_key'))
    grade = grade_entry_key.get()
    urlsafe_assignment_key = grade.assignment_key.urlsafe()
    grade_entry_key.delete();
    self.redirect("/?assignment=" + urlsafe_assignment_key)

