from django.contrib import admin
from .models import Author, AuthorProfile, Publisher, Category, Book, Publication


class AuthorProfileInline(admin.TabularInline):
    """Inline para editar el perfil del autor junto con su registro principal."""
    model = AuthorProfile
    can_delete = False
    verbose_name = 'Profile'
    verbose_name_plural = 'Profile Data'


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'nationality', 'date_of_birth')
    search_fields = ('first_name', 'last_name', 'nationality')
    list_filter = ('nationality',)
    inlines = [AuthorProfileInline]


@admin.register(AuthorProfile)
class AuthorProfileAdmin(admin.ModelAdmin):
    list_display = ('author', 'email', 'website')
    search_fields = ('author__first_name', 'author__last_name', 'email')


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'website')
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    prepopulated_fields = {'name': ('name',)}


class PublicationInline(admin.TabularInline):
    model = Publication
    extra = 0
    verbose_name = 'Publication'
    verbose_name_plural = 'Publications'


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'isbn', 'author', 'publication_year', 'pages')
    search_fields = ('title', 'isbn')
    list_filter = ('publication_year', 'categories')
    filter_horizontal = ('categories',)
    inlines = [PublicationInline]


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ('book', 'publisher', 'publication_date', 'edition_number')
    list_filter = ('publication_date', 'edition_number')
    search_fields = ('book__title', 'publisher__name')
