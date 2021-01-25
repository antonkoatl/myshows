from django.contrib import admin

from .models import Show, Poster, Genre, Tag, Article, ArticleImage, Country, Network, Season, Episode, EpisodeImage

admin.site.register(Poster)
admin.site.register(EpisodeImage)
admin.site.register(ArticleImage)
admin.site.register(Network)


class ShowAdmin(admin.ModelAdmin):
    list_display = ('title_ru', 'id',)
    filter_horizontal = ('country', 'genres', 'tags')


admin.site.register(Show, ShowAdmin)


class GenresAdmin(admin.ModelAdmin):
    list_display = ('title', 'id',)


admin.site.register(Genre, GenresAdmin)


class TagsAdmin(admin.ModelAdmin):
    list_display = ('title', 'id',)


admin.site.register(Tag, TagsAdmin)


class ArticlesAdmin(admin.ModelAdmin):
    list_display = ('id', 'title',)


admin.site.register(Article, ArticlesAdmin)


class CountriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_ru', 'name_short')


admin.site.register(Country, CountriesAdmin)


class SeasonsAdmin(admin.ModelAdmin):
    list_display = ('show', 'number', 'id')


admin.site.register(Season, SeasonsAdmin)


class EpisodesAdmin(admin.ModelAdmin):
    list_display = ('get_show', 'get_season_number', 'number', 'title', 'id')

    def get_show(self, obj):
        return obj.season.show.title_ru

    get_show.short_description = 'Show'

    def get_season_number(self, obj):
        return obj.season.number

    get_season_number.short_description = 'Season'


admin.site.register(Episode, EpisodesAdmin)
