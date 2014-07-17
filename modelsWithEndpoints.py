'''
Created on Jul 16, 2014

@author: boutell
'''

import endpoints
from endpoints_proto_datastore.ndb.model import EndpointsModel
from google.appengine.ext import ndb

class Assignment(EndpointsModel):
    _message_fields_schema = ("entityKey", "name") 
    name = ndb.StringProperty()
    owner_email = ndb.StringProperty()
    last_touch_date_time = ndb.DateTimeProperty(auto_now=True)
    
class GradeEntry(EndpointsModel):
    _message_fields_schema = ("entityKey", "student_name", "score", "assignment_key") 
    student_name = ndb.StringProperty()
    score = ndb.IntegerProperty()
    assignment_key = ndb.KeyProperty(kind=Assignment)


    
    
    