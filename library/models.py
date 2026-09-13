from django.db import models


class Author(models.Model):
    """Autor de libros - relación 1:N con Book (ForeignKey) y 1:1 con AuthorProfile."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class AuthorProfile(models.Model):
    """Perfil detallado de un autor - relación OneToOne con Author.
    
    Separación de biografía y datos adicionales del registro principal.
    Justificación: evita sobrecargar el modelo Author con campos extensos,
    aplica el principio de responsabilidad única y carga bajo demanda.
    """
    author = models.OneToOneField(
        Author,
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=True
    )
    biography = models.TextField(blank=True, default='')
    email = models.EmailField(blank=True, max_length=254)
    website = models.URLField(blank=True, max_length=200)
    photo = models.ImageField(upload_to='author_photos/', blank=True, null=True)

    class Meta:
        verbose_name = 'Author Profile'
        verbose_name_plural = 'Author Profiles'

    def __str__(self):
        return f"Profile of {self.author}"


class Publisher(models.Model):
    """Editorial de libros."""
    name = models.CharField(max_length=200)
    website = models.URLField(blank=True, max_length=200)
    address = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = 'Publisher'
        verbose_name_plural = 'Publishers'
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    """Categoría/Género literario."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    """Libro - modelo central con ForeignKey a Author, ManyToMany a Category,
    y ManyToMany through=Publication a Publisher."""
    title = models.CharField(max_length=300)
    isbn = models.CharField(max_length=13, unique=True, help_text='ISBN-13')
    publication_year = models.IntegerField()
    pages = models.PositiveIntegerField()
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)

    # ForeignKey: Book pertenece a un solo Author
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='books',
        help_text='Author of this book'
    )

    # ManyToMany: un libro puede tener varias categorías
    categories = models.ManyToManyField(
        Category,
        related_name='books',
        blank=True
    )

    # ManyToMany through: la relación Libro-Editorial tiene atributos propios
    publishers = models.ManyToManyField(
        Publisher,
        through='Publication',
        related_name='books',
        blank=True
    )

    class Meta:
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
        ordering = ['title']
        indexes = [
            models.Index(fields=['title'], name='idx_book_title'),
            models.Index(fields=['isbn'], name='idx_book_isbn'),
        ]

    def __str__(self):
        return self.title


class Publication(models.Model):
    """Modelo intermedio explícito para la relación Libro-Publisher.
    
    Almacena datos propios de la relación: fecha de publicación específica
    de esta editorial y número de edición. Justificación: no basta con
    saber qué editorial publicó un libro; también importa cuándo y en qué edición.
    """
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='publications')
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='publications')
    publication_date = models.DateField(null=True, blank=True)
    edition_number = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Publication'
        verbose_name_plural = 'Publications'
        unique_together = ('book', 'publisher')
        ordering = ['-publication_date']

    def __str__(self):
        return f"{self.book.title} - {self.publisher.name} (Ed. {self.edition_number})"
