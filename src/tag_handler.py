import webapp2
import jinja2
import os
import logging

from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor

from blog_model import BlogPost
import main

class AddTag(webapp2.RedirectHandler):
    
    def post(self):
        key = ndb.Key(urlsafe=self.request.get('keyurl'))
        post = key.get()
        tag = self.request.get('tag')
        
        if not (tag in post.taglist):  
            post.taglist.append(tag)
            
        post.put()
        
        template_values = { 'post': post }
        template = main.JINJA_ENVIRONMENT.get_template('read_post.html')
        self.response.write(template.render(template_values))
        
class SearchTag(webapp2.RedirectHandler):
    
    def get(self):
        tag = self.request.get('tag')
        curs = Cursor(urlsafe=self.request.get('cursor'))
        
        post_query = BlogPost.query().order(-BlogPost.create_time)
        post_query = post_query.filter(BlogPost.taglist.IN([tag]))
        
        posts, next_curs, more = post_query.fetch_page(main.MAX_POST_PER_PAGE, start_cursor=curs)
        cur_url = ''
        
        if more and next_curs:
            cur_url = next_curs.urlsafe()
        
        template_values = {
                'posts':  posts,
                'moreHTML': cur_url,
                'tag': tag,
            }    
        
        template = main.JINJA_ENVIRONMENT.get_template('search_result.html')
        self.response.write(template.render(template_values))
        
        