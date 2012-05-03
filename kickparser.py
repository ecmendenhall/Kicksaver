from __future__ import division
from google.appengine.ext import db
from models import Project
from urllib2 import urlopen 
from urlparse import urlparse
from bs4 import BeautifulSoup
from operator import itemgetter
from time import strptime, mktime
from datetime import datetime

ENDING_SOON = 'http://www.kickstarter.com/discover/ending-soon'
SMALL_PROJECTS = 'http://www.kickstarter.com/discover/small-projects'

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
CRAWL_TIME = datetime.now()


def get_ending_projects(pages, url, project_list):
    for page in range(1, pages):
    
        projects_url = url + '?page=' + str(page)
        print projects_url
    
        p = urlopen(projects_url).read()
        ending_soon = BeautifulSoup(p)
    
        projects = ending_soon.select('.project-card')
        parse_projects(projects, project_list)

    return sorted(project_list, key=itemgetter('left'))
    
def parse_projects(projects, project_list):
    for project in projects:
        project_dict = {}
       
        progress_str = project.select('.funded strong')[0].get_text()[:-1]
        project_dict['progress'] = int(progress_str.replace(',','')) * .01
        pledged_str = project.select('.pledged strong')[0].get_text()[1:]
        project_dict['pledged'] = int(pledged_str.replace(',', '').replace('.',''))
        link_str = project.select('a')[0]['href']
        parsed_link = urlparse(link_str)
        project_dict['link'] = parsed_link[1] + parsed_link[2]
        end_str = project.select('.ksr_page_timer')[0]['data-end_time']
        end_struct = strptime(end_str[:-6], DATE_FORMAT)
        end_datetime = datetime.fromtimestamp(mktime(end_struct))
        project_dict['end'] = end_datetime
        
        try:
            total = int(project_dict['pledged'] / project_dict['progress'])
        except ZeroDivisionError:
            total = int(project_dict['pledged'] / .01)
        
        project_dict['total'] = total
        project_dict['left'] = int(project_dict['total'] - project_dict['pledged'])

        if project_dict['progress'] < 1 and project_dict['total'] > 0:
            project_list.append(project_dict)

def save_projects(project_list):
    projects = []
    unduped_project_list = []
    for project in project_list:
        if project not in unduped_project_list:
            unduped_project_list.append(project)
    for p in unduped_project_list:
        project = Project()
        project.link = 'http://www.kickstarter.com' + p['link']
        project.left = p['left'] 
        project.end = p['end']
        project.saved = CRAWL_TIME
        projects.append(project)
    db.put(projects)

def remove_old_projects():
    p = Project.all()
    old_project = p.order('-saved').get()
    if old_project:
        old_date = old_project.saved
        p = Project.all().filter('saved = ', old_date)
        db.delete(p) 


def run():        
    project_list = []   
    get_ending_projects(20, ENDING_SOON, project_list)
    get_ending_projects(20, SMALL_PROJECTS, project_list)
    remove_old_projects()
    save_projects(project_list)

if __name__ == '__main__':
    run()
