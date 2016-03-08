from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from api.models import Author, Post, Comment
import random
import uuid

post_id = uuid.uuid4()
post_id2 = uuid.uuid4()
date = timezone.now()
# testing creating and getting posts
class ApiPostModelTestCase(TestCase):
    # Model tests - Set up authors and the created post
    def setUp(self):
        user = User.objects.create(username="bob")
        Post.objects.create(id=post_id, title="Title", contentType="PLAINTEXT", 
        					content="this is my post data",
        					author=user, published=date, visibility="PUBLIC")

    # check that the post is an instance of the post
    def test_is_post(self):
        post = Post.objects.get(id=post_id)
        self.assertTrue(isinstance(post, Post))

    # check for all the correct values in a regular post
    def test_get_post_1(self):
        post = Post.objects.get(id=post_id)
        self.assertEqual(post.author.username, "bob")
        self.assertEqual(post.contentType, "PLAINTEXT")
        self.assertEqual(post.published, date)
        self.assertEqual(post.visibility, "PUBLIC")
        self.assertEqual(post.title, "Title")
        self.assertEqual(post.content, "this is my post data")

class PostUrlsTestCase(TestCase):
    def test_redirect_to_login(self):
        # check that it redirects to the login page
        # when the user is not signed in
        resp = self.client.get("/")
        self.assertTrue(resp.status_code, 302)
        split = resp.get("location").split("/")
        path = split[3] + "/" + split[4]
        self.assertEqual(path, "accounts/login")

        resp1 = self.client.get("/myStream/")
        self.assertEqual(resp1.status_code, 302)
        split = resp1.get("location").split("/")
        path = split[3] + "/" + split[4]

        resp2 = self.client.get("/user/vanbelle/")
        self.assertEqual(resp2.status_code, 302)
        split = resp2.get("location").split("/")
        path = split[3] + "/" + split[4]

    def test_access(self):
        # login to the page
        self.user = User.objects.create(username='testuser', password='12345', is_active=True, is_staff=True, is_superuser=True) 
        self.user.set_password('hello') 
        self.user.save() 
        login = self.client.login(username='testuser', password='hello') 
        self.assertTrue(login)
        self.client.session.save()

        #check access to the other pages once the user is logged in 
        resp1 = self.client.get("/")
        resp2 = self.client.get("/myStream/")
        resp3 = self.client.get("/user/vanbelle/")
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp3.status_code, 200)

        #check an existing post is viewable
        user = User.objects.create(username="sam")
        Post.objects.create(id=post_id2, title="Title", contentType="PLAINTEXT", 
        					content="this is my post data",
        					author=user, published=date, visibility="PUBLIC")
        resp4 = self.client.get("/post/"+str(post_id2)+"/")
        self.assertEqual(resp4.status_code, 200)
        