from django.contrib import admin

from .models import Show, Poster, Genre, Tag, Article, ArticleImage, Country

admin.site.register(Poster)
admin.site.register(ArticleImage)


class ShowAdmin(admin.ModelAdmin):
    list_display = ('id', 'title_ru',)
    filter_horizontal = ('country', 'genres', 'tags')


admin.site.register(Show, ShowAdmin)


class GenresAdmin(admin.ModelAdmin):
    list_display = ('id', 'title',)


admin.site.register(Genre, GenresAdmin)


class TagsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title',)


admin.site.register(Tag, TagsAdmin)


class ArticlesAdmin(admin.ModelAdmin):
    list_display = ('id', 'title',)


admin.site.register(Article, ArticlesAdmin)


class CountriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_ru', 'name_short')


admin.site.register(Country, CountriesAdmin)
