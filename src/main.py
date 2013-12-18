import os
import logging
import jinja2
import webapp2
import re

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor

from blog_model import Blog
from blog_model import BlogPost
from blog_handler import RegisterBlog
from blog_handler import SwitchBlog
from blog_handler import BlogGallery
from blog_handler import LoadPicture
from blog_handler import UploadHandler
from blog_handler import RSSHandler
from post_handler import PostEditPage
from post_handler import AddPost
from post_handler import ReadPost  
from tag_handler import AddTag
from tag_handler import SearchTag

def autolink(string):
     
    r = re.compile(r"(http[s]?://[^ ]+(jpg|png|gif))")
    temp = r.sub(r'<img src="\1">',string)
     
    r1 = re.compile(r'[^"](http[s]?://[^ ]+)')
    result = r1.sub(r'<a href="\1"> \1</a>', temp)
    return result

def user_key(username):
    return ndb.Key('User', username)

def blog_key(blogname):
    return ndb.Key('Blog', blogname)

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
JINJA_ENVIRONMENT.filters['autolink'] = autolink

MAX_POST_PER_PAGE = 10


class MainPage(webapp2.RequestHandler):
    
    def get(self):
        msg = self.request.get('msg')
        if msg:
            template_values = {
                'msg': msg
            }
            template = JINJA_ENVIRONMENT.get_template('info.html')
            self.response.write(template.render(template_values))
        else:
            blog_name = self.request.get('blog_name')
            curs = Cursor(urlsafe=self.request.get('cursor'))
            tags = []
            
            if blog_name == '':
                blogposts_query = BlogPost.query().order(-BlogPost.create_time) 
                templist = []
                for post in blogposts_query.fetch():
                    templist = templist + post.taglist
                tags = list(set(templist))
            else:
                blogposts_query = BlogPost.query(ancestor=blog_key(blog_name)).order(-BlogPost.create_time) 
             
            blogposts, next_curs, more = blogposts_query.fetch_page(MAX_POST_PER_PAGE, start_cursor=curs)
            cur_url = ''
            if more and next_curs:
                cur_url = next_curs.urlsafe()
            
            user = users.get_current_user()
            if user:
                blogs_query = Blog.query(ancestor=user_key(user.email())).order(-Blog.create_time)
                blogs = blogs_query.fetch()
                url = users.create_logout_url(self.request.uri)
                url_linktext = 'Logout'   
                username = user.email()
            else:
                blogs = ''
                url = users.create_login_url(self.request.uri)
                url_linktext = 'Login'
                username = ''
    
            template_values = {
                'currentuser': user,
                'blogs': blogs,
                'selectedblog': blog_name,
                'username' : username,
                'blogposts':  blogposts,
                'url': url,
                'url_linktext': url_linktext,
                'moreHTML': cur_url,
                'tags': tags,
            }    
             
            template = JINJA_ENVIRONMENT.get_template('index.html')
            self.response.write(template.render(template_values))

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/register', RegisterBlog),
    ('/switch', SwitchBlog),
    ('/edit_post', PostEditPage),
    ('/add_post', AddPost),
    ('/read_post', ReadPost),
    ('/add_tag', AddTag),
    ('/search_tag',SearchTag),
    ('/blog_gallery', BlogGallery),
    ('/pic', LoadPicture),
    ('/upload', UploadHandler),
    ('/RSS', RSSHandler)
], debug=True)