#!/usr/bin/env python

from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from models import Project
from urlparse import urlparse
from datetime import datetime, timedelta
from operator import itemgetter
import webapp2
import os
import kickparser
import json

class MainHandler(webapp2.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, {}))

class AboutHandler(webapp2.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'templates/about.html')
        self.response.out.write(template.render(path, {}))
                
class ProjectHandler(webapp2.RequestHandler):
    def get(self):
        def make_project_dict(project, project_list):
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
            project_list.append(project_dict)

        def get_next_page(cursor):
            p = Project.all().with_cursor(cursor)
            projects = p.filter('left < ', budget)
            page = projects.fetch(8)
            cursor = p.cursor()
            return page, cursor
        
        project_dicts = []
        input_error = False
        budget_toolow = False

        
        p = self.request.get('p')
        try:
            pages = int(p)
        except ValueError:
            pages = 0

        more = self.request.get('more')
        if more:
            pages += 1 
        
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
        all_projects = p.filter('left < ', budget)
        page = all_projects
        
        if all_projects.count() == 0:
            budget_toolow = True
            while all_projects.count() < 4:
                budget = budget + 5
                p = Project.all()
                all_projects = p.filter('left < ', budget)
            page = all_projects
        for project in page:
            make_project_dict(project, project_dicts)
        
        """if pages:
            for page in range(0, pages):
                page, cursor = get_next_page(cursor)
                for project in page:
                    make_project_dict(project, project_dicts)"""
        
        
        project_dicts.sort(key=lambda i: i['timeleft'])

        if sort == 'close':
            project_dicts.sort(key=itemgetter('left'))

        template_dict = {}
        template_dict['project_dicts'] = project_dicts[:8]
        template_dict['initial_budget'] = initial_budget
        template_dict['budget'] = budget
        template_dict['projects'] = all_projects.count()
        template_dict['sort'] = sort
        template_dict['pages'] = pages
        template_dict['budget_toolow'] = budget_toolow
        #template_dict['cursor'] = cursor
        
        path = os.path.join(os.path.dirname(__file__), 'templates/projects.html')
        self.response.out.write(template.render(path, template_dict))

class MoreHandler(webapp2.RequestHandler):
    def get(self):

        def make_project_dict(project, project_list):
            project_dict = {}
            project_dict['link'] = project.link + '/widget/card.html'
            project_dict['left'] = project.left
            timeleft =  project.end - datetime.now() + timedelta(0, 14400)
            project_dict['timeleft'] = (timeleft.days*60*60*24) + timeleft.seconds
            hours = str(timeleft.seconds / 3600)
            if timeleft.days < 0:
                timeleft_str = hours
            else:
                timeleft_str = str(timeleft.days) + ' days, ' + hours + ' hours'
            project_dict['time'] = timeleft_str
            project_list.append(project_dict)

        #cursor = self.request.get('c')

        budget = self.request.get('b')
        try:
            budget = int(float(budget))
        except ValueError:
            budget = 0

        sort = self.request.get('sort')
        if sort not in ['soon', 'close']:
            sort = 'soon'
        
        p = Project.all()
        projects = p.filter('left < ', budget)
        page = projects
        #cursor = p.cursor()

        project_dicts = []

        for project in page:
            make_project_dict(project, project_dicts)
        
        if sort == 'soon':
            project_dicts.sort(key=lambda i: i['timeleft'])

        if sort == 'close':
            project_dicts.sort(key=itemgetter('left'))

        response_dict = {}
        response_dict['projects'] = project_dicts
        #response_dict['cursor'] = cursor

        json_response = json.dumps(response_dict)
        
        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
        self.response.out.write(json_response)

       
app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/project', ProjectHandler),
                               ('/about', AboutHandler),
                               ('/more', MoreHandler)],
                              debug=True)
