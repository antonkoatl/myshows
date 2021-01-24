from django.contrib import admin

from .models import Show, Poster, Genre, Tag, Article, ArticleImage

admin.site.register(Show)
admin.site.register(Poster)
admin.site.register(ArticleImage)


class GenresAdmin(admin.ModelAdmin):
    list_display = ('id', 'title',)


admin.site.register(Genre, GenresAdmin)


class TagsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title',)


admin.site.register(Tag, TagsAdmin)


class ArticlesAdmin(admin.ModelAdmin):
    list_display = ('id', 'title',)


admin.site.register(Article, ArticlesAdmin)
