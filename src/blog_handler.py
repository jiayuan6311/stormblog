import webapp2
import urllib
import logging

from datetime import datetime
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import images

from blog_model import Blog
from blog_model import Picture
import main

EXISTING_BLOG_MSG = 'Blog Name exists. Please try another title.'

class RegisterBlog(webapp2.RequestHandler):

    def post(self):
        user = users.get_current_user()
        blog_name = self.request.get('blog_name')
        
        blogs_query = Blog.query().order(-Blog.create_time)
        blogs_query = blogs_query.filter(Blog.blog_name == blog_name)
     
        blogs = blogs_query.fetch()      
        if blogs: 
            query_params = {'msg': EXISTING_BLOG_MSG}
            self.redirect('/?'+ urllib.urlencode(query_params))
        else:      
            blog = Blog(parent=main.user_key(user.email()))
            blog.author = user
            blog.blog_name = blog_name
            blog.create_time = datetime.now()
            blog.put()
            self.redirect('/?blog_name='+blog.blog_name)
        
class SwitchBlog(webapp2.RedirectHandler):
    
    def post(self):
        blog_name = self.request.get('blogoptions')
        self.redirect('/?blog_name='+blog_name)
        
class BlogGallery(webapp2.RedirectHandler):
    
    def get(self):
        blog_name = self.request.get('blog_name')
        image = self.request.get('img')
        
        
        pics_query = Picture.query(ancestor=main.blog_key(blog_name))
        pics = pics_query.fetch() 
        
        if image:
            image = images.resize(image, 32, 32)
            pic = Picture(parent=main.blog_key(blog_name))
            pic.data = ndb.blobstore.BlobInfo(image)
            pic.put()
             
        template_values={
            'pics': pics,
            'blog_name': blog_name
        }
        
        template = main.JINJA_ENVIRONMENT.get_template('blog_gallery.html')
        self.response.write(template.render(template_values))
       
    def post(self):
        self.get() 

class LoadPicture(webapp2.RedirectHandler):
        
        def get(self):
            key_url = self.request.get('key_url')
            pic_key = ndb.Key(urlsafe=key_url)
            pic = pic_key.get()
            
            if pic:
                self.response.headers['Content-Type'] = 'image/png'
                self.response.out.write(pic.data)
            else:
                self.response.out.write('No image')
        