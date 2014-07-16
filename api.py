'''
Created on Jul 16, 2014

@author: Matt Boutell
'''

import protorpc
import endpoints
from models import Assignment, GradeEntry
from google.appengine.ext import ndb

# For authentication
WEB_CLIENT_ID = "3607967651-5nqg6qis8ivo294oenp8nff9k35dp70h.apps.googleusercontent.com"
ANDROID_CLIENT_ID = ""
IOS_CLIENT_ID = ""

@endpoints.api(name="graderecorder", version="v1", description="Grade Recorder API",
               hostname="boutell-grade-recorder-2", audiences=[WEB_CLIENT_ID],
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID, ANDROID_CLIENT_ID, IOS_CLIENT_ID])
class GradeRecorderApi(protorpc.remote.Service):

    @Assignment.query_method(user_required=True, query_fields=("limit", "order", "pageToken"), 
                             name="assignment.list", path="assignment/list", http_method="GET")
    def assignment_list(self, query):
        """ List all the assignments owned by the user """
        filtered_query = query.filter(Assignment.owner_email == endpoints.get_current_user().email().lower())
        return filtered_query

    @GradeEntry.query_method(user_required=True, query_fields=("limit", "order", "pageToken", "assignment_key"),
                             name="gradeentry.list", path="gradeentry/list/{assignment_key}", http_method="GET")
    def gradeentry_list(self, query):
        """ List all the grade entries for the given assignment key """
        return query

    @Assignment.method(user_required= True, name="assignment.insert", path="assignment/insert", http_method="POST")
    def assignment_insert(self, assignment):
        """ Add or update an assignment owned by the given user """
        if assignment.from_datastore:
            assignment_with_parent = assignment
        else:
            email = endpoints.get_current_user().email().lower()
            assignment_with_parent = Assignment(parent = ndb.Key("Entity", email), 
                                                name = assignment.name,
                                                owner_email = email)
        assignment_with_parent.put()
        return assignment_with_parent 
    
    @GradeEntry.method(user_required= True, name="gradeentry.insert", path="gradeentry/insert", http_method="POST")
    def gradeentry_insert(self, grade_entry):
        """ Add or update a grade entry for an assignment """
        if grade_entry.from_datastore:
            grade_entry_with_parent = grade_entry
        else:
            grade_entry_with_parent = GradeEntry(parent= grade_entry.assignment_key, 
                                                 student_name = grade_entry.student_name, 
                                                 score = grade_entry.score, 
                                                 assignment_key = grade_entry.assignment_key) 
        grade_entry_with_parent.put()
        return grade_entry_with_parent

    @Assignment.method(user_required= True, request_fields = ("entityKey",), 
                       name="assignment.delete", path="assignment/delete/{entityKey}", http_method="DELETE")
    def assignment_delete(self, assignment):
        """ Delete the assignment with the given key, plus all the associated grade entries """
        if not assignment.from_datastore:
            raise endpoints.NotFoundException("No assignment found for the given key")
        children = GradeEntry.query(ancestor=assignment.key)
        for grade_entry in children:
            grade_entry.key.delete()
        assignment.key.delete()
        return Assignment(name="deleted")

    @GradeEntry.method(user_required= True, request_fields = ("entityKey",), 
                       name="gradeentry.delete", path="gradeentry/delete/{entityKey}", http_method="DELETE")
    def gradeentry_delete(self, grade_entry):
        """ Delete the grade entry with the given key """
        if not grade_entry.from_datastore:
            raise endpoints.NotFoundException("No grade entry found for the given key")
        grade_entry.key.delete()
        return GradeEntry(student_name="deleted")


app = endpoints.api_server([GradeRecorderApi], restricted=False)


