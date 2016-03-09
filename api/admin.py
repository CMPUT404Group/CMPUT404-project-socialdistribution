from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import Post, Comment, Upload, Author

# Register your models here.
# admin.site.unregister(User)
admin.site.unregister(Group)

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Upload)
admin.site.register(Author)