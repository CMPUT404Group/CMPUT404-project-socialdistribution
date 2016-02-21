from django.contrib import admin
from .models import Post
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from post.models import Author

# Register your models here.
class AuthorInline(admin.StackedInline):
    model = Author
    can_delete = True
    verbose_name_plural = "authors"

class UserAdmin(BaseUserAdmin):
    inlines = (AuthorInline, )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Post)
