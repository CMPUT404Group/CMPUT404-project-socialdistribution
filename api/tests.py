from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from api.models import Author, Post, Comment, Friending
import uuid
import requests
from urllib import urlencode
from rest_framework import HTTP_HEADER_ENCODING
import base64
from rest_framework.test import APIClient
from rest_framework import status
from api.serializers import AuthorSerializer, PostSerializer
import copy

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
pid10 = uuid.uuid4()
pid11 = uuid.uuid4()
tester_id = uuid.uuid4()
other = uuid.uuid4()

class APIPostList(TestCase):
    def setUp(self):
        client = APIClient()

        validUser = User.objects.create(username="tester")
        validUser.set_password('testing')
        validUser.save()

        self.author = Author.objects.create(user=validUser, github="tester", host='testserver')

    # def test_unauthenticated(self):
    #     resp1 = self.client.get('/api/posts/')
    #     self.assertEqual(resp1.status_code, 401)
    #
    # def test_invalid_authentication(self):
    #     client = APIClient()
    #     username = "tester"
    #     wrong_password = "TESTING"
    #     string1 = username + ":" + wrong_password
    #     basicAuthEncoding =  base64.b64encode(string1)
    #     resp1 = self.client.get("/api/posts/", authorization="Basic " + basicAuthEncoding)
    #     self.assertEqual(resp1.status_code, 401)

    def test_valid_authentication(self):
        client = APIClient()
        username = "tester"
        correct_password = "testing"
        string2 = username + ":" + correct_password
        basicAuthEncoding2 =  base64.encodestring(string2)
        client.credentials(HTTP_AUTHORIZATION='Basic ' + basicAuthEncoding2)
        response = client.get('/api/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_success_post(self):
        client = APIClient()
        username = "tester"
        correct_password = "testing"
        string2 = username + ":" + correct_password
        basicAuthEncoding2 =  base64.encodestring(string2)
        client.credentials(HTTP_AUTHORIZATION='Basic ' + basicAuthEncoding2)
        post = { 'title': 'my title', 'contentType': 'text/plain', 'content': "hello world", 'visibility': Post.PUBLIC }
        response = client.post('/api/posts/', post , format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(response.data, post)


class APIPostDetail(TestCase):
    def setUp(self):
        client = APIClient()

        # fake
        fakeUsername = "fake"
        fakePassword = "fake"
        self.basicAuthEncodingFake =  base64.encodestring(fakeUsername + ":" + fakePassword)

        username1 = "tester1"
        password1 = "testing1"
        user1 = User.objects.create(username=username1)
        user1.set_password(password1)
        user1.save()
        author1 = Author.objects.create(user=user1, github=username1, host="testserver")
        self.basicAuthEncoding1 =  base64.encodestring(username1 + ":" + password1)

        username2 = "tester2"
        password2 = "testing2"
        user2 = User.objects.create(username=username2)
        user2.set_password(password2)
        user2.save()
        author2 = Author.objects.create(user=user2, github=username2, host="testserver")
        self.basicAuthEncoding2 =  base64.encodestring(username2 + ":" + password2)

        username3 = "tester3"
        password3 = "testing3"
        user3 = User.objects.create(username=username3)
        user3.set_password(password3)
        user3.save()
        author3 = Author.objects.create(user=user3, github=username3, host="testserver")
        self.basicAuthEncoding3 =  base64.encodestring(username3 + ":" + password3)

        # 1 friends with 2
        friendshipPartA = Friending.objects.create(author=author1, friend=author2)
        friendshipPartB = Friending.objects.create(author=author2, friend=author1)

        # public post by author1
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding1)
        post = { 'title': 'my title', 'contentType': 'text/plain', 'content': "hello world", 'visibility': Post.PUBLIC }
        response = client.post('/api/posts/', post , format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.publicPost = response.data

        # friends post by author1
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding1)
        friendsPost = { 'title': "for friends", 'contentType': 'text/plain', 'content': "hello world", 'visibility': Post.FRIENDS }
        response = client.post('/api/posts/', friendsPost , format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.friendsPost = response.data

    def test_get_public_post(self):
        client = APIClient()
        # client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding2)
        response = client.get('/api/posts/' + str(self.publicPost["id"]) + "/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.publicPost)

    def test_get_valid_friends_post(self):
        client = APIClient()

        # ensure friends can see it
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding2)
        response = client.get('/api/posts/' + str(self.friendsPost["id"]) + "/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.friendsPost)

        # ensure non-friends can't see it - no longer supported due to just returning everything & letting other nodes handle this filtering
        # client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding3)
        # response = client.get('/api/posts/' + str(self.friendsPost["id"]) + "/")
        # self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_nonexisting_post(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding2)
        nonexistingPostId = uuid.uuid4()
        response = client.get('/api/posts/' + str(nonexistingPostId) + "/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_unauthorized(self):
        client = APIClient()
        # no credentials
        response = client.get('/api/posts/' + str(self.friendsPost["id"]) + "/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # fake credentials
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncodingFake)
        response = client.get('/api/posts/' + str(self.friendsPost["id"]) + "/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_success(self):
        client = APIClient()

        # public post by author1
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding1)
        post = { 'title': 'my title', 'contentType': 'text/plain', 'content': "hello world", 'visibility': Post.PUBLIC }
        response = client.post('/api/posts/', post , format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        publicPost = response.data

        response = client.delete('/api/posts/' + str(publicPost["id"]) + "/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_not_author(self):
        client = APIClient()

       # public post by author1
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding1)
        post = { 'title': 'my title', 'contentType': 'text/plain', 'content': "hello world", 'visibility': Post.PUBLIC }
        response = client.post('/api/posts/', post , format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        publicPost = response.data

        # author2 try to delete
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding2)
        response = client.delete('/api/posts/' + publicPost["id"] + "/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_non_existing_post(self):
        client = APIClient()

       # public post by author1
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding1)
        post = { 'title': 'my title', 'contentType': 'text/plain', 'content': "hello world", 'visibility': Post.PUBLIC }
        response = client.post('/api/posts/', post , format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        publicPost = response.data

        # author2 try to delete
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding1)
        nonexistingPostId = uuid.uuid4()
        response = client.delete('/api/posts/' + str(nonexistingPostId) + "/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_success(self):
        client = APIClient()

        # public post by author1
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding1)
        post = { 'title': 'my title', 'contentType': 'text/plain', 'content': "hello world", 'visibility': Post.PUBLIC }
        response = client.post('/api/posts/', post , format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        publicPost = response.data

        editedPost = copy.deepcopy(publicPost)
        editedPost["title"] = "EDITED TITLE"
        response = client.put('/api/posts/' + str(publicPost["id"]) + "/", editedPost, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ignore dates difference due to after put update
        response.data["published"] = ""
        editedPost["published"] = ""
        self.assertEqual(response.data, editedPost)

    def test_put_not_author(self):
        client = APIClient()

        # public post by author1
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding1)
        post = { 'title': 'my title', 'contentType': 'text/plain', 'content': "hello world", 'visibility': Post.PUBLIC }
        response = client.post('/api/posts/', post , format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        publicPost = response.data

        # author2 try to edit
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding2)
        editedPost = copy.deepcopy(publicPost)
        editedPost["title"] = "EDITED TITLE"
        response = client.put('/api/posts/' + str(publicPost["id"]) + '/', editedPost, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_non_existing_post(self):
        client = APIClient()

       # public post by author1
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding1)
        post = { 'title': 'my title', 'contentType': 'text/plain', 'content': "hello world", 'visibility': Post.PUBLIC }
        response = client.post('/api/posts/', post , format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        publicPost = response.data

        # author2 try to delete
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding1)
        nonexistingPostId = uuid.uuid4()
        editedPost = copy.deepcopy(publicPost)
        editedPost["title"] = "EDITED TITLE"
        response = client.put('/api/posts/' + str(nonexistingPostId) + '/', editedPost, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class APICommentList(TestCase):
    def setUp(self):
        client = APIClient()

        # fake
        fakeUsername = "fake"
        fakePassword = "fake"
        self.basicAuthEncodingFake =  base64.encodestring(fakeUsername + ":" + fakePassword)

        username1 = "tester"
        password1 = "testing"
        user1 = User.objects.create(username=username1)
        user1.set_password(password1)
        user1.save()
        author1 = Author.objects.create(user=user1, github=username1, host="testserver")
        self.basicAuthEncoding1 =  base64.encodestring(username1 + ":" + password1)

        username2 = "tester2"
        password2 = "testing2"
        user2 = User.objects.create(username=username2)
        user2.set_password(password2)
        user2.save()
        author2 = Author.objects.create(user=user2, github=username2, host="testserver")
        self.basicAuthEncoding2 =  base64.encodestring(username2 + ":" + password2)

        username3 = "tester3"
        password3 = "testing3"
        user3 = User.objects.create(username=username3)
        user3.set_password(password3)
        user3.save()
        author3 = Author.objects.create(user=user3, github=username3, host="testserver")
        self.basicAuthEncoding3 =  base64.encodestring(username3 + ":" + password3)

        # 1 friends with 2
        friendshipPartA = Friending.objects.create(author=author1, friend=author2)
        friendshipPartB = Friending.objects.create(author=author2, friend=author1)

        # public post by author1
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding1)
        self.post = { 'title': 'my title', 'contentType': 'text/plain', 'content': "hello world", 'visibility': Post.PUBLIC }
        response = client.post('/api/posts/', self.post , format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.publicPost = response.data

        # friends post by author1
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding1)
        post = { 'title': "for friends", 'contentType': 'text/plain', 'content': "hello world", 'visibility': Post.FRIENDS }
        response = client.post('/api/posts/', post , format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.friendsPost = response.data

    def test_get_invalid_authentication(self):
        client = APIClient()
        username = "tester"
        wrong_password = "TESTING"
        string1 = username + ":" + wrong_password
        basicAuthEncoding =  base64.b64encode(string1)
        resp1 = self.client.get("/api/posts/" + str(self.friendsPost["id"]) + "/comments/", authorization="Basic " + basicAuthEncoding)
        self.assertEqual(resp1.status_code, 401)

    def test_get_valid_authentication(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding2)
        response = client.get('/api/posts/' + str(self.publicPost["id"]) + "/comments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_comment_success(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding2)
        serializer = PostSerializer(Post.objects.get(id=self.publicPost["id"]))
        post = serializer.data
        comment = {"comment": "hello world", "contentType": "text/plain", "post": post}
        response = client.post('/api/posts/' + str(self.publicPost["id"]) + "/comments/", comment , format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(response.data, post)

    def test_post_non_existing_post_comment(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding2)
        serializer = PostSerializer(Post.objects.get(id=self.publicPost["id"]))
        post = serializer.data
        comment = {"comment": "hello world", "contentType": "text/plain", "post": post}
        response = client.post('/api/posts/' + str(uuid.uuid4()) + "/comments/", comment , format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_not_allowed_comment(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding3)
        serializer = PostSerializer(Post.objects.get(id=self.friendsPost["id"]))
        post = serializer.data
        comment = {"comment": "hello world", "contentType": "text/plain", "post": post}
        response = client.post('/api/posts/' + str(self.friendsPost["id"]) + "/comments/", comment , format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class APICommentDetail(TestCase):
    def setUp(self):
        client = APIClient()

        # fake
        fakeUsername = "fake"
        fakePassword = "fake"
        self.basicAuthEncodingFake =  base64.encodestring(fakeUsername + ":" + fakePassword)

        username1 = "tester"
        password1 = "testing"
        user1 = User.objects.create(username=username1)
        user1.set_password(password1)
        user1.save()
        author1 = Author.objects.create(user=user1, github=username1, host="testserver")
        self.basicAuthEncoding1 =  base64.encodestring(username1 + ":" + password1)

        username2 = "tester2"
        password2 = "testing2"
        user2 = User.objects.create(username=username2)
        user2.set_password(password2)
        user2.save()
        author2 = Author.objects.create(user=user2, github=username2, host="testserver")
        self.basicAuthEncoding2 =  base64.encodestring(username2 + ":" + password2)

        username3 = "tester3"
        password3 = "testing3"
        user3 = User.objects.create(username=username3)
        user3.set_password(password3)
        user3.save()
        author3 = Author.objects.create(user=user3, github=username3, host="testserver")
        self.basicAuthEncoding3 =  base64.encodestring(username3 + ":" + password3)

        # 1 friends with 2
        friendshipPartA = Friending.objects.create(author=author1, friend=author2)
        friendshipPartB = Friending.objects.create(author=author2, friend=author1)

        # public post by author1
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding1)
        self.post = { 'title': 'my title', 'contentType': 'text/plain', 'content': "hello world", 'visibility': Post.PUBLIC }
        response = client.post('/api/posts/', self.post , format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.publicPost = response.data

        # friends post by author1
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding1)
        post = { 'title': "for friends", 'contentType': 'text/plain', 'content': "hello world", 'visibility': Post.FRIENDS }
        response = client.post('/api/posts/', post , format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.friendsPost = response.data

        serializer = PostSerializer(Post.objects.get(id=self.publicPost["id"]))
        postData = serializer.data
        publicComment = {"comment": "hello world", "contentType": "text/plain", "post": postData}
        response = client.post('/api/posts/' + str(self.publicPost["id"]) + "/comments/", publicComment , format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.publicComment = response.data

        serializer = PostSerializer(Post.objects.get(id=self.friendsPost["id"]))
        postData = serializer.data
        friendsComment = {"comment": "hello world", "contentType": "text/plain", "post": postData}
        response = client.post('/api/posts/' + str(self.friendsPost["id"]) + "/comments/", friendsComment , format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.friendsComment = response.data

#     def test_get_valid_friends_comment(self):
#         client = APIClient()
#
#         # ensure friends can see it
#         client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding2)
#         response = client.get('/api/posts/' + str(self.friendsPost["id"]) + "/comments/" + str(self.friendsComment["id"]))
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data, self.friendsComment)
#
#         # ensure non-friends can't see it
#         client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding3)
#         response = client.get('/api/posts/' + str(self.friendsPost["id"]) + "/comments/" + str(self.friendsComment["id"]))
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_nonexisting_comment(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding2)
        nonexistingPostId = uuid.uuid4()
        response = client.get('/api/posts/' + str(nonexistingPostId) + "/comments/" + str(self.publicComment["id"]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        nonexistingCommentId = uuid.uuid4()
        response = client.get('/api/posts/' + str(self.publicPost["id"]) + "/comments/" + str(nonexistingCommentId))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_unauthorized_comment(self):
        client = APIClient()
        # no credentials
        response = client.get('/api/posts/' + str(self.publicPost["id"]) + "/comments/" + str(self.publicComment["id"]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # fake credentials
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncodingFake)
        response = client.get('/api/posts/' + str(self.publicPost["id"]) + "/comments/" + str(self.publicComment["id"]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



    def test_delete_comment_success(self):
        client = APIClient()

        # public comment by author1
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding1)
        serializer = PostSerializer(Post.objects.get(id=self.publicPost["id"]))
        postData = serializer.data
        publicComment = {"comment": "hello world", "contentType": "text/plain", "post": postData}
        response = client.post('/api/posts/' + str(self.publicPost["id"]) + "/comments/", publicComment , format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        publicComment = response.data

        response = client.delete('/api/posts/' + str(self.publicPost["id"]) + "/comments/" + str(publicComment["id"]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_not_author(self):
        client = APIClient()

       # public comment by author1
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding1)
        serializer = PostSerializer(Post.objects.get(id=self.publicPost["id"]))
        postData = serializer.data
        publicComment = {"comment": "hello world", "contentType": "text/plain", "post": postData}
        response = client.post('/api/posts/' + str(self.publicPost["id"]) + "/comments/", publicComment , format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        publicComment = response.data

        # author2 try to delete
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding2)
        response = client.delete('/api/posts/' + str(self.publicPost["id"]) + "/comments/" + str(publicComment["id"]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_non_existing(self):
        client = APIClient()

       # public comment by author1
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding1)
        serializer = PostSerializer(Post.objects.get(id=self.publicPost["id"]))
        postData = serializer.data
        publicComment = {"comment": "hello world", "contentType": "text/plain", "post": postData}
        response = client.post('/api/posts/' + str(self.publicPost["id"]) + "/comments/", publicComment , format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        publicComment = response.data

        # author2 try to delete
        # non-existing post
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding1)
        nonexistingPostId = uuid.uuid4()
        response = client.delete('/api/posts/' + str(nonexistingPostId) + "/comments/" + str(self.publicComment["id"]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # non-existing comment
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding1)
        nonexistingCommentId = uuid.uuid4()
        response = client.delete('/api/posts/' +  str(self.publicPost["id"]) + "/comments/" + str(nonexistingCommentId))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_comment_success(self):
        client = APIClient()


        # public comment by author1
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding1)
        serializer = PostSerializer(Post.objects.get(id=self.publicPost["id"]))
        postData = serializer.data
        publicComment = {"comment": "hello world", "contentType": "text/plain", "post": postData}
        response = client.post('/api/posts/' + str(self.publicPost["id"]) + "/comments/", publicComment , format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        publicComment = response.data

        editedComment = copy.deepcopy(publicComment)
        editedComment["comment"] = "EDITED COMMENT"
        response = client.put('/api/posts/' + str(self.publicPost["id"]) + "/comments/" + str(publicComment["id"]), editedComment, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ignore dates difference due to after put update
        response.data["published"] = ""
        editedComment["published"] = ""
        self.assertEqual(response.data, editedComment)

    def test_put_not_author(self):
        client = APIClient()

       # public comment by author1
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding1)
        serializer = PostSerializer(Post.objects.get(id=self.publicPost["id"]))
        postData = serializer.data
        publicComment = {"comment": "hello world", "contentType": "text/plain", "post": postData}
        response = client.post('/api/posts/' + str(self.publicPost["id"]) + "/comments/", publicComment , format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        publicComment = response.data

        # author2 try to edit
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding2)
        editedComment = copy.deepcopy(publicComment)
        editedComment["comment"] = "EDITED COMMENT"
        response = client.put('/api/posts/' + str(self.publicPost["id"]) + "/comments/" + str(publicComment["id"]), editedComment, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_non_existing(self):
        client = APIClient()

       # public comment by author1
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding1)
        serializer = PostSerializer(Post.objects.get(id=self.publicPost["id"]))
        postData = serializer.data
        publicComment = {"comment": "hello world", "contentType": "text/plain", "post": postData}
        response = client.post('/api/posts/' + str(self.publicPost["id"]) + "/comments/", publicComment , format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        publicComment = response.data


        editedComment = copy.deepcopy(publicComment)
        editedComment["comment"] = "EDITED COMMENT"

        # author2 try to update
        # non-existing post
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding1)
        nonexistingPostId = uuid.uuid4()
        response = client.put('/api/posts/' + str(nonexistingPostId) +"/comments/" + str(publicComment["id"]), editedComment, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # # non-existing comment
        client.credentials(HTTP_AUTHORIZATION='Basic ' + self.basicAuthEncoding1)
        nonexistingCommentId = uuid.uuid4()
        response = client.put('/api/posts/' +  str(self.publicPost["id"]) + "/comments/" + str(nonexistingCommentId), editedComment, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

# testing creating and getting posts
class ApiPostModelTestCase(TestCase):
    # Model tests - Set up authors and the created post
    def setUp(self):
        user = User.objects.create(username="bob")
        user1 = User.objects.create(username="sam")
        author = Author.objects.create(user=user1, github="sammy")
        author1 = Author.objects.create(user=user, github="bobby")
        post = Post.objects.create(id=post_id, title="Title", contentType="text/plain",
                          content="this is my post data", author=author, published=date,
                            visibility="PUBLIC", image="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTu-eC39iANJccZL5c6oKKFdRyRldGt5UT1gCTpXbRkOSb2IFAv")

        Comment.objects.create(id=c_id, post=post, author=author1, contentType="text/plain",
                          comment="this is my comment", published=date)

    #check that two authors can friend each other
    def test_friending(self):
        user = User.objects.create(username="cam")
        user1 = User.objects.create(username="mitchel")
        author1 = Author.objects.create(user=user1, github="mitchel")
        author = Author.objects.create(user=user, github="cam")
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
        self.assertEqual(post.image,"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTu-eC39iANJccZL5c6oKKFdRyRldGt5UT1gCTpXbRkOSb2IFAv")
        response = requests.get(post.image)
        self.assertEqual(response.status_code,200)

        #test that we can get an author back
        user = User.objects.get(username="sam")
        author = Author.objects.get(user=user)
        self.assertEqual(author.user.username, "sam")
        self.assertEqual(author.github, "sammy")

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