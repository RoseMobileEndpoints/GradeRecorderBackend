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
import os

from handlers import main_page_handler, insert_handlers, delete_handlers, csv_handlers
import jinja2
import utils
import webapp2


# Jinja environment instance necessary to use Jinja templates.
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
                               autoescape=True)
jinja_env.filters["one_decimal_point_format"] = utils.one_decimal_point_format

app = webapp2.WSGIApplication([
    ("/", main_page_handler.GradeRecorderPage),
    ("/action/insert_course", insert_handlers.InsertCourseAction),
    ("/action/add_student", insert_handlers.AddStudentAction),
    ("/action/insert_assignment", insert_handlers.InsertAssignmentAction),
    ("/action/add_single_grade_entry", insert_handlers.AddSingleGradeEntryAction),
    ("/action/add_team_grade_entry", insert_handlers.AddTeamGradeEntryAction),
    ("/action/delete_student", delete_handlers.DeleteStudentAction),
    ("/action/delete_assignment", delete_handlers.DeleteAssignmentAction),
    ("/action/delete_grade_entry", delete_handlers.DeleteGradeEntryAction),
    ("/action/bulk_student_import", csv_handlers.BulkStudentImportAction),
    ("/action/grade_recorder_grades.csv", csv_handlers.ExportCsvAction)
], debug=True)
