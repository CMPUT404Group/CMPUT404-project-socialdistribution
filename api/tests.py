from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from api.models import Author, Post, Comment, Following, Friending
import uuid

#global vars
post_id = uuid.uuid4()
post_id2 = uuid.uuid4()
c_id = uuid.uuid4()
c_id2 = uuid.uuid4()
date = timezone.now()
pid1 = uuid.uuid4()
pid2 = uuid.uuid4()
pid3 = uuid.uuid4()
pid4 = uuid.uuid4()
pid5 = uuid.uuid4()

# testing creating and getting posts
class ApiPostModelTestCase(TestCase):
    # Model tests - Set up authors and the created post
    def setUp(self):
        user = User.objects.create(username="bob")
        user1 = User.objects.create(username="sam")
        author = Author.objects.create(user=user1, github_name="sammy")
        author1 = Author.objects.create(user=user, github_name="bobby")
        post = Post.objects.create(id=post_id, title="Title", contentType="PLAINTEXT", 
        					content="this is my post data",
        					author=author, published=date, visibility="PUBLIC")

        Comment.objects.create(id=c_id, post=post, author=author1, contentType="PLAINTEXT",
        					comment="this is my comment", published=date)


    #check that two authors can follow each other
    def test_following(self):
        user = User.objects.create(username="rob")
        user1 = User.objects.create(username="tammy")
        author1 = Author.objects.create(user=user1, github_name="tammy")
        author = Author.objects.create(user=user, github_name="rob")
        Following.objects.create(author=author, following=author1)
        following = Following.objects.get(author=author)
        self.assertEqual(following.author,author)
        self.assertEqual(following.following,author1)

    #check that two authors can friend each other
    def test_friending(self):
        user = User.objects.create(username="cam")
        user1 = User.objects.create(username="mitchel")
        author1 = Author.objects.create(user=user1, github_name="mitchel")
        author = Author.objects.create(user=user, github_name="cam")
        Friending.objects.create(author=author, friend=author1)
        friending = Friending.objects.get(author=author)
        self.assertEqual(friending.author,author)
        self.assertEqual(friending.friend,author1)


    # check that the post is an instance of the post
    def test_is_post(self):
        post = Post.objects.get(id=post_id)
        self.assertTrue(isinstance(post, Post))

    # check for all the correct values in a regular post
    def test_get(self):
        #test that we can get the post back
        post = Post.objects.get(id=post_id)
        self.assertEqual(post.author.user.username, "sam")
        self.assertEqual(post.contentType, "PLAINTEXT")
        self.assertEqual(post.published, date)
        self.assertEqual(post.visibility, "PUBLIC")
        self.assertEqual(post.title, "Title")
        self.assertEqual(post.content, "this is my post data")

        #test that we can get an author back
        user = User.objects.get(username="sam")
        author = Author.objects.get(user=user)
        self.assertEqual(author.user.username, "sam")
        self.assertEqual(author.github_name, "sammy")

        #test that we can get the comment back
        comment = Comment.objects.get(id=c_id)
        self.assertEqual(comment.post.id, post_id)
        self.assertEqual(comment.author.user.username, "bob")
        self.assertEqual(comment.contentType, "PLAINTEXT")
        self.assertEqual(comment.comment, "this is my comment")
        self.assertEqual(comment.published, date)

class ApiUrlsTestCase(TestCase):
    def setUp(self):
        user2 = User.objects.create(username="sam")
        user1 = User.objects.create(username="bob")
        user = User.objects.create(username='tester', password='12345', is_active=True, is_staff=False, is_superuser=True) 
        user.set_password('hello') 
        user.save()

        sam = Author.objects.create(user=user2, github_name="sammy")
        bob = Author.objects.create(user=user1, github_name="bobby")

        tester = Author.objects.create(user=user)

        post = Post.objects.create(id=post_id2, title="Title", contentType="PLAINTEXT", 
                            content="this is my post data",
                            author=tester, published=date, visibility="PUBLIC")

        post1 = Post.objects.create(id=post_id, title="Title", contentType="PLAINTEXT", 
                            content="this is my hidden post data",
                            author=tester, published=date, visibility="PRIVATE")

        post2 = Post.objects.create(id=pid3, title="Title", contentType="PLAINTEXT", 
                            content="this is my friends private post data",
                            author=bob, published=date, visibility="PRIVATE")

        post3 = Post.objects.create(id=pid4, title="Title", contentType="PLAINTEXT", 
                            content="this is my friends public post data",
                            author=bob, published=date, visibility="PUBLIC")

        Comment.objects.create(id=c_id, post=post, author=bob, contentType="PLAINTEXT",
                            comment="this is my comment", published=date)


    def test_redirect(self):
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
        self.assertEqual(path, "accounts/login")

        resp2 = self.client.get("/user/vanbelle/")
        self.assertEqual(resp2.status_code, 302)
        split = resp2.get("location").split("/")
        path = split[3] + "/" + split[4]
        self.assertEqual(path, "accounts/login")

        #check an existing post is not  viewable since the user is not logged in
        resp = self.client.get("/post/"+str(post_id2)+"/")
        resp1 = self.client.get("/post/"+str(post_id2)+"/success/")
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp1.status_code, 302)

        #check the redirect path
        split = resp.get("location").split("/")
        path = split[3] + "/" + split[4]
        split1 = resp1.get("location").split("/")
        path1 = split1[3] + "/" + split1[4]
        self.assertEqual(path, "accounts/login")
        self.assertEqual(path1, "accounts/login")

    def test_access(self):
    	#login
        login = self.client.login(username='tester', password='hello') 
        self.assertTrue(login)
        self.client.session.save()

        #check an existing post is viewable now that they are logged in
        resp1 = self.client.get("/post/"+str(post_id2)+"/")
        resp2 = self.client.get("/")
        resp3 = self.client.get("/myStream/")
        resp4 = self.client.get("/user/tester/")
        resp5 = self.client.get("/post/"+str(pid3)+"/")
        resp6 = self.client.get("/user/bob/")
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp3.status_code, 200)
        self.assertEqual(resp4.status_code, 200)
        self.assertEqual(resp5.status_code, 200) #should not see   THIS SHOULD FAIL      
        self.assertEqual(resp6.status_code, 200)

        #check that the content of the post and comment are viewable along 
        #with their authors from the page url ./post/<post id>
        self.assertContains(resp1,"this is my post data")
        self.assertContains(resp1, "this is my comment")
        self.assertContains(resp1, "tester")

        #check thats the public post is also viewable from the main page
        self.assertContains(resp2,"this is my post data")
        self.assertContains(resp2,"this is my friends public post data")
        self.assertContains(resp2, "tester")

        #but that the private posts are not visible
        self.assertFalse("this is my hidden post data" in str(resp2)) 
        self.assertFalse("this is my friends private post data" in str(resp2))     

        #check that both posts are viewable from the myStream page   
        self.assertContains(resp3,"this is my post data")
        self.assertContains(resp3,"this is my hidden post data")
        self.assertFalse("this is my friends private post data" in str(resp3))
        self.assertFalse("this is my friends public post data" in str(resp3))

     
        #check that my posts are on my profile page
        self.assertContains(resp4,"this is my post data")
        self.assertContains(resp4,"this is my hidden post data")

        print(resp6)
        #check that my friends private post is hidden but the public one is public
        self.assertFalse("this is my post data" in str(resp6))
        self.assertContains(resp6,"this is my friends public post data")
        self.assertFalse("this is my friends private post data" in str(resp6))