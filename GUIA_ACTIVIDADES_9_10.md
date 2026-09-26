# Guía - Actividades 9 y 10 (Laboratorio 04)

Todas las consultas fueron ejecutadas y verificadas en `python3 manage.py shell`.
Los resultados mostrados son reales.

---

## ACTIVIDAD 9 — Consultas de ida, de vuelta y filtrado con doble guion bajo

### Cómo entrar a la consola

```bash
cd /home/meli_dev/cuarto_ciclo/Aplicaciones_empresariales/Lab04
python3 manage.py shell
```

Dentro de la consola, escribe siempre esto primero:

```python
>>> from library.models import Author, AuthorProfile, Publisher, Category, Book, Publication
>>> b = Book.objects.get(title='The Lord of the Rings')
```

---

### 9.1 — Consulta de IDA (forward)

Va del hijo al padre. En `Book`, el atributo `author` es la ForeignKey.

```python
>>> b
<Book: The Lord of the Rings>
>>> b.author
<Author: J.R.R. Tolkien>
>>> b.author.first_name
'J.R.R.'
```

**Resultado registrado:** `libro.autor` devuelve una **instancia del modelo `Author`**, no un texto.
Por eso se puede encadenar (`b.author.first_name`). El `str()` del modelo
(`__str__` en `library/models.py:16`) es lo que hace que se vea `J.R.R. Tolkien`.

Dato extra: la FK guarda el id, no el objeto.

```python
>>> b.author_id
1
```

---

### 9.2 — Consulta de VUELTA (reverse)

Va del padre al hijo. Funciona gracias a `related_name='books'`
declarado en `library/models.py:88`.

```python
>>> a = b.author
>>> a
<Author: J.R.R. Tolkien>
>>> a.books.all()
<QuerySet [<Book: The Lord of the Rings>]>
>>> a.books.count()
1
```

**Resultado registrado:** `autor.libros.all()` devuelve un **QuerySet** (puede haber 0, 1 o N
libros), no un objeto único. Siempre es una lista, aunque tenga un solo elemento.

Si no existiera `related_name`, el acceso sería `a.book_set.all()` (nombre automático
`book_set`). El `related_name` es solo un alias más legible.

---

### 9.3 — Filtrado con doble guion bajo `__`

`__` significa "atraviesa esta relación". Se pueden encadenar varios niveles.

**Un nivel (Book → Author):**

```python
>>> Book.objects.filter(author__last_name='Tolkien')
<QuerySet [<Book: The Lord of the Rings>]>
```

```python
>>> Book.objects.filter(author__nationality='British')
<QuerySet [<Book: The Lord of the Rings>]>
```

> Ojo: `nationality` guarda `British`, `Argentine`, `Colombian`, `Estadounidense`
> (no `English`). Un valor inexistente devuelve `<QuerySet []>` silenciosamente,
> no un error. Verifícalo siempre con `print(list(...))`.

**Atravesar ManyToMany (Book → Category):**

```python
>>> Book.objects.filter(categories__name='Fantasy')
<QuerySet [<Book: Rayuela>, <Book: The Lord of the Rings>]>
```

**Atravesar el modelo intermedio (Book → Publication → Publisher):**

```python
>>> Book.objects.filter(publications__publisher__name__icontains='penguin')
<QuerySet [<Book: The Lord of the Rings>]>
```

Aquí hay **dos dobles guiones bajos** porque se cruzan dos relaciones:
`publications` y luego `publisher`.

**Atravesar OneToOne (Book → Author → AuthorProfile):**

```python
>>> Book.objects.filter(author__profile__email__isnull=False)
<QuerySet [<Book: One Hundred Years of Solitude>, <Book: Rayuela>, <Book: The Lord of the Rings>]>
```

**Varios niveles + condición (Book → Author → Book → año):**

```python
>>> Book.objects.filter(author__books__publication_year__gt=1950).distinct()
<QuerySet [<Book: One Hundred Years of Solitude>, <Book: Rayuela>, <Book: The Lord of the Rings>]>
```

**Sobre el `.distinct()`:** al cruzar `author__books__`, un mismo libro puede
aparecer **repetido** (una vez por cada libro de su autor que cumple la condición).
`distinct()` elimina los duplicados del `SELECT`. Sin él, el resultado trae filas
repetidas.

---

### 9.4 — Tabla resumen de resultados

| # | Tipo | Consulta | Resultado |
|---|------|----------|-----------|
| 1 | Ida | `book.author` | `<Author: J.R.R. Tolkien>` |
| 2 | Vuelta | `author.books.all()` | `<QuerySet [<Book: The Lord of the Rings>]>` |
| 3 | Filtro 1 nivel | `filter(author__last_name='Tolkien')` | `<QuerySet [<Book: The Lord of the Rings>]>` |
| 4 | Filtro 1 nivel | `filter(author__nationality='British')` | `<QuerySet [<Book: The Lord of the Rings>]>` |
| 5 | Filtro M2M | `filter(categories__name='Fantasy')` | `<QuerySet [<Book: Rayuela>, <Book: The Lord of the Rings>]>` |
| 6 | Filtro through | `filter(publications__publisher__name__icontains='penguin')` | `<QuerySet [<Book: The Lord of the Rings>]>` |
| 7 | Filtro OneToOne | `filter(author__profile__email__isnull=False)` | 3 libros |
| 8 | Filtro anidado | `filter(author__books__publication_year__gt=1950).distinct()` | 3 libros |

---

## ACTIVIDAD 10 — Borrado de un autor con libros: CASCADE vs PROTECT

> **Importante:** para no romper los datos del laboratorio, se crea un autor
> temporal con libros temporales y se trabaja solo con él.

---

### 10.1 — Escenario CASCADE (`on_delete=models.CASCADE`)

**Paso 1 — Crear el autor temporal con 2 libros, 1 publicación cada uno y un perfil:**

```python
>>> from library.models import *
>>> p = Publisher.objects.first()
>>> c1, c2 = Category.objects.all()[:2]
>>> tmp = Author.objects.create(first_name='Temp', last_name='Borrable', nationality='Test')
>>> l1 = Book.objects.create(title='Temp Book 1', isbn='9780000000001', publication_year=2020, pages=100, author=tmp)
>>> l2 = Book.objects.create(title='Temp Book 2', isbn='9780000000002', publication_year=2021, pages=200, author=tmp)
>>> l1.categories.set([c1])
>>> l2.categories.set([c2])
>>> Publication.objects.create(book=l1, publisher=p, publication_date='2020-01-01', edition_number=1)
>>> Publication.objects.create(book=l2, publisher=p, publication_date='2021-01-01', edition_number=1)
>>> AuthorProfile.objects.create(author=tmp, biography='Temporal', email='tmp@test.com')
```

**Paso 2 — Contar antes:**

```
Authors      = 5
Books        = 5
Publications = 6
Profiles     = 5
tmp.books.all() = [<Book: Temp Book 1>, <Book: Temp Book 2>]
```

**Paso 3 — Borrar (sin try/except, a propósito):**

```python
>>> tmp.delete()
```

**Resultado: NO ocurre nada visible. No hay error.** El comando se ejecuta en silencio.

**Paso 4 — Contar después:**

```
Authors      = 4
Books        = 3     <- Temp Book 1 y Temp Book 2 desaparecieron
Publications = 4     <- las 2 Publication de esos libros tambien
Profiles     = 4     <- el AuthorProfile tambien
Book.objects.filter(title__startswith='Temp') = []
```

**Documentación de qué ocurre con CASCADE:**

1. `tmp.delete()` no lanza ninguna excepción.
2. Django borra en cascada el autor → sus libros → las publicaciones de esos libros.
3. También borra el `AuthorProfile` (su FK es `OneToOneField` con CASCADE).
4. Es una cascada **en profundidad**: borrar el autor destruye 3 tablas.
5. Ventaja: nunca queda un libro sin autor (integridad referencial garantizada).
6. Desventaja: **no hay confirmación ni возможность de deshacer**; un `delete()`
   accidental borra todo el historial editorial de ese autor.
7. Nota: `Category` y `Publisher` **no** se borran (no son hijos del autor, y las
   categorías de los libros borrados quedan huérfanas porque su FK era implícita
   en la tabla intermedia).

---

### 10.2 — Escenario PROTECT (`on_delete=models.PROTECT`)

**Paso 1 — Cambiar el modelo** en `library/models.py:87`:

```python
    author = models.ForeignKey(
        Author,
        on_delete=models.PROTECT,   # era CASCADE
        related_name='books',
        help_text='Author of this book'
    )
```

**Paso 2 — Migrar (obligatorio, si no el cambio no tiene efecto):**

```bash
python3 manage.py makemigrations library
python3 manage.py migrate
```

Salida:
```
library/migrations/0002_alter_book_author.py
```

**Paso 3 — Importar la excepción y crear el autor temporal:**

```python
>>> from django.db.models import ProtectedError
>>> tmp = Author.objects.create(first_name='Temp', last_name='Protegido', nationality='Test')
>>> l1 = Book.objects.create(title='Temp Book P1', isbn='9780000000011', publication_year=2020, pages=100, author=tmp)
>>> l2 = Book.objects.create(title='Temp Book P2', isbn='9780000000012', publication_year=2021, pages=200, author=tmp)
```

**Paso 4 — Intentar borrar:**

```python
>>> tmp.delete()
```

Salida real:
```
django.db.models.deletion.ProtectedError: ("Cannot delete some instances of model
'Author' because they are referenced through protected foreign keys: 'Book.author'.",
{<Book: Temp Book P1>, <Book: Temp Book P2>})
```

**Paso 5 — Verificar que nada se borró:**

```
Author sigue existiendo?  True
Libros siguen existiendo? 2
```

**Documentación de qué ocurre con PROTECT:**

1. `tmp.delete()` lanza `ProtectedError`.
2. **No se borra nada**: la operación es atómica, se rechaza completa.
3. El mensaje indica qué modelo bloquea (`Book.author`) y **cuáles** son los
   registros que lo bloquean (`{<Book: Temp Book P1>, <Book: Temp Book P2>}`).
4. Autor sin libros → `delete()` **sí** funciona (PROTECT solo bloquea si hay referencias).
5. `AuthorProfile` **no** bloquea: su FK sigue en CASCADE, así que un autor con
   perfil pero sin libros se borra junto con su perfil.
6. Hay que intervenir manualmente: `tmp.books.all().delete()` y luego `tmp.delete()`
   (verificado: funciona).
7. Ventaja: protege datos históricos; útil cuando borrar el padre destruiría
   información que no se puede recuperar.
8. Desventaja: en cascadas de varios niveles (libro → publicación) el borrado se
   vuelve manual y el error se propaga a la interfaz de usuario.

---

### 10.3 — Tabla comparativa

| Aspecto | CASCADE | PROTECT |
|---------|---------|---------|
| `autor.delete()` | Se ejecuta en silencio | Lanza `ProtectedError` |
| Libros del autor | Se borran | **Se conservan** |
| Publicaciones de esos libros | Se borran (cascada) | Se conservan |
| AuthorProfile | Se borra | Se borra (su FK sigue CASCADE) |
| Integridad referencial | Garantizada automáticamente | Garantizada por bloqueo |
| ¿Deshacible? | No | Sí (no se borra nada) |
| Autor sin libros | Se borra | Se borra |
| Orden de borrado | 1 sola llamada | N llamadas manuales |
| Riesgo | Pérdida de datos en cascada | Error en la aplicación |

---

### 10.4 — Efecto en la suite de tests

Al cambiar a `PROTECT`, el test `test_author_delete_cascades_books` falla
(1 de 25). Resultado real:

```
ERROR: test_author_delete_cascades_books (library.tests.OnDeleteBehaviorTest...)
django.db.models.deletion.ProtectedError: ("Cannot delete some instances of model
'Author' because they are referenced through protected foreign keys: 'Book.author'.")
Ran 25 tests - FAILED (errors=1)
```

Esto demuestra que los tests **detectan** el cambio de comportamiento.

**Restaurar CASCADE (estado original del lab):**

```python
# models.py:87 -> on_delete=models.CASCADE
```

```bash
python3 manage.py makemigrations library
python3 manage.py migrate
python3 manage.py test library
```

Verificado: `Ran 25 tests ... OK`.

---

## Comandos útiles de la consola

```python
# Entrar al shell
python3 manage.py shell

# Salir
exit()

# Cambiar a shell con IPython (colores, autocomplete)
python3 manage.py shell -i ipython

# Ejecutar un archivo .py con el contexto de Django
python3 manage.py shell < library/queries.py

# Ejecutar una línea suelta
python3 manage.py shell -c "from library.models import *; print(Book.objects.count())"

# Ver el SQL generado (muy útil para entender el __ y el JOIN)
>>> print(Book.objects.filter(author__last_name='Tolkien').query)
```

Ejemplo de SQL generado por `filter(publications__publisher__name__icontains='penguin')`:

```sql
SELECT ... FROM "library_book"
INNER JOIN "library_publication" ON ("library_book"."id" = "library_publication"."book_id")
INNER JOIN "library_publisher" ON ("library_publication"."publisher_id" = "library_publisher"."id")
WHERE UPPER("library_publisher"."name") LIKE UPPER('%PENGUIN%')
```

Cada `__` es un `JOIN`. Por eso `distinct()` es necesario al atravesar
relaciones *a many* (como `author__books__`): un mismo libro entra al
resultado una vez por cada coincidencia.
