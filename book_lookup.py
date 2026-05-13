import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


OPEN_LIBRARY_BASE = "https://openlibrary.org"


@dataclass
class BookMetadata:
    title: str
    author_name: str
    isbn: str | None = None
    publication_year: int | None = None
    cover_url: str | None = None


def lookup_book(query):
    cleaned_query = query.strip()
    if not cleaned_query:
        return None

    isbn = _normalize_isbn(cleaned_query)
    if isbn:
        return _lookup_by_isbn(isbn)

    return _lookup_by_title(cleaned_query)


def _lookup_by_isbn(isbn):
    params = urlencode({"bibkeys": f"ISBN:{isbn}", "format": "json", "jscmd": "data"})
    data = _get_json(f"{OPEN_LIBRARY_BASE}/api/books?{params}")
    item = data.get(f"ISBN:{isbn}") if data else None
    if not item:
        return None

    authors = item.get("authors") or []
    author_name = authors[0].get("name") if authors else "Unbekannter Autor"
    published = item.get("publish_date")
    cover = item.get("cover") or {}

    return BookMetadata(
        title=item.get("title") or f"ISBN {isbn}",
        author_name=author_name,
        isbn=isbn,
        publication_year=_extract_year(published),
        cover_url=cover.get("large") or cover.get("medium") or cover.get("small"),
    )


def _lookup_by_title(title):
    params = urlencode({"title": title, "limit": 1, "fields": "title,author_name,first_publish_year,isbn,cover_i"})
    data = _get_json(f"{OPEN_LIBRARY_BASE}/search.json?{params}")
    docs = data.get("docs") if data else None
    if not docs:
        return None

    doc = docs[0]
    isbns = doc.get("isbn") or []
    isbn = next((_normalize_isbn(value) for value in isbns if _normalize_isbn(value)), None)
    cover_id = doc.get("cover_i")
    author_names = doc.get("author_name") or []

    return BookMetadata(
        title=doc.get("title") or title,
        author_name=author_names[0] if author_names else "Unbekannter Autor",
        isbn=isbn,
        publication_year=doc.get("first_publish_year"),
        cover_url=f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else None,
    )


def _get_json(url):
    request = Request(url, headers={"User-Agent": "BookAlchemy/1.0"})
    try:
        with urlopen(request, timeout=8) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return None


def _normalize_isbn(value):
    isbn = value.replace("-", "").replace(" ", "")
    if len(isbn) == 10 and all(char.isdigit() or char.upper() == "X" for char in isbn):
        return isbn.upper()
    if len(isbn) == 13 and isbn.isdigit():
        return isbn
    return None


def _extract_year(value):
    if not value:
        return None

    for part in str(value).replace(",", " ").split():
        if len(part) == 4 and part.isdigit():
            return int(part)

    return None
