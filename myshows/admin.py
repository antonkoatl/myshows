from django.contrib import admin

from .models import Genre, Tag, Country, Network
from .models.article import Article, ArticleImage
from .models.named_entity import Lemma, NamedEntityOccurrence, NamedEntity
from .models.person import Person, PersonSpouse, PersonRole
from .models.episode import Episode, EpisodeImage, EpisodeComment
from .models.season import Season
from .models.show import Show, Poster, Review

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
class PersonRolesAdmin(admin.ModelAdmin):
    list_display = ('person', 'role', 'show', 'id',)
    autocomplete_fields = ['person']


@admin.register(PersonSpouse)
class PersonSpousesAdmin(admin.ModelAdmin):
    list_display = ('person1', 'person2', 'id',)
    autocomplete_fields = ['person1', 'person2']


class NamedEntityLemmaInline(admin.TabularInline):
    model = Lemma


class NamedEntityOccurrenceInline(admin.TabularInline):
    model = NamedEntityOccurrence


@admin.register(NamedEntity)
class NamedEntityAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')
    search_fields = ['name']

    inlines = [
        NamedEntityLemmaInline, NamedEntityOccurrenceInline
    ]


@admin.register(Review)
class PersonSpousesAdmin(admin.ModelAdmin):
    list_display = ('show', 'date', 'title', 'author')
