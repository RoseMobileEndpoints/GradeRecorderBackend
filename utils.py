from google.appengine.ext import ndb
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError
from models import Assignment, Student, GradeEntry, UserState


def get_user_parent_key(user):
  return ndb.Key("Entity", user.email().lower())


def get_user_state(user):
  user_state = UserState.get_by_id(user.email().lower())
  if user_state == None:
    user_state = UserState(id=user.email().lower())
    user_state.put()
  return user_state


def clear_user_state(user):
  """ Clears the user state. """
  user_state = UserState.get_by_id(user.email().lower())
  user_state.course_key = None
  user_state.assignment_key = None
  user_state.put()


def get_assignments(course_key):
  """ Gets all of the assignments for this course and makes a key map for them. """
  assignments = Assignment.query(ancestor=course_key).order(Assignment.name).fetch()
  assignments_map = {}
  for assignment in assignments:
    assignments_map[assignment.key] = assignment
  return assignments, assignments_map


def get_students(course_key):
  """ Gets all of the students for this user and makes a key map for them. """
  students = Student.query(ancestor=course_key).order(Student.rose_username).fetch()
  students_map = {}
  teams = []
  for student in students:
    students_map[student.key] = student
    if student.team not in teams:
      teams.append(student.team)
  return students, students_map, sorted(teams)


def get_grade_entries(course_key, assignments_map, students_map):
  """ Gets all of the grade entries for this user.
        Replaces the assignment_key and student_key with an assignment and student. """
  grade_entries = GradeEntry.query(ancestor=course_key).fetch()
  for grade_entry in grade_entries:
    grade_entry.assignment = assignments_map[grade_entry.assignment_key]
    grade_entry.student = students_map[grade_entry.student_key]
  return grade_entries


def remove_all_grades_for_assignment(user, assignment_key):
  """ Removes all grades for the given assignment. """
  grades_for_assignment_query = GradeEntry.query(ancestor=assignment_key)
  for grade in grades_for_assignment_query:
    grade.key.delete()


def remove_all_grades_for_student(course_key, student_key):
  """ Removes all grades for the given student. """
  grades_for_student_query = GradeEntry.query(GradeEntry.student_key==student_key, ancestor=course_key)
  for grade in grades_for_student_query:
    grade.key.delete()


def delete_all_course_entities(course_key):
  """ Removes all grades, all students, and all assignments for a course. (use with caution) """
  remove_all_students(course_key, delete_assignments=True)


def remove_all_students(course_key, delete_assignments=False):
  """ Removes all grades and all students for a course. (use with caution) """
  keys_to_delete = []
  all_grades_query = GradeEntry.query(ancestor=course_key)
  for grade in all_grades_query:
    keys_to_delete.append(grade.key)
  all_students_query = Student.query(ancestor=course_key)
  for student in all_students_query:
    keys_to_delete.append(student.key)
  if delete_assignments:
    all_assignments_query = Assignment.query(ancestor=course_key)
    for assignment in all_assignments_query:
      keys_to_delete.append(assignment.key)
  ndb.delete_multi(keys_to_delete)


def get_assignment_and_course_from_urlsafe_assignment_key(urlsafe_assignment_key):
  """ Gets the assignment from the urlsafe key and the associated course. """
  try:
    assignment_key = ndb.Key(urlsafe=urlsafe_assignment_key)
    assignment = assignment_key.get()
    course_key = assignment.key.parent()
    course = course_key.get()
    return assignment, course
  except ProtocolBufferDecodeError:
    return None


def get_course_from_urlsafe_key(urlsafe_course_key):
  """ Gets the course from the urlsafe key. """
  try:
    course_key = ndb.Key(urlsafe=urlsafe_course_key)
    return course_key.get()
  except ProtocolBufferDecodeError:
    return None


def get_any_course_for_user(user):
  """ Searches for any course connected to this user and returns it. """
  # TODO: Implement
  pass


def one_decimal_point_format(value):
  try:
    rounded_value = round(value, 1)
    if rounded_value * 10 % 10 == 0:
      return "%.0f" % rounded_value
    return "%.1f" % rounded_value
  except:
    return value

