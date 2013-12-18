from google.appengine.ext import ndb

class BlogPost(ndb.Model):
	author = ndb.UserProperty()
	blog_name = ndb.StringProperty()
	title = ndb.StringProperty()
	content = ndb.StringProperty(indexed=False)
	create_time = ndb.DateTimeProperty(auto_now_add=True)
	modify_time = ndb.DateTimeProperty(auto_now_add=True)
	taglist = ndb.StringProperty(repeated=True)
	
	
class Blog(ndb.Model):
	author = ndb.UserProperty()
	blog_name = ndb.StringProperty()
	create_time = ndb.DateTimeProperty(auto_now_add=True)
	

class Picture(ndb.Model):
	data = ndb.BlobKeyProperty()