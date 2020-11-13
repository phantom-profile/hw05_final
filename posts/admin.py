from django.contrib import admin
from .models import Post, Group, Comment, Follow


class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author",)
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class GroupAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "description",)
    search_fields = ("title", "description",)
    list_filter = ("title",)


class CommentAdmin(admin.ModelAdmin):
    list_display = ("pk", "author", "post", "text",)
    search_fields = ("author", "post",)
    list_filter = ("created", "author",)


class FollowAdmin(admin.ModelAdmin):
    list_display = ("user", "author",)
    search_fields = ("user", "author",)
    list_filter = ("user", "author",)


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
