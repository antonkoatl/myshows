from django.contrib import admin

from .models import Show, Poster, Genre, Tag, Article, ArticleImage, Country, Network, Season, Episode, EpisodeImage, \
    EpisodeComment, PersonRole, Person, PersonSpouse

admin.site.register(Poster)
admin.site.register(EpisodeImage)
admin.site.register(ArticleImage)
admin.site.register(Network)


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ('title_ru', 'id',)
    filter_horizontal = ('country', 'genres', 'tags')


@admin.register(Genre, Tag, Article)
class SimpleAdmin(admin.ModelAdmin):
    list_display = ['title', 'id']


@admin.register(Country)
class CountriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_ru', 'name_short')


@admin.register(Season)
class SeasonsAdmin(admin.ModelAdmin):
    list_display = ('show', 'number', 'id')


@admin.register(Episode)
class EpisodesAdmin(admin.ModelAdmin):
    list_display = ('get_show', 'get_season_number', 'number', 'title', 'id')

    def get_show(self, obj):
        return obj.season.show.title_ru

    get_show.short_description = 'Show'

    def get_season_number(self, obj):
        return obj.season.number

    get_season_number.short_description = 'Season'


@admin.register(EpisodeComment)
class EpisodeCommentsAdmin(admin.ModelAdmin):
    raw_id_fields = ['episode']


@admin.register(Person)
class PersonsAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_ru', 'id',)
    search_fields = ['name', 'name_ru']


@admin.register(PersonRole)
class GenresAdmin(admin.ModelAdmin):
    list_display = ('person', 'role', 'show', 'id',)


@admin.register(PersonSpouse)
class PersonSpousesAdmin(admin.ModelAdmin):
    list_display = ('person1', 'person2', 'id',)
    autocomplete_fields = ['person1', 'person2']
