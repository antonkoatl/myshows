from django.contrib import admin

from .models import Show, Poster, Genre, Tag

admin.site.register(Show)
admin.site.register(Poster)


class GenresAdmin(admin.ModelAdmin):
    list_display = ('id', 'title',)


admin.site.register(Genre, GenresAdmin)

class TagsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title',)

admin.site.register(Tag, TagsAdmin)
