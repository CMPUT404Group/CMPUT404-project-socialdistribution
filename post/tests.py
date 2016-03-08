from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from post.forms import PostForm, CommentForm
from post.models import Author, Post, Comment
import random

# create the post ids as global variables
p_id1 = random.randint(0, 1000000)
p_id2 = random.randint(0, 1000000)
date = timezone.now()

class CommentModelTestCase(TestCase):
    def test_get_comment(self):
        user = User.objects.create(username="kevin")
        author = Author.objects.create(author=user, github_name="kevin", status="P")
        #comment = Comment.objects.create(comment_id=random.randint(0, 1000000))



class PostModelTestCase(TestCase):
    # Model tests - Set up authors and the created post
    def setUp(self):
        user = User.objects.create(username="bob")
        author = Author.objects.create(author=user, github_name="bobby", status="P")
        user2 = User.objects.create(username="sam")
        author2 = Author.objects.create(author=user2, github_name="sammy", status="P")
        Post.objects.create(post_id=p_id1, author=author, content_type="TX",
                            pub_date=date, privilege="ME", title="Title",
                            post_text="this is my post data", recipient=author2)
        Post.objects.create(post_id=p_id2, author=author, content_type="MG",
                            pub_date=date, privilege="FF", title="Title",
                            post_text="this is my post data",
                            img_url="https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcTp95Lq61UlbSSa2h40Cpt-Q8NBYxkKhGoUirr04TYzzgeArnQK9VKJhZaz",
                            recipient=author2)

    # check that the post is an instance of the post
    def test_is_post(self):
        post = Post.objects.get(post_id=p_id1)
        self.assertTrue(isinstance(post, Post))

    # check for all the correct values in a regular post
    def test_get_post_1(self):
        post = Post.objects.get(post_id=p_id1)
        self.assertEqual(post.author.author.username, "bob")
        self.assertEqual(post.author.github_name, "bobby")
        self.assertEqual(post.author.status, "P")
        self.assertEqual(post.content_type, "TX")
        self.assertEqual(post.pub_date, date)
        self.assertEqual(post.privilege, "ME")
        self.assertEqual(post.title, "Title")
        self.assertEqual(post.post_text, "this is my post data")
        self.assertEqual(post.recipient.author.username, "sam")

    # check the values for an image post
    def test_get_post_2(self):
        post = Post.objects.get(post_id=p_id2)
        self.assertEqual(post.author.author.username, "bob")
        self.assertEqual(post.author.github_name, "bobby")
        self.assertEqual(post.author.status, "P")
        self.assertEqual(post.content_type, "MG")
        self.assertEqual(post.pub_date, date)
        self.assertEqual(post.privilege, "FF")
        self.assertEqual(post.title, "Title")
        self.assertEqual(post.img_url,
                         "https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcTp95Lq61UlbSSa2h40Cpt-Q8NBYxkKhGoUirr04TYzzgeArnQK9VKJhZaz")
        self.assertEqual(post.post_text, "this is my post data")
        self.assertEqual(post.recipient.author.username, "sam")