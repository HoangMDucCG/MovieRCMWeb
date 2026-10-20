from django.contrib import admin
from .models import Genre, Movie, TheaterLink


class TheaterLinkInline(admin.TabularInline):
    model = TheaterLink
    extra = 1


class MovieAdmin(admin.ModelAdmin):
    inlines = [TheaterLinkInline]

    list_display = ("title", "type", "release_date", "rating")
    list_filter = ("type", "genres")
    search_fields = ("title",)


# 3. Đăng ký các Model
admin.site.register(Genre)
admin.site.register(Movie, MovieAdmin)
