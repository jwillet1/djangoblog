from django.test import TestCase, LiveServerTestCase, Client
from django.utils import timezone
from blogengine.models import Post

# Create your tests here.
class PostTest(TestCase):
	def test_create_post(self):
		# create the Post
		post = Post()

		# set attributes
		post.title = 'My first post'
		post.text = 'This is my first blog post'
		post.pub_date = timezone.now()

		# save it
		post.save()

		# check that we can find it
		all_posts = Post.objects.all()
		self.assertEquals(len(all_posts), 1)
		only_post = all_posts[0]
		self.assertEquals(only_post, post)

		# check attribures
		self.assertEquals(only_post.title, 'My first post') 
		self.assertEquals(only_post.text, 'This is my first blog post')
		self.assertEquals(only_post.pub_date.day, post.pub_date.day)
		self.assertEquals(only_post.pub_date.month, post.pub_date.month)
		self.assertEquals(only_post.pub_date.year, post.pub_date.year)
		self.assertEquals(only_post.pub_date.hour, post.pub_date.hour)
		self.assertEquals(only_post.pub_date.minute, post.pub_date.minute)
		self.assertEquals(only_post.pub_date.second, post.pub_date.second)

class AdminTest(LiveServerTestCase):
	fixtures = ['users.json']

	def setUp(self):
		self.client = Client()

	def test_login(self):
		# get login page
		response = self.client.get('/admin/login/?next=/admin/')

		# check response code
		self.assertEquals(response.status_code, 200)

		# check 'Log in' in response
		self.assertTrue('Log in' in response.content)

		# log the user in
		self.client.login(username='bobsmith', password="password")

		# check response code
		response = self.client.get('/admin/')
		self.assertEquals(response.status_code, 200)

		# check 'Log out' in response
		self.assertTrue('Log out' in response.content)

	def test_logout(self):
		# log in
		self.client.login(username='bobsmith', password="password")

		# check response code
		response = self.client.get('/admin/')
		self.assertEquals(response.status_code, 200)

		# check 'Log out' in response
		self.assertTrue('Log out' in response.content)

		# log out
		self.client.logout()

		# get login page
		response = self.client.get('/admin/login/?next=/admin/')
		self.assertEquals(response.status_code, 200)

		# check 'Log in' in response
		self.assertTrue('Log in' in response.content)

	def test_create_post(self):
		# log in 
		self.client.login(username='bobsmith', password="password")

		# check response code
		response = self.client.get('/admin/blogengine/post/add/')
		self.assertEquals(response.status_code, 200)

		# create new post
		response = self.client.post('/admin/blogengine/post/add/', {
			'title':'My first post',
			'text':'This is my first post',
			'pub_date_0':'2013-12-28',
			'pub_date_1':'22:00:04'
		}, follow=True)
		self.assertEquals(response.status_code, 200)

		# check added successfully
		self.assertTrue('added successfully' in response.content)

		# check new post now in database
		all_posts = Post.objects.all()
		self.assertEquals(len(all_posts), 1)

	def test_edit_post(self):
		# create the post
		post = Post()
		post.title = 'My first post'
		post.text = 'This is my first blog post'
		post.pub_date = timezone.now()
		post.save()

		# log in 
		self.client.login(username='bobsmith', password="password")

		# edit the post
		response = self.client.post('/admin/blogengine/post/%s/' % post.id, {
			'title':'My second post',
			'text':'This is my second blog post',
			'pub_date_0':'2013-12-28',
			'pub_date_1':'22:00:04'
		}, follow=True)
		self.assertEquals(response.status_code, 200)

		# check if changed successfully
		self.assertTrue('changed successfully' in response.content)

		# check post amended
		all_posts = Post.objects.all()
		self.assertEquals(len(all_posts), 1)
		only_post = all_posts[0]
		self.assertEquals(only_post.title, 'My second post')
		self.assertEquals(only_post.text, 'This is my second blog post')

	def test_delete_post(self):
		# create the post
		post = Post()
		post.title = 'My first post'
		post.text = 'This is my first blog post'
		post.pub_date = timezone.now()
		post.save()

		# check new post saved
		all_posts = Post.objects.all()
		self.assertEquals(len(all_posts), 1)

		# log in 
		self.client.login(username='bobsmith', password="password")

		# delete the post
		response = self.client.post('/admin/blogengine/post/%s/delete/' % post.id, {'post':'yes'}, follow=True)
		self.assertEquals(response.status_code, 200)

		# check deleted successfully
		self.assertTrue('deleted successfully' in response.content)

		# check post amended
		all_posts = Post.objects.all()
		self.assertEquals(len(all_posts), 0)

class PostViewTest(LiveServerTestCase):
	def setUp(self):
		self.client = Client()

	def test_index(self):
		# create the post
		post = Post()
		post.title = 'My first post'
		post.text = 'This is my first blog post'
		post.pub_date = timezone.now()
		post.save()

		# check new post saved
		all_posts = Post.objects.all()
		self.assertEquals(len(all_posts), 1)

		# fetch index
		response = self.client.get('/')
		self.assertEquals(response.status_code, 200)

		# check the post title in the response
		self.assertTrue(post.title in response.content)

		# check the post text in the response
		self.assertTrue(post.text in response.content)

		# check the post date in the response
		self.assertTrue(str(post.pub_date.year) in response.content)
		self.assertTrue(post.pub_date.strftime('%b') in response.content)
		self.assertTrue(str(post.pub_date.day) in response.content)
