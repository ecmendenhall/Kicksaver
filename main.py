#!/usr/bin/env python

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
        project_dicts = []
        input_error = False
        budget_toolow = False
        
        sort = self.request.get('sort')
        if sort not in ['soon', 'close']:
            sort = 'soon'

        budget = self.request.get('b')
        try:
            initial_budget = int(float(budget))
            budget = initial_budget
        except ValueError:
            initial_budget = 0
            budget = initial_budget
                   
        p = Project.all()
        projects = p.filter('left < ', budget)
        if projects.count() == 0:
            budget_toolow = True
            while projects.count() < 4:
                budget = budget + 5
                p = Project.all()
                projects = p.filter('left < ', budget)
        for project in projects:
            project_dict = {}
            project_dict['link'] = project.link + '/widget/card.html'
            project_dict['left'] = project.left
            timeleft =  project.end - datetime.now() + timedelta(0, 14400)
            project_dict['timeleft'] = timeleft
            hours = str(timeleft.seconds / 3600)
            if timeleft.days < 0:
                timeleft_str = hours
            else:
                timeleft_str = str(timeleft.days) + ' days, ' + hours + ' hours'
            project_dict['time'] = timeleft_str
            project_dicts.append(project_dict)
        project_dicts.sort(key=lambda i: i['timeleft'])
        if sort == 'close':
            project_dicts.sort(key=itemgetter('left'))

        template_dict = {}
        template_dict['project_dicts'] = project_dicts
        template_dict['initial_budget'] = initial_budget
        template_dict['budget'] = budget
        template_dict['projects'] = len(project_dicts)
        template_dict['sort'] = sort
        template_dict['budget_toolow'] = budget_toolow
        
        path = os.path.join(os.path.dirname(__file__), 'templates/projects.html')
        self.response.out.write(template.render(path, template_dict))
        
app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/project', ProjectHandler)],
                              debug=True)
