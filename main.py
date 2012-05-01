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
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from models import Project
from urlparse import urlparse
from datetime import datetime, timedelta
from operator import itemgetter
import webapp2
import os
import kickparser

class MainHandler(webapp2.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, {}))
                
class ProjectHandler(webapp2.RequestHandler):
    def get(self):
        budget = int(self.request.get('b'))
        
        p = Project.all()
        projects = p.filter('left < ', budget)
        project_dicts = []
        for project in projects:
            project_dict = {}
            project_dict['link'] = project.link + '/widget/card.html'
            project_dict['left'] = project.left
            timeleft =  project.end - datetime.now() + timedelta(0, 14400)
            hours = str(timeleft.seconds / 3600)
            if timeleft.days < 0:
                timeleft_str = hours
            else:
                timeleft_str = str(timeleft.days) + ' days, ' + hours + ' hours'
            project_dict['time'] = timeleft_str
            project_dicts.append(project_dict)
        
        project_dicts.sort(key=itemgetter('time'))
        template_dict = {}
        template_dict['project_dicts'] = project_dicts
        template_dict['budget'] = budget
        template_dict['projects'] = len(project_dicts)
        path = os.path.join(os.path.dirname(__file__), 'templates/projects.html')
        self.response.out.write(template.render(path, template_dict))

        

        
app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/project', ProjectHandler)],
                              debug=True)
