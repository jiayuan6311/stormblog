import webapp2
import urllib
import logging

from datetime import datetime
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from blog_model import Blog
from blog_model import BlogPost
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
        
        pics_query = Picture.query(ancestor=main.blog_key(blog_name))
        pics = pics_query.fetch() 
        upload_url = blobstore.create_upload_url('/upload')
        
        pic_urls = []
        
        for pic in pics:
            pic_urls.append(images.get_serving_url(pic.data))
             
        template_values={
            'upload_url': upload_url,
            'pics': pics,
            'pic_urls': pic_urls,
            'blog_name': blog_name
        }
        
        template = main.JINJA_ENVIRONMENT.get_template('blog_gallery.html')
        self.response.write(template.render(template_values))
       
 
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    
    def post(self):
        blog_name = self.request.get('blog_name')
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        logging.warning(upload_files)
        pic = Picture(parent=main.blog_key(blog_name))
        pic.data = blob_info.key()
        pic.put()
        self.redirect('/blog_gallery?blog_name='+blog_name)

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

class RSSHandler(webapp2.RedirectHandler):
    
    def get(self):
    
        blog_name = self.request.get('blog_name')
        blogs_query = Blog.query().order(-Blog.create_time)
        blogs_query = blogs_query.filter(Blog.blog_name == blog_name)
        blogs = blogs_query.fetch()
        blog = blogs[0]
        
        posts_query = BlogPost.query(ancestor=main.blog_key(blog_name)).order(-BlogPost.create_time)
        posts = posts_query.fetch()
        
        template_values = {
            'blog': blog,
            'posts': posts,
            'back_url': self.request.uri
        }
        
        template = main.JINJA_ENVIRONMENT.get_template('rss.html')
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(template.render(template_values))
        