from google.appengine.api import users
from google.appengine.ext import ndb
from models import Student, Assignment, GradeEntry, Course
import utils
import webapp2


class InsertCourseAction(webapp2.RequestHandler):
  def post(self):
    user = users.get_current_user()
    urlsafe_entity_key = self.request.get('course_key') # At present there is no way to edit a course, but that'll come. :)
    if len(urlsafe_entity_key) > 0:
      # Edit
      course_key = ndb.Key(urlsafe=urlsafe_entity_key)
      course = course_key.get()
    else:
      # Add
      course = Course(parent=utils.get_user_parent_key(user))
    course.title = self.request.get('title')
    course.academic_quarter = self.request.get('academic_quarter')
    graders_emails = self.request.get('grader_emails')
    if len(graders_emails) > 0:
      graders_emails_list = graders_emails.split(",")
      for grader_email in graders_emails_list:
        course.grader_emails.append(grader_email.lower().trim())
    course.put()
    self.redirect("/?course=" + course.key.urlsafe())


class AddStudentAction(webapp2.RequestHandler):
  def post(self):
    urlsafe_entity_key = self.request.get('course_key')
    if len(urlsafe_entity_key) > 0:
      course_key = ndb.Key(urlsafe=urlsafe_entity_key)
      rose_username = self.request.get('rose_username')
      new_student = Student(parent=course_key,
                            id=rose_username,
                            first_name=self.request.get('first_name'),
                            last_name=self.request.get('last_name'),
                            rose_username=rose_username,
                            team=self.request.get('team'))
      new_student.put()
    self.redirect("/")


class InsertAssignmentAction(webapp2.RequestHandler):
  def post(self):
    urlsafe_entity_key = self.request.get('course_key')
    if len(urlsafe_entity_key) > 0:
      course_key = ndb.Key(urlsafe=urlsafe_entity_key)
      urlsafe_entity_key = self.request.get('assignment_entity_key')
      if len(urlsafe_entity_key) > 0:
        # Edit
        assignment_key = ndb.Key(urlsafe=urlsafe_entity_key)
        assignment = assignment_key.get()
      else:
        # Add
        assignment = Assignment(parent=course_key)
      assignment.name = self.request.get('assignment_name')
      assignment.put()
      self.redirect("/?assignment=" + assignment.key.urlsafe())
    else:
      self.redirect("/")


class AddSingleGradeEntryAction(webapp2.RequestHandler):
  def post(self):
    assignment_key = ndb.Key(urlsafe=self.request.get('assignment_key'))
    student_key = ndb.Key(urlsafe=self.request.get('student_key'))
    student = student_key.get()
    score = self.request.get('score')
    new_grade_entry = GradeEntry(parent=assignment_key,
                                 id=student.rose_username,
                                 assignment_key=assignment_key,
                                 student_key=student_key,
                                 score=score)
    new_grade_entry.put()
    self.redirect("/?assignment=" + assignment_key.urlsafe())


class AddTeamGradeEntryAction(webapp2.RequestHandler):
  def post(self):
    assignment_key = ndb.Key(urlsafe=self.request.get('assignment_key'))
    score = self.request.get('score')
    team = self.request.get('team')
    urlsafe_course_key = self.request.get('course_key')
    if len(urlsafe_course_key) > 0:
      course_key = ndb.Key(urlsafe=urlsafe_course_key)
      student_query = Student.query(Student.team==team, ancestor=course_key)
      for student in student_query:
          new_grade_entry = GradeEntry(parent=assignment_key,
                                       id=student.rose_username,
                                       assignment_key=assignment_key,
                                       student_key=student.key,
                                       score=score)
          new_grade_entry.put()
    self.redirect("/?assignment=" + assignment_key.urlsafe())

