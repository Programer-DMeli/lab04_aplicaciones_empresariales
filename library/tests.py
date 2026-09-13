from django.test import TestCase
from datetime import date
from library.models import Author, AuthorProfile, Publisher, Category, Book, Publication


class ForeignKeyQueryTest(TestCase):
    """Tests para relación ForeignKey (Book -> Author)."""

    def setUp(self):
        self.author = Author.objects.create(
            first_name="Jorge",
            last_name="L Borges",
            nationality="Argentine"
        )
        self.book = Book.objects.create(
            title="Ficciones",
            isbn="9780000000001",
            publication_year=1944,
            pages=200,
            author=self.author
        )

    def test_book_author(self):
        """Query: obtener autor de un libro (ForeignKey)."""
        self.assertEqual(self.book.author.first_name, "Jorge")
        self.assertEqual(self.book.author.nationality, "Argentine")

    def test_author_books(self):
        """Query: obtener todos los libros de un autor (related_name='books')."""
        self.assertEqual(self.author.books.count(), 1)
        self.assertEqual(self.author.books.first().title, "Ficciones")

    def test_author_books_with_second_book(self):
        """Query: múltiples libros de un autor."""
        book2 = Book.objects.create(
            title="El Aleph",
            isbn="9780000000002",
            publication_year=1949,
            pages=180,
            author=self.author
        )
        self.assertEqual(self.author.books.count(), 2)


class OneToOneQueryTest(TestCase):
    """Tests para relación OneToOne (Author -> AuthorProfile)."""

    def setUp(self):
        self.author = Author.objects.create(
            first_name="Gabriel",
            last_name="García Márquez",
            nationality="Colombian",
            date_of_birth=date(1927, 3, 6)
        )
        self.profile = AuthorProfile.objects.create(
            author=self.author,
            biography="Escritor colombiano, Nobel de Literatura 1982.",
            email="gabriel@example.com",
            website="https://example.com"
        )

    def test_author_has_profile(self):
        """Query: obtener perfil del autor (OneToOne reverse)."""
        self.assertEqual(self.author.profile.biography, "Escritor colombiano, Nobel de Literatura 1982.")

    def test_profile_author(self):
        """Query: obtener autor desde perfil (OneToOne forward)."""
        self.assertEqual(self.profile.author.first_name, "Gabriel")

    def test_author_without_profile(self):
        """Query: autor sin perfil no tiene profile attribute (raises AttributeError)."""
        author_no_profile = Author.objects.create(
            first_name="Julio",
            last_name="Cortázar",
            nationality="Argentine"
        )
        with self.assertRaises(AttributeError):
            _ = author_no_profile.profile


class ManyToManyQueryTest(TestCase):
    """Tests para relación ManyToMany (Book -> Category)."""

    def setUp(self):
        self.fantasy = Category.objects.create(
            name="Fantasy",
            description="Fantasy genre"
        )
        self.adventure = Category.objects.create(
            name="Adventure",
            description="Adventure stories"
        )
        self.book = Book.objects.create(
            title="The Hobbit",
            isbn="9780000000010",
            publication_year=1937,
            pages=310,
            author=Author.objects.create(
                first_name="J.R.R.",
                last_name="Tolkien",
                nationality="British"
            )
        )
        self.book.categories.add(self.fantasy, self.adventure)

    def test_book_categories(self):
        """Query: obtener categorías de un libro."""
        self.assertEqual(self.book.categories.count(), 2)
        self.assertTrue(self.book.categories.filter(name="Fantasy").exists())

    def test_category_books(self):
        """Query: obtener libros de una categoría (related_name='books')."""
        self.assertEqual(self.fantasy.books.count(), 1)
        self.assertEqual(self.fantasy.books.first().title, "The Hobbit")

    def test_add_remove_category(self):
        """Query: agregar y quitar categorías."""
        self.classic = Category.objects.create(name="Classic")
        self.book.categories.add(self.classic)
        self.assertEqual(self.book.categories.count(), 3)
        self.book.categories.remove(self.classic)
        self.assertEqual(self.book.categories.count(), 2)


class ThroughModelQueryTest(TestCase):
    """Tests para relación ManyToMany with through model (Book <-> Publisher via Publication)."""

    def setUp(self):
        self.book = Book.objects.create(
            title="Don Quijote",
            isbn="9780000000020",
            publication_year=1605,
            pages=863,
            author=Author.objects.create(
                first_name="Miguel de Cervantes",
                last_name="Saavedra"
            )
        )
        self.publisher1 = Publisher.objects.create(
            name="Ediciones Clásicas",
            website="https://ejemplo.com",
            address="Madrid, España"
        )
        self.publisher2 = Publisher.objects.create(
            name="Penguin Clásicos",
            website="https://penguin.com",
            address="London, UK"
        )
        self.pub1 = Publication.objects.create(
            book=self.book,
            publisher=self.publisher1,
            publication_date=date(1990, 5, 15),
            edition_number=1
        )
        self.pub2 = Publication.objects.create(
            book=self.book,
            publisher=self.publisher2,
            publication_date=date(2000, 3, 20),
            edition_number=2
        )

    def test_book_publishers_through_publications(self):
        """Query: obtener editoriales de un libro a través de Publication."""
        self.assertEqual(self.book.publications.count(), 2)
        publishers = [pub.publisher.name for pub in self.book.publications.all()]
        self.assertIn("Ediciones Clásicas", publishers)
        self.assertIn("Penguin Clásicos", publishers)

    def test_publisher_books(self):
        """Query: obtener libros de una editorial."""
        self.assertEqual(self.publisher1.books.count(), 1)
        self.assertEqual(self.publisher1.books.first().title, "Don Quijote")

    def test_publication_details(self):
        """Query: obtener detalles de la publicación (fecha, edición)."""
        self.assertEqual(self.pub1.publication_date, date(1990, 5, 15))
        self.assertEqual(self.pub1.edition_number, 1)

    def test_edition_number(self):
        """Query: acceder al número de edición."""
        for pub in self.book.publications.all():
            if pub.publisher.name == "Ediciones Clásicas":
                self.assertEqual(pub.edition_number, 1)
            elif pub.publisher.name == "Penguin Clásicos":
                self.assertEqual(pub.edition_number, 2)


class BidirectionalQueryTest(TestCase):
    """Tests para queries bidireccionales (acceso en ambos sentidos de las relaciones)."""

    def setUp(self):
        self.author = Author.objects.create(
            first_name="Jorge Luis",
            last_name="Borges",
            nationality="Argentine",
            date_of_birth=date(1899, 8, 24)
        )
        self.profile = AuthorProfile.objects.create(
            author=self.author,
            biography="Escritor argentino, maestro del cuento fantástico.",
            email="borges@example.com"
        )
        self.fantasy = Category.objects.create(name="Fantasy")
        self.classic = Category.objects.create(name="Classic")
        self.book1 = Book.objects.create(
            title="Ficciones",
            isbn="9780000000001",
            publication_year=1944,
            pages=200,
            author=self.author
        )
        self.book1.categories.add(self.fantasy, self.classic)
        self.publisher = Publisher.objects.create(
            name="Editorial Sudamericana",
            website="https://sudamericana.com",
            address="Buenos Aires, Argentina"
        )
        self.pub_record = Publication.objects.create(
            book=self.book1,
            publisher=self.publisher,
            publication_date=date(1944, 10, 15),
            edition_number=1
        )

    def test_full_bidirectional_flow(self):
        """Query completa bidireccional: Editorial -> Libro -> Autor -> Perfil."""
        publisher = Publisher.objects.get(name="Editorial Sudamericana")
        for publication in publisher.books.all():
            author = publication.author
            if author.profile:
                self.assertEqual(author.profile.biography, "Escritor argentino, maestro del cuento fantástico.")

    def test_author_to_books_to_categories(self):
        """Query: Autor -> Libros -> Categorías."""
        author = Author.objects.get(first_name="Jorge Luis")
        for book in author.books.all():
            for cat in book.categories.all():
                self.assertTrue(cat.name in ["Fantasy", "Classic"])

    def test_reverse_profile_to_author(self):
        """Query: Perfil -> Autor -> Libros."""
        profile = AuthorProfile.objects.get(author=self.author)
        for book in profile.author.books.all():
            self.assertEqual(book.title, "Ficciones")


class OnDeleteBehaviorTest(TestCase):
    """Tests para verificar el comportamiento de on_delete=CASCADE."""

    def test_author_delete_cascades_books(self):
        """Si se elimina un autor, se eliminan sus libros (CASCADE)."""
        author = Author.objects.create(
            first_name="Test",
            last_name="Author"
        )
        book = Book.objects.create(
            title="Test Book",
            isbn="9780000000099",
            publication_year=2000,
            pages=100,
            author=author
        )
        author_id = author.id
        book_id = book.id
        author.delete()
        with self.assertRaises(Author.DoesNotExist):
            Author.objects.get(id=author_id)
        with self.assertRaises(Book.DoesNotExist):
            Book.objects.get(id=book_id)

    def test_author_profile_cascade(self):
        """Si se elimina un autor, se elimina su perfil (CASCADE)."""
        author = Author.objects.create(
            first_name="Test",
            last_name="Profile"
        )
        profile = AuthorProfile.objects.create(
            author=author,
            biography="Test biography"
        )
        profile_author_id = profile.author_id
        author_id = author.id
        author.delete()
        with self.assertRaises(Author.DoesNotExist):
            Author.objects.get(id=author_id)
        with self.assertRaises(AuthorProfile.DoesNotExist):
            AuthorProfile.objects.get(author_id=profile_author_id)

    def test_book_delete_cascades_publication(self):
        """Si se elimina un libro, se eliminan sus publicaciones (CASCADE)."""
        author = Author.objects.create(first_name="Test", last_name="Author")
        book = Book.objects.create(
            title="Test Book",
            isbn="9780000000088",
            publication_year=2000,
            pages=100,
            author=author
        )
        publisher = Publisher.objects.create(name="Test Publisher")
        pub = Publication.objects.create(
            book=book,
            publisher=publisher,
            edition_number=1
        )
        book_id = book.id
        pub_id = pub.id
        book.delete()
        with self.assertRaises(Book.DoesNotExist):
            Book.objects.get(id=book_id)
        with self.assertRaises(Publication.DoesNotExist):
            Publication.objects.get(id=pub_id)


class StringRepresentationTest(TestCase):
    """Tests para los métodos __str__ de los modelos."""

    def setUp(self):
        self.author = Author.objects.create(
            first_name="Gabriel",
            last_name="García Márquez",
            nationality="Colombian"
        )
        self.profile = AuthorProfile.objects.create(
            author=self.author,
            biography="Test"
        )
        self.publisher = Publisher.objects.create(name="Penguin")
        self.category = Category.objects.create(name="Fantasy")
        self.book = Book.objects.create(
            title="Cien Años de Soledad",
            isbn="9780000000001",
            publication_year=1967,
            pages=417,
            author=self.author
        )
        self.pub_record = Publication.objects.create(
            book=self.book,
            publisher=self.publisher,
            publication_date=date(1990, 1, 1),
            edition_number=1
        )

    def test_author_str(self):
        self.assertEqual(str(self.author), "Gabriel García Márquez")

    def test_profile_str(self):
        self.assertEqual(str(self.profile), "Profile of Gabriel García Márquez")

    def test_publisher_str(self):
        self.assertEqual(str(self.publisher), "Penguin")

    def test_category_str(self):
        self.assertEqual(str(self.category), "Fantasy")

    def test_book_str(self):
        self.assertEqual(str(self.book), "Cien Años de Soledad")

    def test_publication_str(self):
        expected = "Cien Años de Soledad - Penguin (Ed. 1)"
        self.assertEqual(str(self.pub_record), expected)
