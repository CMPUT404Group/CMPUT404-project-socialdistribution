from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from api.models import Author, Post, Comment, Friending
import uuid
import requests
from urllib import urlencode

#global vars
post_id = uuid.uuid4()
c_id = uuid.uuid4()
c_id2 = uuid.uuid4()
date = timezone.now()
pid1 = uuid.uuid4()
pid2 = uuid.uuid4()
pid3 = uuid.uuid4()
pid4 = uuid.uuid4()
pid5 = uuid.uuid4()
pid6 = uuid.uuid4()
pid7 = uuid.uuid4()
pid8 = uuid.uuid4()
pid9 = uuid.uuid4()

# testing creating and getting posts
class ApiPostModelTestCase(TestCase):
    # Model tests - Set up authors and the created post
    def setUp(self):
        user = User.objects.create(username="bob")
        user1 = User.objects.create(username="sam")
        author = Author.objects.create(user=user1, github_name="sammy")
        author1 = Author.objects.create(user=user, github_name="bobby")
        post = Post.objects.create(id=post_id, title="Title", contentType="text/plain", 
        					content="this is my post data", author=author, published=date, 
                            visibility="PUBLIC", image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTu-eC39iANJccZL5c6oKKFdRyRldGt5UT1gCTpXbRkOSb2IFAv")

        Comment.objects.create(id=c_id, post=post, author=author1, contentType="text/plain",
        					comment="this is my comment", published=date)

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
        self.assertEqual(post.contentType, "text/plain")
        self.assertEqual(post.published, date)
        self.assertEqual(post.visibility, "PUBLIC")
        self.assertEqual(post.title, "Title")
        self.assertEqual(post.content, "this is my post data")
        self.assertEqual(post.image_url,"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTu-eC39iANJccZL5c6oKKFdRyRldGt5UT1gCTpXbRkOSb2IFAv")
        response = requests.get(post.image_url)
        self.assertEqual(response.status_code,200)

        #test that we can get an author back
        user = User.objects.get(username="sam")
        author = Author.objects.get(user=user)
        self.assertEqual(author.user.username, "sam")
        self.assertEqual(author.github_name, "sammy")

        #test that we can get the comment back
        comment = Comment.objects.get(id=c_id)
        self.assertEqual(comment.post.id, post_id)
        self.assertEqual(comment.author.user.username, "bob")
        self.assertEqual(comment.contentType, "text/plain")
        self.assertEqual(comment.comment, "this is my comment")
        self.assertEqual(comment.published, date)

        #host multiple authors
        authors = Author.objects.all()
        self.assertTrue(len(authors) > 1)

class ApiUrlsTestCase(TestCase):
    def setUp(self):
        #user and author setup
        user2 = User.objects.create(username="sam")
        user1 = User.objects.create(username="bob")
        user3 = User.objects.create(username="john")
        user = User.objects.create(username='tester', password='12345', is_active=True, is_staff=False, is_superuser=True) 
        user.set_password('hello') 
        user.save()

        sam = Author.objects.create(user=user2, github_name="sammy")
        bob = Author.objects.create(user=user1, github_name="bobby")
        john = Author.objects.create(user=user3, github_name="johnny")
        tester = Author.objects.create(user=user)

        #the tester has no relation to sam, is a FoaF with Bob, and is friends with john
        Friending.objects.create(author=sam, friend=bob)
        Friending.objects.create(author=bob, friend=sam)

        Friending.objects.create(author=bob, friend=john)
        Friending.objects.create(author=john, friend=bob)

        Friending.objects.create(author=tester, friend=john)
        Friending.objects.create(author=john, friend=tester)

        #the tester is a follower of sam
        Friending.objects.create(author=tester, friend=sam)
    

        post = Post.objects.create(id=post_id, title="Title", contentType="text/plain", 
                            content="this is my post data",
                            author=tester, published=date, visibility="PUBLIC")

        post1 = Post.objects.create(id=pid1, title="Title1", contentType="text/plain", 
                            content="this is my hidden post data",
                            author=tester, published=date, visibility="PRIVATE")

        post2 = Post.objects.create(id=pid2, title="Title2", contentType="text/plain", 
                            content="this is my friends private post data",
                            author=john, published=date, visibility="PRIVATE")

        post3 = Post.objects.create(id=pid3, title="Title3", contentType="text/plain", 
                            content="this is my friends public post data",
                            author=john, published=date, visibility="FRIENDS")

        post4 = Post.objects.create(id=pid4, title="Title4", contentType="text/plain", 
                            content="this is my FoaF friend post",
                            author=bob, published=date, visibility="FRIENDS")

        post5 = Post.objects.create(id=pid5, title="Title5", contentType="text/plain", 
                            content="this is my FoaF foaf post",
                            author=bob, published=date, visibility="FOAF")

        post6 = Post.objects.create(id=pid6, title="Title6", contentType="text/plain", 
                            content="this is my following private post data",
                            author=sam, published=date, visibility="PRIVATE")

        post7 = Post.objects.create(id=pid7, title="Title7", contentType="text/plain", 
                            content="this is my following public post data",
                            author=sam, published=date, visibility="PUBLIC")

        post8 = Post.objects.create(id=pid8, title="Title8", contentType="text/plain", 
                            content="this is the message i sent to tester",
                            author=sam, published=date, visibility="OTHERAUTHOR",
                            other_author=tester)

        post9 = Post.objects.create(id=pid9, title="Title8", contentType="text/plain", 
                            content="this is the message i didnt sent to tester",
                            author=john, published=date, visibility="OTHERAUTHOR",
                            other_author=bob)

        Comment.objects.create(id=c_id, post=post7, author=bob, contentType="text/plain",
                            comment="this is my comment", published=date)

    #test that people cant edit/delete other peoples posts and comments
    def test_posts_notAllowed(self):
        #login
        login = self.client.login(username='tester', password='hello') 
        self.assertTrue(login)

        #test that we can't edit someone else's post
        post_data = {"title":"Changed Title","content":"changed post data","contentType":"text/plain","visibility":"PRIVATE"}
        resp1= self.client.put("/api/posts/"+str(pid7)+"/", urlencode(post_data),content_type = 'application/x-www-form-urlencoded')
        self.assertEqual(resp1.status_code,403)

        #check if he can delete his post
        resp2= self.client.delete("/api/posts/"+str(pid7)+"/")
        self.assertEqual(resp2.status_code,403)

        #Check that things were correctly updated
        posts = Post.objects.filter(id=pid7)
        self.assertEqual(len(posts),1)

        #check that we cant delete a comment
        resp6= self.client.delete("/api/posts/"+str(pid7)+"/comments/"+str(c_id))
        self.assertEqual(resp6.status_code,403)

        #Check that things were correctly left alone
        comments = Comment.objects.filter(id=c_id)
        self.assertEqual(len(comments),1)


    #test that people can add/edit/delete their own posts and comments
    def test_posts_allowed(self):
        #login
        login = self.client.login(username='tester', password='hello') 
        self.assertTrue(login)

        post_data_new = {"title":"New Title","content":"new body data","contentType":"text/plain","visibility":"PUBLIC"}
        post_data_e = {"title":"Changed Title","content":"changed post data","contentType":"text/plain","visibility":"PRIVATE"}

        #test that we were able to make a new post
        resp1= self.client.post("/api/posts/", post_data_new)
        self.assertEqual(resp1.status_code,201)

        #test that the information is correct
        new_post = Post.objects.get(title="New Title")
        newpid = new_post.id
        self.assertEqual(new_post.content,"new body data")
        self.assertEqual(new_post.contentType,"text/plain")
        self.assertEqual(new_post.visibility,"PUBLIC")

        #test that we can edit the post
        resp2= self.client.put("/api/posts/"+str(newpid)+"/", urlencode(post_data_e),content_type = 'application/x-www-form-urlencoded')
        self.assertEqual(resp2.status_code,200)

        #Check that things were correctly updated
        changed_post = Post.objects.get(id=newpid)
        self.assertEqual(changed_post.content,"changed post data")
        self.assertEqual(changed_post.contentType,"text/plain")
        self.assertEqual(changed_post.visibility,"PRIVATE")

        #check if he can delete his post
        resp3= self.client.delete("/api/posts/"+str(newpid)+"/")
        self.assertEqual(resp3.status_code,204)

        #Check that things were correctly updated
        posts = Post.objects.filter(id=newpid)
        self.assertEqual(len(posts),0)

        #check that we can add a comment
        new_comment = {"comment":"this is my new comment", "contentType":"text/plain"}
        resp4= self.client.post("/api/posts/"+str(pid7)+"/comments/",new_comment)
        self.assertEqual(resp4.status_code,201)
        comment = Comment.objects.get(comment="this is my new comment")
        self.assertEqual(comment.contentType,"text/plain")

        #check that we can edit a comment
        changed_comment = {"comment":"this is my changed comment", "contentType":"text/plain"}
        resp5= self.client.put("/api/posts/"+str(pid7)+"/comments/"+str(comment.id),urlencode(changed_comment),content_type = 'application/x-www-form-urlencoded')
        self.assertEqual(resp5.status_code,200)

        self.assertContains(resp5,"this is my changed comment")
        self.assertContains(resp5,"text/plain")

        #check that we can delete a comment
        resp6= self.client.delete("/api/posts/"+str(pid7)+"/comments/"+str(comment.id))
        self.assertEqual(resp6.status_code,204)

        #Check that things were correctly updated
        comments = Comment.objects.filter(id=newpid)
        self.assertEqual(len(comments),0)

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

        resp2 = self.client.get("/author/vanbelle/")
        self.assertEqual(resp2.status_code, 302)
        split = resp2.get("location").split("/")
        path = split[3] + "/" + split[4]
        self.assertEqual(path, "accounts/login")

        #check an existing post is not  viewable since the user is not logged in
        resp = self.client.get("/post/"+str(pid7)+"/")
        resp1 = self.client.get("/post/"+str(pid7)+"/success/")
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp1.status_code, 302)

        #check the redirect path
        split = resp.get("location").split("/")
        path = split[3] + "/" + split[4]
        split1 = resp1.get("location").split("/")
        path1 = split1[3] + "/" + split1[4]
        self.assertEqual(path, "accounts/login")
        self.assertEqual(path1, "accounts/login")

    def test_view_access(self):
    	#login
        login = self.client.login(username='tester', password='hello') 
        self.assertTrue(login)

        #check an existing post is viewable now that they are logged in
        resp1 = self.client.get("/post/"+str(post_id)+"/") #my public post is viewable
        resp2 = self.client.get("/") #home stream
        resp3 = self.client.get("/myStream/") #mystream
        resp4 = self.client.get("/author/tester/") #my profile
        resp5 = self.client.get("/post/"+str(pid1)+"/")
        resp6 = self.client.get("/post/"+str(pid2)+"/")
        resp7 = self.client.get("/post/"+str(pid3)+"/")
        resp8 = self.client.get("/post/"+str(pid4)+"/")
        resp9 = self.client.get("/post/"+str(pid5)+"/")
        resp10 = self.client.get("/post/"+str(pid6)+"/")
        resp11 = self.client.get("/post/"+str(pid7)+"/")
        resp12 = self.client.get("/author/bob/")
        resp13 = self.client.get("/post/"+str(pid8)+"/")
        resp14 = self.client.get("/post/"+str(pid9)+"/")

        u = User.objects.get(username="tester")
        user = Author.objects.get(user=u)

        #my pages should be accessible
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp3.status_code, 200)
        self.assertEqual(resp4.status_code, 200)
        self.assertEqual(resp5.status_code, 200)       
        #this should not since it is private to my friend
        self.assertEqual(resp6.status_code, 403)
        #this i should since it is friends only and i am a friend
        self.assertEqual(resp7.status_code, 200)
        #this is for friends but was written by a afoaf so should be private
        self.assertEqual(resp8.status_code, 403)
        #this was by a foaf for foafs
        self.assertEqual(resp9.status_code, 200)
        #i am following this person but it is private 
        self.assertEqual(resp10.status_code, 403)
        #this one is public so i should see it
        self.assertEqual(resp11.status_code, 200)
        #this is bobs profile and is visible       
        self.assertEqual(resp12.status_code, 200)
        #this should be viewable since it was sent to me
        self.assertEqual(resp13.status_code, 200)
        #this should not be viewable since it was sent to someone else
        self.assertEqual(resp14.status_code, 403)

        #check that the content of the post and comment are viewable along 
        #with their authors from the page url ./post/<post id>
        self.assertContains(resp1,"this is my post data")
        self.assertContains(resp1, "tester")
        self.assertFalse("this is the message i sent to tester" in str(resp1))

        #check thats the public post is also viewable from the main page, 
        #but that the private stuff is not viewable
        self.assertContains(resp2,"this is my post data")
        self.assertContains(resp2,"this is my following public post data")
        self.assertFalse("this is my hidden post data" in str(resp2)) 
        self.assertFalse("this is my friends private post data" in str(resp2)) 
        self.assertFalse("this is my FoaF friend post" in str(resp2))
        self.assertFalse("this is my FoaF foaf post" in str(resp2))
        self.assertFalse("this is the message i sent to tester" in str(resp2))

        #check that both my posts are viewable from the myStream page   
        #check also that the posts from my friends and FOFs and the people i am 
        #following are visiblie 
        self.assertContains(resp3,"this is my post data")
        self.assertContains(resp3,"this is my hidden post data")
        self.assertContains(resp3,"this is my friends public post data")
        self.assertContains(resp3,"this is my following public post data")
        self.assertFalse("this is my friends private post data" in str(resp3))
        self.assertContains(resp3, "this is the message i sent to tester")
     
        #check that my posts are on my profile page and that other posts arent 
        self.assertContains(resp4,"this is my post data")
        self.assertFalse("this is my following public post data" in str(resp4))
        self.assertFalse("this is the message i sent to tester" in str(resp4))

        #the page for my private post
        self.assertContains(resp5,"this is my hidden post data")

        #check that my friends private post is hidden but the public one is public

        #resp6/8/10/14 should not be viewable so we dont need to check what they contain

        #check that the viewable posts contain what they should
        self.assertContains(resp7,"this is my friends public post data")
        self.assertContains(resp9,"this is my FoaF foaf post")
        self.assertContains(resp11,"this is my following public post data")
        #check the comment is there too
        self.assertContains(resp11, "this is my comment")
        #self.assertContains(resp12,"this is my FoaF foaf post")
        self.assertFalse("this is the message i sent to tester" in str(resp12))
        self.assertFalse("this is my FoaF friend post" in str(resp12))
        #this is the private post to tester
        self.assertContains(resp13, "this is the message i sent to tester")
