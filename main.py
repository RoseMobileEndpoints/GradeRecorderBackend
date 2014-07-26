#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os

from google.appengine.api import users
from google.appengine.ext import ndb

from models import Student, Assignment, GradeEntry
import logging

# Jinja environment instance necessary to use Jinja templates.
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)), autoescape=True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return
        assignments, assignments_map = get_assignments(user)
        students, students_map, teams = get_students(user)
        grade_entries = get_grade_entries(user, assignments_map, students_map)
        # Optional adding some meta data about the assignments for the badge icon.
        assignment_badge_data = {}
        for assignment in assignments:
            assignment_badge_data[assignment.key] = [0, 0]  # Count, Score Accumulator
        for grade_entry in grade_entries:
            assignment_badge_data[grade_entry.assignment_key][0] += 1
            assignment_badge_data[grade_entry.assignment_key][1] += grade_entry.score
        for assignment in assignments:
            metadata = assignment_badge_data[assignment.key]
            if metadata[0] > 0:
                metadata.append(metadata[1] / metadata[0])  # Average
            else:
                metadata.append("na")  # Average is NA
        template = jinja_env.get_template("templates/graderecorder.html")
        self.response.out.write(template.render({'assignments': assignments,
                                                 'active_assignemnt': self.request.get('active_assignemnt'),
                                                 'students': students,
                                                 'teams': teams,
                                                 'grade_entries': grade_entries,
                                                 'assignment_badge_data': assignment_badge_data,
                                                 'user_email': user.email(),
                                                 'logout_url': users.create_logout_url("/")}))

    def post(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return
        next_active_assignemnt = None
        if (self.request.get('type') == 'Student'):
            new_student = Student(parent=get_parent_key(user),
                                  first_name=self.request.get('first_name'),
                                  last_name=self.request.get('last_name'),
                                  rose_username=self.request.get('rose_username'),
                                  team=self.request.get('team'))
            new_student.put()
        elif (self.request.get('type') == 'Assignment'):
            new_assignment = Assignment(parent=get_parent_key(user),
                                        name=self.request.get('assignment_name'))
            new_assignment.put()
            next_active_assignemnt = new_assignment.key.urlsafe()
        elif (self.request.get('type') == 'SingleGradeEntry'):
            assignment_key = ndb.Key(urlsafe=self.request.get('assignment_key'))
            student_key = ndb.Key(urlsafe=self.request.get('student_key'))
            student = student_key.get()
            score = int(self.request.get('score'))
            new_grade_entry = GradeEntry(parent=assignment_key,
                                         id=student.rose_username,
                                         assignment_key=assignment_key,
                                         student_key=student_key,
                                         score=score)
            new_grade_entry.put()
            next_active_assignemnt = assignment_key.urlsafe()
        elif (self.request.get('type') == 'TeamGradeEntry'):
            assignment_key = ndb.Key(urlsafe=self.request.get('assignment_key'))
            score = int(self.request.get('score'))
            team = self.request.get('team')
            student_query = Student.query(Student.team==team, ancestor=get_parent_key(user))
            for student in student_query:
                new_grade_entry = GradeEntry(parent=assignment_key,
                                             id=student.rose_username,
                                             assignment_key=assignment_key,
                                             student_key=student.key,
                                             score=score)
                new_grade_entry.put()
            next_active_assignemnt = assignment_key.urlsafe()
        if next_active_assignemnt:
          self.redirect("/?active_assignemnt=" + next_active_assignemnt)
        else:
          self.redirect("/")

def get_parent_key(user):
    return ndb.Key("Entity", user.email().lower())

def get_assignments(user):
    """ Gets all of the assignments for this user and makes a key map for them. """
    assignments = Assignment.query(ancestor=get_parent_key(user)).order(Assignment.name).fetch()
    assignments_map = {}
    for assignment in assignments:
        assignments_map[assignment.key] = assignment
    return assignments, assignments_map


def get_students(user):
    """ Gets all of the students for this user and makes a key map for them. """
    students = Student.query(ancestor=get_parent_key(user)).order(Student.rose_username).fetch()
    students_map = {}
    teams = []
    for student in students:
        students_map[student.key] = student
        if student.team not in teams:
          teams.append(student.team)
    return students, students_map, teams


def get_grade_entries(user, assignments_map, students_map):
    """ Gets all of the grade entries for this user.
          Replaces the assignment_key and student_key with an assignment and student. """
    grade_entries = GradeEntry.query(ancestor=get_parent_key(user)).fetch()
    for grade_entry in grade_entries:
        grade_entry.assignment = assignments_map[grade_entry.assignment_key]
        grade_entry.student = students_map[grade_entry.student_key]
    return grade_entries

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
