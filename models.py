from google.appengine.ext import ndb
from endpoints_proto_datastore.ndb.model import EndpointsModel


class Course(EndpointsModel):
  """ Course. """
  _message_fields_schema = ("entityKey", "title", "academic_quarter", "owner_email", "grader_emails")
  title = ndb.StringProperty()
  academic_quarter = ndb.StringProperty()
  owner_email = ndb.StringProperty()
  grader_emails = ndb.StringProperty(repeated=True)


class Student(EndpointsModel):
  """ Student. """
  _message_fields_schema = ("entityKey", "first_name", "last_name", "rose_username", "team")
  first_name = ndb.StringProperty()
  last_name = ndb.StringProperty()
  rose_username = ndb.StringProperty()
  team = ndb.StringProperty(default="None")


class Assignment(EndpointsModel):
  """ Assignment. """
  _message_fields_schema = ("entityKey", "name")
  name = ndb.StringProperty()


class GradeEntry(EndpointsModel):
  """ Score for a student on an assignment. """
  _message_fields_schema = ("entityKey", "score", "student_key", "assignment_key")
  score = ndb.StringProperty()
  student_key = ndb.KeyProperty(kind=Student)
  assignment_key = ndb.KeyProperty(kind=Assignment)


class UserState(EndpointsModel):
  """ Keeps a reference to the most recent course and assignment for this user. """
  active_course_key = ndb.KeyProperty(kind=Course)
  active_assignment_key = ndb.KeyProperty(kind=Assignment)
