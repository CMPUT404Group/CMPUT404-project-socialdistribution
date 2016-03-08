from django.contrib import admin
from .models import Author, Post, Upload, Comment, Node, Friending, Following
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group

# Register your models here.
class AuthorInline(admin.StackedInline):
    model = Author
    can_delete = True
    verbose_name_plural = "authors"

class UserAdmin(BaseUserAdmin):
    inlines = (AuthorInline, )


#admin.site.register(User, UserAdmin)
# admin.site.register(Author)
# admin.site.register(Post)
# admin.site.register(Upload)
# admin.site.register(Comment)
# admin.site.register(Node)
# admin.site.register(Friending)
# admin.site.register(Following)