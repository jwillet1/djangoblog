from django.test import TestCase, LiveServerTestCase, Client
from django.utils import timezone
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from blogengine.models import Post, Category, Tag
import markdown2 as markdown
import feedparser

# Create your tests here.
class PostTest(TestCase):
    def test_creat_tag(self):
        # crate the tag
        tag = Tag()

        # add attributes
        tag.name = 'python'
        tag.description = 'The Python programming language'
        tag.slug = 'python'

        # save it
        tag.save()

        # check we can find it
        all_tags = Tag.objects.all()
        self.assertEquals(len(all_tags), 1)
        only_tag = all_tags[0]
        self.assertEquals(only_tag, tag)

        # check attributes
        self.assertEquals(only_tag.name, 'python')
        self.assertEquals(only_tag.description, 'The Python programming language')
        self.assertEquals(only_tag.slug, 'python')

    def test_create_category(self):
        # create category
        category = Category()

        # add attibutes
        category.name = 'python'
        category.description = 'The Python programming language'
        category.slug = 'python'

        # save it
        category.save()

        # check we can find it
        all_categories = Category.objects.all()
        self.assertEquals(len(all_categories), 1)
        only_category = all_categories[0]
        self.assertEquals(only_category, category)

        # check attributes
        self.assertEquals(only_category.name, 'python')
        self.assertEquals(only_category.description, 'The Python programming language')
        self.assertEquals(only_category.slug, 'python')

    def test_create_post(self):
        # create category
        category = Category()
        category.name = 'python'
        category.description = 'The Python programming language'
        category.save()

        # crate the tag
        tag = Tag()
        tag.name = 'python'
        tag.description = 'The Python programming language'
        tag.save()

        # create the author
        author = User.objects.create_user('testuser', 'user@example.com', 'password')
        author.save()

        # create the site
        site = Site()
        site.name = 'example.com'
        site.domain = 'example.com'
        site.save()

        # Create the post
        post = Post()

        # Set the attributes
        post.title = 'My first post'
        post.text = 'This is my first blog post'
        post.slug = 'my-first-post'
        post.pub_date = timezone.now()
        post.author = author
        post.site = site
        post.category = category

        # Save it
        post.save()

        # add the tag
        post.tags.add(tag)
        post.save()

        # Check we can find it
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)
        only_post = all_posts[0]
        self.assertEquals(only_post, post)

        # Check attributes
        self.assertEquals(only_post.title, 'My first post')
        self.assertEquals(only_post.text, 'This is my first blog post')
        self.assertEquals(only_post.slug, 'my-first-post')
        self.assertEquals(only_post.site.name, 'example.com')
        self.assertEquals(only_post.site.domain, 'example.com')
        self.assertEquals(only_post.pub_date.day, post.pub_date.day)
        self.assertEquals(only_post.pub_date.month, post.pub_date.month)
        self.assertEquals(only_post.pub_date.year, post.pub_date.year)
        self.assertEquals(only_post.pub_date.hour, post.pub_date.hour)
        self.assertEquals(only_post.pub_date.minute, post.pub_date.minute)
        self.assertEquals(only_post.pub_date.second, post.pub_date.second)
        self.assertEquals(only_post.author.username, 'testuser')
        self.assertEquals(only_post.author.email, 'user@example.com')
        self.assertEquals(only_post.category.name, 'python')
        self.assertEquals(only_post.category.description, 'The Python programming language')

        # check tags
        post_tags = only_post.tags.all()
        self.assertEquals(len(post_tags), 1)
        only_post_tag = post_tags[0]
        self.assertEquals(only_post_tag, tag)
        self.assertEquals(only_post_tag.name, 'python')
        self.assertEquals(only_post_tag.description, 'The Python programming language')

class BaseAcceptanceTest(LiveServerTestCase):
    def setUp(self):
        self.client = Client()

class AdminTest(BaseAcceptanceTest):
    fixtures = ['users.json']

    def test_login(self):
        # Get login page
        response = self.client.get('/admin/login/?next=/admin/')

        # Check response code
        self.assertEquals(response.status_code, 200)

        # Check 'Log in' in response
        self.assertTrue('Log in' in response.content)

        # Log the user in
        self.client.login(username='bobsmith', password="password")

        # Check response code
        response = self.client.get('/admin/')
        self.assertEquals(response.status_code, 200)

        # Check 'Log out' in response
        self.assertTrue('Log out' in response.content)

    def test_logout(self):
        # Log in
        self.client.login(username='bobsmith', password="password")

        # Check response code
        response = self.client.get('/admin/')
        self.assertEquals(response.status_code, 200)

        # Check 'Log out' in response
        self.assertTrue('Log out' in response.content)

        # Log out
        self.client.logout()

        # Check response code
        response = self.client.get('/admin/login/?next=/admin/')
        self.assertEquals(response.status_code, 200)

        # Check 'Log in' in response
        self.assertTrue('Log in' in response.content)

    def test_create_post(self):
        # Create the category
        category = Category()
        category.name = 'python'
        category.description = 'The Python programming language'
        category.save()

        # Create the tag
        tag = Tag()
        tag.name = 'python'
        tag.description = 'The Python programming language'
        tag.save()

        # Log in
        self.client.login(username='bobsmith', password="password")

        # Check response code
        response = self.client.get('/admin/blogengine/post/add/')
        self.assertEquals(response.status_code, 200)

        # Create the new post
        response = self.client.post('/admin/blogengine/post/add/', {
            'title': 'My first post',
            'text': 'This is my first post',
            'pub_date_0': '2013-12-28',
            'pub_date_1': '22:00:04',
            'slug': 'my-first-post',
            'site': '1',
            'category': '%s' % category.id ,
            'tags': '%s' % tag.id
        },
        follow=True
        )
        self.assertEquals(response.status_code, 200)

        # Check added successfully
        self.assertTrue('added successfully' in response.content)

        # Check new post now in database
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)

    def test_creat_post_without_tag(self):
        # Create the category
        category = Category()
        category.name = 'python'
        category.description = 'The Python programming language'
        category.save()

        # Log in
        self.client.login(username='bobsmith', password="password")

        # Check response code
        response = self.client.get('/admin/blogengine/post/add/')
        self.assertEquals(response.status_code, 200)

        # Create the new post
        response = self.client.post('/admin/blogengine/post/add/', {
            'title': 'My first post',
            'text': 'This is my first post',
            'pub_date_0': '2013-12-28',
            'pub_date_1': '22:00:04',
            'slug': 'my-first-post',
            'site': '1',
            'category': '%s' % category.id
        },
        follow=True
        )
        self.assertEquals(response.status_code, 200)

        # Check added successfully
        self.assertTrue('added successfully' in response.content)

        # Check new post now in database
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)

    def test_edit_post(self):
        # Create the category
        category = Category()
        category.name = 'python'
        category.description = 'The Python programming language'
        category.save()

        # Create the tag
        tag = Tag()
        tag.name = 'python'
        tag.description = 'The Python programming language'
        tag.save()

        # create the author
        author = User.objects.create_user('testuser', 'user@example.com', 'password')
        author.save()

        # create the site
        site = Site()
        site.name = 'example.com'
        site.domain = 'example.com'
        site.save()

        # Create the post
        post = Post()
        post.title = 'My first post'
        post.text = 'This is my first blog post'
        post.slug = 'my-first-post'
        post.pub_date = timezone.now()
        post.author = author
        post.site = site
        post.category = category
        post.save()
        post.tags.add(tag)
        post.save()

        # Log in
        self.client.login(username='bobsmith', password="password")

        # Edit the post
        response = self.client.post('/admin/blogengine/post/%s/' % post.id, {
            'title': 'My second post',
            'text': 'This is my second blog post',
            'pub_date_0': '2013-12-28',
            'pub_date_1': '22:00:04',
            'slug': 'my-second-post',
            'site': '1',
            'category': '%s' % category.id ,
            'tags': '%d' % tag.id
        },
        follow=True
        )
        self.assertEquals(response.status_code, 200)

        # Check changed successfully
        self.assertTrue('changed successfully' in response.content)

        # Check post amended
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)
        only_post = all_posts[0]
        self.assertEquals(only_post.title, 'My second post')
        self.assertEquals(only_post.text, 'This is my second blog post')

    def test_delete_post(self):
        # Create the category
        category = Category()
        category.name = 'python'
        category.description = 'The Python programming language'
        category.save()

        # Create the tag
        tag = Tag()
        tag.name = 'python'
        tag.description = 'The Python programming language'
        tag.save()

        # create the author
        author = User.objects.create_user('testuser', 'user@example.com', 'password')
        author.save()

        # create the site
        site = Site()
        site.name = 'example.com'
        site.domain = 'example.com'
        site.save()

        # Create the post
        post = Post()
        post.title = 'My first post'
        post.text = 'This is my first blog post'
        post.slug = 'my-first-post'
        post.pub_date = timezone.now()
        post.author = author
        post.site = site
        post.category = category
        post.save()
        post.tags.add(tag)
        post.save()

        # Check new post saved
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)

        # Log in
        self.client.login(username='bobsmith', password="password")

        # Delete the post
        response = self.client.post('/admin/blogengine/post/%s/delete/' % post.id, {
            'post': 'yes'
        }, follow=True)
        self.assertEquals(response.status_code, 200)

        # Check deleted successfully
        self.assertTrue('deleted successfully' in response.content)

        # Check post amended
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 0)

    def test_create_category(self):
        # Log in
        self.client.login(username='bobsmith', password="password")

        # Check response code
        response = self.client.get('/admin/blogengine/category/add/')
        self.assertEquals(response.status_code, 200)

        # Create the new category
        response = self.client.post('/admin/blogengine/category/add/', {
            'name': 'python',
            'description': 'The Python programming language'
        },
        follow=True
        )
        self.assertEquals(response.status_code, 200)

        # Check added successfully
        self.assertTrue('added successfully' in response.content)

        # Check new category now in database
        all_categories = Category.objects.all()
        self.assertEquals(len(all_categories), 1)

    def test_edit_category(self):
        # Create the category
        category = Category()
        category.name = 'python'
        category.description = 'The Python programming language'
        category.save()

        # Log in
        self.client.login(username='bobsmith', password="password")

        # Edit the category
        response = self.client.post('/admin/blogengine/category/%s/' % category.id, {
            'name': 'perl',
            'description': 'The Perl programming language'
        }, follow=True)
        self.assertEquals(response.status_code, 200)

        # Check changed successfully
        self.assertTrue('changed successfully' in response.content)

        # Check category amended
        all_categories = Category.objects.all()
        self.assertEquals(len(all_categories), 1)
        only_category = all_categories[0]
        self.assertEquals(only_category.name, 'perl')
        self.assertEquals(only_category.description, 'The Perl programming language')

    def test_delete_category(self):
        # Create the category
        category = Category()
        category.name = 'python'
        category.description = 'The Python programming language'
        category.save()

        # Log in
        self.client.login(username='bobsmith', password="password")

        # Delete the category
        response = self.client.post('/admin/blogengine/category/%s/delete/' % category.id, {
            'post': 'yes'
        }, follow=True)
        self.assertEquals(response.status_code, 200)

        # Check deleted successfully
        self.assertTrue('deleted successfully' in response.content)

        # Check category amended
        all_categories = Category.objects.all()
        self.assertEquals(len(all_categories), 0)

    def test_create_tag(self):
        # Log in
        self.client.login(username='bobsmith', password="password")

        # Check response code
        response = self.client.get('/admin/blogengine/tag/add/')
        self.assertEquals(response.status_code, 200)

        # Create the new tag
        response = self.client.post('/admin/blogengine/tag/add/', {
            'name': 'python',
            'description': 'The Python programming language'
        },
        follow=True
        )
        self.assertEquals(response.status_code, 200)

        # Check added successfully
        self.assertTrue('added successfully' in response.content)

        # Check new tag now in database
        all_tags = Tag.objects.all()
        self.assertEquals(len(all_tags), 1)

    def test_edit_tag(self):
        # Create the tag
        tag = Tag()
        tag.name = 'python'
        tag.description = 'The Python programming language'
        tag.save()

        # Log in
        self.client.login(username='bobsmith', password="password")

        # Edit the tag
        response = self.client.post('/admin/blogengine/tag/%s/' % tag.id, {
            'name': 'perl',
            'description': 'The Perl programming language'
        }, follow=True)
        self.assertEquals(response.status_code, 200)

        # Check changed successfully
        self.assertTrue('changed successfully' in response.content)

        # Check tag amended
        all_tags = Tag.objects.all()
        self.assertEquals(len(all_tags), 1)
        only_tag = all_tags[0]
        self.assertEquals(only_tag.name, 'perl')
        self.assertEquals(only_tag.description, 'The Perl programming language')

    def test_delete_tag(self):
        # Create the tag
        tag = Tag()
        tag.name = 'python'
        tag.description = 'The Python programming language'
        tag.save()

        # Log in
        self.client.login(username='bobsmith', password="password")

        # Delete the tag
        response = self.client.post('/admin/blogengine/tag/%s/delete/' % tag.id, {
            'post': 'yes'
        }, follow=True)
        self.assertEquals(response.status_code, 200)

        # Check deleted successfully
        self.assertTrue('deleted successfully' in response.content)

        # Check tag amended
        all_tags = Tag.objects.all()
        self.assertEquals(len(all_tags), 0)

class PostViewTest(BaseAcceptanceTest):
    def test_index(self):
        # Create the category
        category = Category()
        category.name = 'python'
        category.description = 'The Python programming language'
        category.save()

        # Create the tag
        tag = Tag()
        tag.name = 'perl'
        tag.description = 'The Perl programming language'
        tag.save()

        # create the author
        author = User.objects.create_user('testuser', 'user@example.com', 'password')
        author.save()

        # create the site
        site = Site()
        site.name = 'example.com'
        site.domain = 'example.com'
        site.save()

        # Create the post
        post = Post()
        post.title = 'My first post'
        post.text = 'This is [my first blog post](http://127.0.0.1:8000/)'
        post.slug = 'my-first-post'
        post.pub_date = timezone.now()
        post.author = author
        post.site = site
        post.category = category
        post.save()
        post.tags.add(tag)
        post.save()

        # Check new post saved
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)

        # Fetch the index
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)

        # Check the post title is in the response
        self.assertTrue(post.title in response.content)

        # Check the post text is in the response
        self.assertTrue(markdown.markdown(post.text) in response.content)

        # check the post category in response
        self.assertTrue(post.category.name in response.content)

        # check the post tag in response
        post_tag = all_posts[0].tags.all()[0]
        self.assertTrue(post_tag.name in response.content)

        # Check the post date is in the response
        self.assertTrue(str(post.pub_date.year) in response.content)
        self.assertTrue(post.pub_date.strftime('%b') in response.content)
        self.assertTrue(str(post.pub_date.day) in response.content)

        # Check the link is marked up properly
        self.assertTrue('<a href="http://127.0.0.1:8000/">my first blog post</a>' in response.content)

    def test_post_page(self):
        # Create the category
        category = Category()
        category.name = 'python'
        category.description = 'The Python programming language'
        category.save()

        # Create the tag
        tag = Tag()
        tag.name = 'perl'
        tag.description = 'The Perl programming language'
        tag.save()

        # create the author
        author = User.objects.create_user('testuser', 'user@example.com', 'password')
        author.save()

        # create the site
        site = Site()
        site.name = 'example.com'
        site.domain = 'example.com'
        site.save()

        # Create the post
        post = Post()
        post.title = 'My first post'
        post.text = 'This is [my first blog post](http://127.0.0.1:8000/)'
        post.slug = 'my-first-post'
        post.pub_date = timezone.now()
        post.author = author
        post.site = site
        post.category = category
        post.save()
        post.tags.add(tag)
        post.save()

        # Check new post saved
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)
        only_post = all_posts[0]
        self.assertEquals(only_post, post)

        # Get the post URL
        post_url = only_post.get_absolute_url()

        # Fetch the post
        response = self.client.get(post_url)
        self.assertEquals(response.status_code, 200)

        # Check the post title is in the response
        self.assertTrue(post.title in response.content)

        # Check the post text is in the response
        self.assertTrue(markdown.markdown(post.text) in response.content)

        # check the post category in response
        self.assertTrue(post.category.name in response.content)

        # check the post tag in response
        post_tag = all_posts[0].tags.all()[0]
        self.assertTrue(post_tag.name in response.content)

        # Check the post date is in the response
        self.assertTrue(str(post.pub_date.year) in response.content)
        self.assertTrue(post.pub_date.strftime('%b') in response.content)
        self.assertTrue(str(post.pub_date.day) in response.content)

        # Check the link is marked up properly
        self.assertTrue('<a href="http://127.0.0.1:8000/">my first blog post</a>' in response.content)

    def test_category_page(self):
        # Create the category
        category = Category()
        category.name = 'python'
        category.description = 'The Python programming language'
        category.save()

        # create the author
        author = User.objects.create_user('testuser', 'user@example.com', 'password')
        author.save()

        # create the site
        site = Site()
        site.name = 'example.com'
        site.domain = 'example.com'
        site.save()

        # Create the post
        post = Post()
        post.title = 'My first post'
        post.text = 'This is [my first blog post](http://127.0.0.1:8000/)'
        post.slug = 'my-first-post'
        post.pub_date = timezone.now()
        post.author = author
        post.site = site
        post.category = category
        post.save()

        # Check new post saved
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)
        only_post = all_posts[0]
        self.assertEquals(only_post, post)

        # Get the category URL
        category_url = post.category.get_absolute_url()

        # Fetch the category
        response = self.client.get(category_url)
        self.assertEquals(response.status_code, 200)

        # Check the category name is in the response
        self.assertTrue(post.category.name in response.content)

        # Check the post text is in the response
        self.assertTrue(markdown.markdown(post.text) in response.content)

        # Check the post date is in the response
        self.assertTrue(str(post.pub_date.year) in response.content)
        self.assertTrue(post.pub_date.strftime('%b') in response.content)
        self.assertTrue(str(post.pub_date.day) in response.content)

        # Check the link is marked up properly
        self.assertTrue('<a href="http://127.0.0.1:8000/">my first blog post</a>' in response.content)

    def test_tag_page(self):
        # Create the tag
        tag = Tag()
        tag.name = 'python'
        tag.description = 'The Python programming language'
        tag.save()

        # create the author
        author = User.objects.create_user('testuser', 'user@example.com', 'password')
        author.save()

        # create the site
        site = Site()
        site.name = 'example.com'
        site.domain = 'example.com'
        site.save()

        # Create the post
        post = Post()
        post.title = 'My first post'
        post.text = 'This is [my first blog post](http://127.0.0.1:8000/)'
        post.slug = 'my-first-post'
        post.pub_date = timezone.now()
        post.author = author
        post.site = site
        post.save()
        post.tags.add(tag)
        post.save()

        # Check new post saved
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)
        only_post = all_posts[0]
        self.assertEquals(only_post, post)

        # Get the tag
        tag_url = post.tags.all()[0].get_absolute_url()

        # Fetch the tag
        response = self.client.get(tag_url)
        self.assertEquals(response.status_code, 200)

        # Check the tag name is in the response
        self.assertTrue(post.tags.all()[0].name in response.content)

        # Check the post text is in the response
        self.assertTrue(markdown.markdown(post.text) in response.content)

        # Check the post date is in the response
        self.assertTrue(str(post.pub_date.year) in response.content)
        self.assertTrue(post.pub_date.strftime('%b') in response.content)
        self.assertTrue(str(post.pub_date.day) in response.content)

        # Check the link is marked up properly
        self.assertTrue('<a href="http://127.0.0.1:8000/">my first blog post</a>' in response.content)

    def test_nonexistent_category_page(self):
        category_url = '/category/blah'
        response = self.client.get(category_url)
        self.assertEquals(response.status_code, 200)
        self.assertTrue('No posts found' in response.content)

    def test_nonexistent_tag_page(self):
        tag_url = '/tag/blah'
        response = self.client.get(tag_url)
        self.assertEquals(response.status_code, 200)
        self.assertTrue('No posts found' in response.content)

class FeedTest(BaseAcceptanceTest):
    def test_all_post_feed(self):
        # Create the category
        category = Category()
        category.name = 'python'
        category.description = 'The Python programming language'
        category.save()

        # Create the tag
        tag = Tag()
        tag.name = 'python'
        tag.description = 'The Python programming language'
        tag.save()

        # create the author
        author = User.objects.create_user('testuser', 'user@example.com', 'password')
        author.save()

        # create the site
        site = Site()
        site.name = 'example.com'
        site.domain = 'example.com'
        site.save()

        # Create the post
        post = Post()
        post.title = 'My first post'
        post.text = 'This is my first blog post'
        post.slug = 'my-first-post'
        post.pub_date = timezone.now()
        post.author = author
        post.site = site
        post.category = category
        post.save()
        post.tags.add(tag)
        post.save()

        # Check post amended
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)
        only_post = all_posts[0]
        self.assertEquals(only_post, post)

        # fetch the feed
        response = self.client.get('/feeds/posts/')
        self.assertEquals(response.status_code, 200)

        # parse the feed
        feed = feedparser.parse(response.content)

        # check the length
        self.assertEquals(len(feed.entries), 1)

        # check the post retrieved is correct
        feed_post = feed.entries[0]
        self.assertEquals(feed_post.title, post.title)
        self.assertEquals(feed_post.description, post.text)

class FlatePageViewTest(BaseAcceptanceTest):
    def test_create_flat_page(self):
        # create flat page
        page = FlatPage()
        page.url = '/about/'
        page.title = 'About me'
        page.content = 'All about me'
        page.save()

        # add the site
        page.sites.add(Site.objects.all()[0])
        page.save()

        # check new page saved
        all_pages = FlatPage.objects.all()
        self.assertEquals(len(all_pages),1)
        only_page = all_pages[0]
        self.assertEquals(only_page, page)

        # check data correct
        self.assertEquals(only_page.url, '/about/')
        self.assertEquals(only_page.title, 'About me')
        self.assertEquals(only_page.content, 'All about me')

        # get url
        page_url = str(only_page.get_absolute_url())

        # get the page
        response = self.client.get(page_url)
        self.assertEquals(response.status_code, 200)

        # check title and content in response
        self.assertTrue('About me' in response.content)
        self.assertTrue('All about me' in response.content)