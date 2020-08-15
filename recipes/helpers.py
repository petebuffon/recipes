"""Helper functions."""
import sqlite3
import re
from json import loads, dumps
from flask import redirect, session, request
from functools import wraps


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


class Categories():
    """Recipe categories."""

    def __init__(self):
        """Categories class."""
        self.categories = ["breakfast", "main", "salad", "side", "dessert", "drink", "poultry",
                           "beef", "pork", "seafood", "veggie"]

    def check(self):
        """Return list of checked categories."""
        categories = []

        for category in self.categories:
            if category in request.form:
                categories.append(category)
        return categories


def parse_ingredients(raw_ingredients):
    """Parse individual ingredients from ingredients form data."""
    ingredients = []
    for ingredient in raw_ingredients.split("\r\n"):
        if ingredient:
            ingredients.append(ingredient)
    return ingredients


def parse_paragraph(name, raw_text):
    """Parse individual paragraphs from form data."""
    if not raw_text:
        return None
    text = []
    for paragraph in raw_text.split("\r\n"):
        if paragraph:
            text.append(paragraph)
    return json.dumps(text)


class SQL:
    """SQL class for simplifying database commands."""

    def __init__(self, database):
        """Database file to perform queries on."""
        self.database = database

    def execute(self, *args):
        """General execute function."""
        conn = sqlite3.connect(self.database)

        if args[0].split(" ")[0] == "SELECT":
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute(*args)
            return c.fetchall()

        else:
            c = conn.cursor()
            c.execute(*args)

        conn.commit()
        conn.close()

    def initialize(self, schema):
        """Initialize database from schema file."""
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        with open(schema) as file:
            c.executescript(file.read())


class Pagination:
    """SQL query, current page, items per page."""

    def __init__(self, query, page, per_page):
        """Sqlite class."""
        self.per_page = per_page
        self.query = query
        self.total = len(query)
        self.page = page
        self.pages = []
        for i in range(0, self.total, self.per_page):
            self.pages.append(query[i: i + self.per_page])
        if self.total == 0:
            self.items = []
        else:
            self.items = self.pages[page - 1]
        self.has_next = len(self.pages) > page
        self.has_prev = page - 1 > 0
        if self.has_prev:
            self.prev = self.page - 1
        if self.has_next:
            self.next = self.page + 1


def plaintext(recipe_id, db):
    """Generate plaintext recipe."""
    # retrieve recipe
    try:
        recipe = db.execute("SELECT * FROM recipes JOIN owners ON recipes.recipe_id="
                            "owners.recipe_id WHERE recipes.recipe_id = ?",
                            (recipe_id,))[0]
        directions = loads(recipe["directions"])
    except IndexError:
        return render_template('page_not_found.html'), 404
    ingredients = db.execute("SELECT ingredient FROM ingredients WHERE recipe_id = ?",
                             (recipe_id,))
    categories = db.execute("SELECT category FROM categories WHERE recipe_id = ?",
                            (recipe_id,))

    # build recipe string
    f = recipe[1] + "\n\n"
    for item in recipe[2:5]:
        f += str(item) + "\n"
    f += "\n"
    for category in categories:
        f += category[0] + "\n"
    f += "\n"
    for ingredient in ingredients:
        f += ingredient[0] + "\n"
    f += "\n"
    for direction in directions[:len(directions)-1]:
        f += direction + "\n\n"
    f += directions[len(directions)-1]

    return f
