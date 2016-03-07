from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from post.forms import PostForm, CommentForm
from post.models import Author, Post
import random

p_id = random.randint(0,1000000)
date = timezone.now()

class PostTestCase(TestCase):

    def setUp(self):
        user = User.objects.create(username="bob")
        author = Author.objects.create(author=user, github_name="bobby", status="P")
        user2 = User.objects.create(username="sam")
        author2 = Author.objects.create(author=user2, github_name="sammy", status="P")
        Post.objects.create(post_id=p_id,author=author, content_type="TX", 
            pub_date=date,privilege="ME",title="Title", 
            post_text="this is my post data", recipient=author2)

    def test_is_post(self):
        post = Post.objects.get(post_id=p_id)
        self.assertTrue(isinstance(post, Post))

    def test_get_post(self):
        post = Post.objects.get(post_id=p_id)
        self.assertEqual(post.author.author.username, "bob")
        self.assertEqual(post.author.github_name, "bobby")
        self.assertEqual(post.author.status, "P")
        self.assertEqual(post.content_type, "TX")
        self.assertEqual(post.pub_date, date)
        self.assertEqual(post.privilege,"ME")
        self.assertEqual(post.title, "Title")
        self.assertEqual(post.post_text,"this is my post data")
        self.assertEqual(post.recipient.author.username, "sam")