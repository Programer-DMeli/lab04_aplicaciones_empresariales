"""
Ejemplos de consultas Django ORM para el proyecto Library Management System.

Este archivo demuestra el uso de:
- ForeignKey queries (Book -> Author)
- OneToOne queries (Author <-> AuthorProfile)
- ManyToMany queries (Book <-> Category)
- Through model queries (Book <-> Publisher via Publication)
- Queries bidireccionales
"""

from library.models import Author, AuthorProfile, Publisher, Category, Book, Publication


def demo_queries():
    """Ejemplos de todas las consultas ORM."""

    # ========================
    # 1. CREACIÓN DE DATOS
    # ========================
    print("\n=== CREACIÓN DE DATOS ===")

    # Crear autor
    author = Author.objects.create(
        first_name="Gabriel",
        last_name="García Márquez",
        nationality="Colombian",
    )
    print(f"Autor creado: {author}")

    # Crear perfil del autor (OneToOne)
    profile = AuthorProfile.objects.create(
        author=author,
        biography="Escritor colombiano, Nobel de Literatura 1982.",
        email="gabriel@example.com",
    )
    print(f"Perfil creado: {profile}")

    # Crear editorial (Publisher)
    publisher = Publisher.objects.create(
        name="Editorial Sudamericana",
        website="https://sudamericana.com",
        address="Buenos Aires, Argentina",
    )
    print(f"Editorial creada: {publisher}")

    # Crear categorías (Category)
    fantasy = Category.objects.create(name="Fantasy")
    magical_realism = Category.objects.create(name="Magical Realism")
    print(f"Categorías creadas: {fantasy.name}, {magical_realism.name}")

    # Crear libro (ForeignKey -> Author)
    book = Book.objects.create(
        title="Cien Años de Soledad",
        isbn="9780000000001",
        publication_year=1967,
        pages=417,
        author=author,
    )
    print(f"Libro creado: {book}")

    # Asociar categorías (ManyToMany)
    book.categories.add(fantasy, magical_realism)
    print(f"Categorías de '{book.title}': {[c.name for c in book.categories.all()]}")

    # Asociar editorial (ManyToMany via Publication - through model)
    publication = Publication.objects.create(
        book=book,
        publisher=publisher,
        publication_date="2005-03-15",
        edition_number=5,
    )
    print(f"Publicación creada: {publication}")

    # ========================
    # 2. QUERIES - ForeignKey (Book -> Author)
    # ========================
    print("\n=== FOREIGN KEY QUERIES ===")

    # Query: Obtener el autor de un libro (acceso directo por el campo author)
    print(f"Autor del libro: {book.author.first_name} {book.author.last_name}")
    print(f"Nacionalidad: {book.author.nationality}")

    # Query: Obtener todos los libros de un autor (usando related_name='books')
    print(f"Libros de {author.first_name}:")
    for b in author.books.all():
        print(f"  - {b.title} ({b.publication_year})")

    # ========================
    # 3. QUERIES - OneToOne (Author <-> AuthorProfile)
    # ========================
    print("\n=== ONE-TO-ONE QUERIES ===")

    # Query: Desde Autor hacia Perfil (acceso reverse por related_name='profile')
    print(f"Biografía: {author.profile.biography}")
    print(f"Email: {author.profile.email}")

    # Query: Desde Perfil hacia Autor (acceso forward por author)
    print(f"Autor del perfil: {profile.author.first_name}")

    # ========================
    # 4. QUERIES - ManyToMany (Book <-> Category)
    # ========================
    print("\n=== MANY-TO-MANY QUERIES (Categories) ===")

    # Query: Obtener categorías de un libro
    print(f"Categorías de '{book.title}':")
    for cat in book.categories.all():
        print(f"  - {cat.name}: {cat.description}")

    # Query: Obtener libros de una categoría (usando related_name='books')
    print(f"Libros de 'Magical Realism': {[b.title for b in magical_realism.books.all()]}")

    # ========================
    # 5. QUERIES - Through Model (Book <-> Publisher via Publication)
    # ========================
    print("\n=== MANY-TO-MANY QUERIES (Publishers via Publication) ===")

    # Query: Obtener todas las publicaciones/editoriales de un libro
    print(f"Publicaciones de '{book.title}':")
    for pub in book.publications.all():
        print(f"  - Editorial: {pub.publisher.name}")
        print(f"    Fecha: {pub.publication_date}")
        print(f"    Edición: {pub.edition_number}")

    # Query: Obtener todos los libros de una editorial
    print(f"Libros de {publisher.name}:")
    for b in publisher.books.all():
        print(f"  - {b.title}")

    # ========================
    # 6. QUERIES BIDIRECCIONALES
    # ========================
    print("\n=== QUERIES BIDIRECCIONALES ===")

    # Query completa: Editorial -> Libro -> Autor -> Perfil -> Email
    print("Flujo: Editorial -> Libro -> Autor -> Perfil -> Email")
    for pub_record in publisher.books.all():
        author_obj = pub_record.author
        if hasattr(author_obj, 'profile') and author_obj.profile:
            print(f"  {publisher.name} -> {pub_record.title} -> {author_obj.first_name} -> {author_obj.profile.email}")

    # ========================
    # 7. QUERIES AVANZADAS
    # ========================
    print("\n=== QUERIES AVANZADAS ===")

    # Ejemplo: Filtrar libros por año de publicación
    print(f"Libros publicados después de 1950:")
    for b in Book.objects.filter(publication_year__gt=1950):
        print(f"  - {b.title} ({b.publication_year})")

    # Ejemplo: Contar libros por categoría
    print(f"Conteo de libros por categoría:")
    for cat in Category.objects.all():
        print(f"  {cat.name}: {cat.books.count()} libros")

    # Ejemplo: Contar libros por editorial
    print(f"Conteo de libros por editorial:")
    for p in Publisher.objects.all():
        print(f"  {p.name}: {p.books.count()} libros")

    # Ejemplo: Filtros combinados
    print(f"Libros de categoría 'Fantasy' y año > 1900:")
    for b in Book.objects.filter(categories__name="Fantasy", publication_year__gt=1900).distinct():
        print(f"  - {b.title}")


if __name__ == "__main__":
    import django
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

    demo_queries()
