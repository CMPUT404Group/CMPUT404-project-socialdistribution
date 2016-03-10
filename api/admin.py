from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import Post, Comment, Upload, Author, Friending, Following

# Register your models here.

class AuthorInline(admin.TabularInline):
    model = Author

class UserAdmin(admin.ModelAdmin):
    inlines = [
        AuthorInline,
    ]
    fields = {'username', 'is_active', 'email'}
    list_display = ('username', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff')

admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
# admin.site.register(Author)
# admin.site.register(Post)
# admin.site.register(Comment)
# admin.site.register(Upload)
# admin.site.register(Friending)
# admin.site.register(Following)

