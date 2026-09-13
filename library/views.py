from django.shortcuts import render
from django.views.generic import DetailView, ListView
from .models import Book


class BookListView(ListView):
    """Lista todos los libros disponibles."""
    model = Book
    template_name = 'library/book_list.html'
    context_object_name = 'books'
    paginate_by = 10


class BookDetailView(DetailView):
    """Vista de detalle de un libro con categorías, editorial (vía Publication)
    y datos completos del autor (incluyendo AuthorProfile)."""
    model = Book
    template_name = 'library/book_detail.html'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.get_object()

        # Categorías del libro
        context['categories'] = book.categories.all()

        # Publicaciones (relación explícita a través de Publication)
        context['publications'] = book.publications.all()

        # Editoriales a través de publicaciones
        context['publishers'] = [pub.publisher for pub in book.publications.all()]

        # Perfil del autor (OneToOne)
        if hasattr(book.author, 'profile'):
            context['author_profile'] = book.author.profile
        else:
            context['author_profile'] = None

        return context
