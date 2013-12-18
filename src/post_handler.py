import webapp2
import jinja2
import os
import re
import logging

from datetime import datetime
from google.appengine.ext import ndb
from google.appengine.api import users

from blog_model import BlogPost
import main


# def autolink(string):
#     
#     r = re.compile(r"(http[s]?://[^ ]+(jpg|png|gif))")
#     temp = r.sub(r'<img src="\1">',string)
#     
#     r1 = re.compile(r'[^"](http[s]?://[^ ]+)')
#     result = r1.sub(r'<a href="\1"> \1</a>', temp)
#     return result


def cap(string, maxlength):
        return string if len(string)<=maxlength else string[0:maxlength-3]+'...'
    

# JINJA_ENVIRONMENT = jinja2.Environment(
#     loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
#     extensions=['jinja2.ext.autoescape'],
#     autoescape=True)
# JINJA_ENVIRONMENT.filters['autolink'] = autolink

class PostEditPage(webapp2.RedirectHandler):
    
    def get(self):
        blog_name = self.request.get('blog_name')
        keyurl = self.request.get('keyurl')
        
        if keyurl:
            key = ndb.Key(urlsafe=keyurl)
            post = key.get()
            content = post.content
            title = post.title
        else:
            keyurl = ''
            content = ''
            title = ''
            
        template_values={
           'blog_name': blog_name,
           'post_title': title,
           'post_content': content,
           'keyurl' : keyurl 
        }
        template = main.JINJA_ENVIRONMENT.get_template('edit_post.html')
        self.response.write(template.render(template_values))
    
    def post(self):
        self.get()

class AddPost(webapp2.RedirectHandler):

    def post(self):
        blog_name=self.request.get('blog_name')
        title = self.request.get('title')
        keyurl = self.request.get('keyurl')
        
        if keyurl:
            rev_key = ndb.Key(urlsafe=keyurl)
            post = rev_key.get()
        else:
            post = BlogPost(parent=main.blog_key(blog_name))

        post.author = users.get_current_user()
        post.blog_name = blog_name
        post.title = title
        post.content = self.request.get('content')
        post.brief = cap(post.content,500)
        post.modify_time = datetime.now()
             
        post.put()
        self.redirect('/?blog_name='+blog_name)

class ReadPost(webapp2.RedirectHandler):
    
    def get(self):
        
        user = users.get_current_user()
        keyurl = self.request.get('keyurl')
        key = ndb.Key(urlsafe=keyurl)
        blog_post = key.get()

        template_values = { 
            'currentuser': user,
            'post': blog_post 
        }
        template = main.JINJA_ENVIRONMENT.get_template('read_post.html')
        self.response.write(template.render(template_values))