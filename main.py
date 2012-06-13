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
import logging

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

        def get_projects(budget, update=False):
            key = str(budget)
            all_projects = memcache.get(key)
            if all_projects is None or update:
                logging.error("DB QUERY")          
                p = Project.all()
                all_projects = p.filter('left <= ', budget)
                all_projects = list(all_projects)
                memcache.set(key, all_projects)
            return all_projects

        def get_next_page(cursor):
            p = Project.all().with_cursor(cursor)
            projects = p.filter('left <= ', budget)
            page = projects.fetch(8)
            cursor = p.cursor()
            return page, cursor
        
        project_dicts = []
        input_error = False
        budget_toolow = False
        number_results = 8
        
        p = self.request.get('p')
        try:
            pages = int(p)
        except ValueError:
            pages = 1

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
        
        page = get_projects(budget)
                
        if len(page) == 0:
            budget_toolow = True
            while len(page) < 4:
                budget = budget + 5
                page = get_projects(budget)
        for project in page:
            make_project_dict(project, project_dicts)
        
        if pages:
            number_results = pages * 8
        
        project_dicts.sort(key=lambda i: i['timeleft'])

        if sort == 'close':
            project_dicts.sort(key=itemgetter('left'))

        template_dict = {}
        template_dict['project_dicts'] = project_dicts[:number_results]
        template_dict['initial_budget'] = initial_budget
        template_dict['budget'] = budget
        template_dict['projects'] = len(page)
        template_dict['sort'] = sort
        template_dict['pages'] = pages
        template_dict['budget_toolow'] = budget_toolow
        
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

        budget = self.request.get('b')
        try:
            budget = int(float(budget))
        except ValueError:
            budget = 0

        sort = self.request.get('sort')
        if sort not in ['soon', 'close']:
            sort = 'soon'
        
        p = Project.all()
        projects = p.filter('left <= ', budget)
        page = projects

        project_dicts = []

        for project in page:
            make_project_dict(project, project_dicts)
        
        if sort == 'soon':
            project_dicts.sort(key=lambda i: i['timeleft'])

        if sort == 'close':
            project_dicts.sort(key=itemgetter('left'))

        response_dict = {}
        response_dict['projects'] = project_dicts

        json_response = json.dumps(response_dict)
        
        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
        self.response.out.write(json_response)

       
app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/project', ProjectHandler),
                               ('/about', AboutHandler),
                               ('/more', MoreHandler)],
                              debug=True)
