from flask import Blueprint, flash, redirect, render_template, request, send_from_directory, url_for

from book_lookup import lookup_book
from data_models import Author, Book, db


main = Blueprint("main", __name__)


@main.route("/")
def home():
    sort_by = request.args.get("sort_by", "title")
    search_query = request.args.get("search", "").strip()
    search_field = request.args.get("search_field", "title")

    query = Book.query.join(Author)

    if search_query:
        if search_field == "author":
            query = query.filter(Author.name.ilike(f"%{search_query}%"))
        else:
            query = query.filter(Book.title.ilike(f"%{search_query}%"))

    if sort_by == "author":
        books = query.order_by(Author.name, Book.title).all()
    else:
        books = query.order_by(Book.title).all()

    return render_template(
        "home.html",
        books=books,
        sort_by=sort_by,
        search_query=search_query,
        search_field=search_field,
    )


@main.route("/add_book", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        lookup_query = request.form.get("lookup_query", "").strip()
        rating = request.form.get("rating")

        if not lookup_query:
            flash("Bitte gib eine ISBN oder einen Titel ein.", "warning")
            return redirect(url_for("main.add_book"))

        metadata = lookup_book(lookup_query)
        if not metadata:
            flash("Dazu wurden keine Buchdaten gefunden. Prüfe ISBN oder Titel und versuche es erneut.", "warning")
            return redirect(url_for("main.add_book"))

        if metadata.isbn and Book.query.filter_by(isbn=metadata.isbn).first():
            flash(f"'{metadata.title}' ist bereits in deiner Bibliothek.", "warning")
            return redirect(url_for("main.add_book"))

        author = _get_or_create_author(metadata.author_name)
        existing_book = Book.query.filter_by(title=metadata.title, author_id=author.id).first()
        if existing_book:
            flash(f"'{metadata.title}' ist bereits in deiner Bibliothek.", "warning")
            return redirect(url_for("main.add_book"))

        book = Book(
            title=metadata.title,
            isbn=metadata.isbn,
            publication_year=metadata.publication_year,
            rating=int(rating) if rating else None,
            cover_url=metadata.cover_url,
            author=author,
        )
        db.session.add(book)
        db.session.commit()

        flash(f"'{book.title}' von {author.name} wurde hinzugefügt.", "success")
        return redirect(url_for("main.book_detail", book_id=book.id))

    return render_template("add_book.html")


@main.route("/book/<int:book_id>")
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template("book_detail.html", book=book)


@main.route("/author/<int:author_id>")
def author_detail(author_id):
    author = Author.query.get_or_404(author_id)
    return render_template("author_detail.html", author=author)


@main.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    author = book.author
    title = book.title
    author_name = author.name

    db.session.delete(book)
    db.session.commit()

    if not author.books:
        db.session.delete(author)
        db.session.commit()
        flash(f"'{title}' und '{author_name}' wurden gelöscht.", "success")
    else:
        flash(f"'{title}' wurde gelöscht.", "success")

    return redirect(url_for("main.home"))


@main.route("/author/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id):
    author = Author.query.get_or_404(author_id)
    author_name = author.name

    db.session.delete(author)
    db.session.commit()
    flash(f"'{author_name}' und alle zugehörigen Bücher wurden gelöscht.", "success")
    return redirect(url_for("main.home"))


@main.route("/manifest.webmanifest")
def manifest():
    return send_from_directory("static", "manifest.webmanifest", mimetype="application/manifest+json")


@main.route("/service-worker.js")
def service_worker():
    return send_from_directory("static", "service-worker.js", mimetype="application/javascript")


def _get_or_create_author(name):
    normalized_name = name.strip() or "Unbekannter Autor"
    author = Author.query.filter(Author.name.ilike(normalized_name)).first()
    if author:
        return author

    author = Author(name=normalized_name)
    db.session.add(author)
    db.session.flush()
    return author
