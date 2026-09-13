# Documentación del sistema Biblioteca - Lab04

## 1. Estructura del proyecto

```text
Lab04/
├── config/                         # Configuración de Django
│   ├── settings.py                 # Configuración principal
│   ├── urls.py                     # URLs raíz
│   └── wsgi.py / asgi.py
├── library/                        # App principal
│   ├── models.py                   # Definición de modelos
│   ├── views.py                    # Vistas (CBV)
│   ├── urls.py                     # URLs de la app
│   ├── admin.py                    # Administración Django
│   ├── queries.py                  # Ejemplos de consultas ORM
│   ├── tests.py                    # Tests unitarios
│   └── templates/library/
│       ├── base.html               # Plantilla base con estilos
│       ├── book_list.html          # Vista lista de libros
│       └── book_detail.html        # Vista detalle de libro
├── db.sqlite3                      # Base de datos
├── manage.py                       # Script de gestión Django
└── README.md                       # Esta documentación
```

## 2. Modelos y relaciones

```text
+------------------+       +-------------------+
|     Author       |1----*|      Book         |
|------------------|       |-------------------|
| id (PK)          |       | id (PK)           |
| first_name       |       | title             |
| last_name        |       | isbn              |
| nationality      |       | publication_year  |
| date_of_birth    |       | pages             |
| created_at       |       | author (FK -> Author) |
+------------------+       +-------------------+
        |1                            |
        |                            |
     [1]                           *|
        |                            |
        v                            v
+------------------+       +-------------------+       +-------------------+
|  AuthorProfile   |       |    Publication    |       |    Category       |
|------------------|       |-------------------|       |-------------------|
| author (PK, FK)  |1-----*| id (PK)           |*-----*| id (PK)           |
| biography        |       | book (FK -> Book) |       | name              |
| email            |       | publisher (FK ->  |       | description       |
| website          |       |   Publisher)      |       | created_at        |
| photo            |       | publication_date  |       +-------------------+
| created_at       |       | edition_number    |              |
+------------------+       +-------------------+              |
        *                                                      |
        |                                                      |
        +------------------------------------------------------+
   ```

   ## 3. Tipos de relaciones

A) ForeignKey (N:1) - Book -> Author
-------------------------------------
   Modelo: Book.author = models.ForeignKey(Author, on_delete=models.CASCADE)
   Significado: Cada libro pertenece a un solo autor.
   Direccionalidad:
     - Book -> Author: book.author.first_name
     - Author -> Book: author.books.all() (related_name='books')

B) OneToOne (1:1) - Author <-> AuthorProfile
----------------------------------------------
   Modelo: AuthorProfile.author = models.OneToOneField(Author, on_delete=models.CASCADE)
   Significado: Cada autor tiene un solo perfil y viceversa.
   Direccionalidad:
     - Author -> Profile: author.profile.biography
     - Profile -> Author: profile.author.first_name

C) ManyToMany con Through Model (N:M) - Book <-> Publisher
------------------------------------------------------------
   Modelo: Book.publishers = models.ManyToManyField(Publisher, through='Publication')
   Through: Publication(book, publisher, publication_date, edition_number)
   Significado: Un libro puede tener múltiples editoriales y viceversa.
                La tabla Publication almacena metadatos adicionales.
   Direccionalidad:
     - Book -> Publishers: book.publications.all()  (NOT book.publishers)
     - Publisher -> Books: publisher.books.all()
   ACCESO A METADATOS:
     - pub.book, pub.publisher, pub.publication_date, pub.edition_number

D) ManyToMany sin Through Model (N:M) - Book <-> Category
-----------------------------------------------------------
   Modelo: Book.categories = models.ManyToManyField(Category)
   Significado: Un libro puede tener múltiples categorías y viceversa.
   Direccionalidad:
     - Book -> Categories: book.categories.all()
     - Category -> Books: category.books.all() (related_name='books')


## 4. Comportamiento `on_delete=CASCADE`
Cuando se elimina un padre, se eliminan los hijos automáticamente:
   - Eliminar Author -> Se eliminan sus Books y su AuthorProfile
   - Eliminar Book -> Se eliminan sus Publications
   - Eliminar Publisher -> Se eliminan sus Publications


## 5. Vistas

A) BookListView (Class-Based View - ListView)
----------------------------------------------
   URL: /
   Template: library/book_list.html
   Context:
     - book_list: QuerySet de todos los libros (ordenados por título)
     - title: "Catálogo de Libros"

B) BookDetailView (Class-Based View - DetailView)
--------------------------------------------------
   URL: /book/<int:pk>/
   Template: library/book_detail.html
   Context:
     - book: El libro seleccionado
     - title: Título del libro


## 6. URLs

/                    -> BookListView    (lista de libros)
/book/<int:pk>/      -> BookDetailView  (detalle de un libro)
admin/               -> Django Admin    (admin interface)


## 7. Superusuario
   Usuario: admin
   Contraseña: admin123
   URL: /admin/


## 8. Datos de ejemplo
   Autores: J.R.R. Tolkien, Gabriel García Márquez, Julio Cortázar
   Editoriales: Penguin Random House, Editorial Sudamericana, HarperCollins
   Categorías: Fantasy, Magical Realism, Science Fiction, Classic Literature
   Libros: The Hobbit, Cien Años de Soledad, Rayuela


## 9. Queries ORM de ejemplo

- **ForeignKey** - Libro -> Autor
```python
book = Book.objects.first()
author = book.author
```

- **ForeignKey** - Autor -> Libros
```python
author = Author.objects.first()
books = author.books.all()
```

- **OneToOne** - Autor -> Perfil
```python
profile = author.profile
```

- **ManyToMany - Libro -> Categorías**
```python
categories = book.categories.all()
```

- **ManyToMany con Through** - Libro -> Publicaciones
```python
publications = book.publications.all()
for pub in publications:
    print(pub.publisher.name, pub.publication_date, pub.edition_number)
```

- **ManyToMany con Through** - Editorial -> Libros
```python
publisher = Publisher.objects.first()
books = publisher.books.all()
```

- **Queries avanzadas**
```python
Book.objects.filter(publication_year__gt=1950)
Book.objects.filter(categories__name="Fantasy").distinct()
```












