"""Recipes application."""
import logging
import os
import time
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo
from io import BytesIO
from base64 import b64encode, b64decode
from json import loads, dumps
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask import render_template_string, send_file
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from forms import Register, Login, Recipe, Search, Import
from helpers import login_required, parse_ingredients, parse_paragraph, SQL, Pagination, Categories
from helpers import plaintext

app = Flask(__name__)

# Secret key
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.after_request
def after_request(response):
    """Ensure responses aren't cached."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Load SQLite database
db = SQL(Path("/config") / "recipes.db")
db.initialize("schema.sql")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Website homepage."""
    form = Search()

    if form.validate_on_submit():
        search = request.form["search"]
        if not search:
            search = "*"
        select = request.form["select"]
        return redirect(url_for("search", **{select: search}, page=1))

    return render_template("index.html", form=form)


@app.route("/help")
@login_required
def help():
    """Help page."""
    return render_template("help.html")


@app.route("/delete/<recipe_id>")
@login_required
def delete(recipe_id):
    """Delete recipe."""
    owner = db.execute("SELECT user_id FROM owners WHERE recipe_id = ?",
                       (recipe_id,))[0]["user_id"]
    if owner != session["user_id"]:
        return render_template('page_not_found.html'), 404

    db.execute("DELETE FROM recipes WHERE recipe_id = ?",
               (recipe_id,))
    db.execute("DELETE FROM categories WHERE recipe_id = ?",
               (recipe_id,))
    db.execute("DELETE FROM ingredients WHERE recipe_id = ?",
               (recipe_id,))
    db.execute("DELETE FROM owners WHERE recipe_id = ?",
               (recipe_id,))
    flash("Recipe deleted!")
    return redirect(url_for("index"))


@app.route("/import", methods=["GET", "POST"])
@login_required
def import_recipe():
    """Import recipe from base64 encoded text."""
    form = Import()
    errors = None

    if form.validate_on_submit():
        encoded = request.form["encoded"]
        try:
            decoded = loads(b64decode(encoded.encode("utf-8")).decode("utf-8"))
            # recipe table
            title = decoded["title"]
            servings = decoded["servings"]
            source = decoded["source"]
            notes = decoded["notes"]
            directions = dumps(decoded["directions"])
            db.execute("INSERT INTO recipes (title, servings, source, notes, directions) VALUES "
                       "(?, ?, ?, ?, ?)", (title, servings, source, notes, directions))

            # categories table
            recipe_id = db.execute("SELECT recipe_id FROM recipes WHERE title = ?",
                                   (title,))[0]["recipe_id"]
            for category in decoded["categories"]:
                db.execute("INSERT INTO categories (category, recipe_id) VALUES (?, ?)",
                           (category, recipe_id))

            # ingredients table
            for ingredient in decoded["ingredients"]:
                db.execute("INSERT INTO ingredients (ingredient, recipe_id) VALUES (?, ?)",
                           (ingredient, recipe_id))

            # owners table
            db.execute("INSERT INTO owners (recipe_id, user_id) VALUES (?, ?)",
                       (recipe_id, session["user_id"]))

            flash("Recipe imported!")
            return redirect(url_for("index"))

        except TypeError:
            errors = ["Invalid text."]

    return render_template("import.html", form=form, errors=errors)


@app.route("/export")
@login_required
def export():
    """Export all recipes as plaintext in compressed directory."""
    recipes = db.execute("SELECT recipes.recipe_id FROM recipes JOIN owners ON recipes.recipe_id="
                         "owners.recipe_id WHERE user_id = ?", (session["user_id"],))
    memory_file = BytesIO()
    with ZipFile(memory_file, "w") as zf:
        for recipe in recipes:
            data = ZipInfo(str(recipe[0]) + ".txt")
            data.date_time = time.localtime(time.time())[:6]
            data.compress_type = ZIP_DEFLATED
            zf.writestr(data, plaintext(recipe[0], db))
    memory_file.seek(0)
    return send_file(memory_file, attachment_filename='recipes.zip', as_attachment=True)


@app.route("/download/<recipe_id>.txt")
@login_required
def download(recipe_id):
    """Download recipe as plaintext."""
    f = plaintext(recipe_id, db)
    return render_template_string(f)


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """Search page."""
    form = Search()

    if form.validate_on_submit():
        search = request.form["search"]
        if not search:
            search = "*"
        select = request.form["select"]
        return redirect(url_for("search", **{select: search}, page=1))

    page = request.args.get('page', default=1, type=int)
    user_id = session["user_id"]
    if request.args.get("title"):
        select = "title"
        search = request.args.get("title")
    elif request.args.get("category"):
        select = "category"
        search = request.args.get("category")
    elif request.args.get("ingredient"):
        select = "ingredient"
        search = request.args.get("ingredient")
    else:
        return render_template('page_not_found.html'), 404

    if search == "*":
        recipes = db.execute("SELECT title, recipes.recipe_id FROM recipes JOIN owners ON "
                             "recipes.recipe_id=owners.recipe_id WHERE user_id = ?",
                             (user_id,))
    elif select == "title":
        recipes = db.execute("SELECT title, recipes.recipe_id FROM recipes JOIN owners ON "
                             "recipes.recipe_id=owners.recipe_id WHERE user_id = ? AND title "
                             "LIKE ?", (user_id, "%" + search + "%"))

    elif select == "category":
        recipes = db.execute("SELECT title, recipes.recipe_id FROM recipes INNER JOIN owners "
                             "ON recipes.recipe_id=owners.recipe_id INNER JOIN categories ON "
                             "recipes.recipe_id=categories.recipe_id WHERE user_id = ? AND "
                             "category = ? GROUP BY title", (user_id, search))
    else:
        recipes = db.execute("SELECT title, recipes.recipe_id FROM recipes INNER JOIN owners "
                             "ON recipes.recipe_id=owners.recipe_id INNER JOIN ingredients ON "
                             "recipes.recipe_id=ingredients.recipe_id WHERE user_id = ? AND "
                             "(' ' || ingredient || ' ') LIKE ? GROUP BY title", (user_id, "% " +
                                                                                  search + " %"))
    # try pages
    per_page = 10
    try:
        pages = Pagination(recipes, page, per_page)
    except IndexError:
        return render_template('page_not_found.html'), 404

    if pages.total >= pages.per_page:
        recipes = pages.items

    return render_template("search.html", form=form, select=select, search=search, pages=pages,
                           recipes=recipes)


@app.route("/recipe/<recipe_id>")
@login_required
def recipe(recipe_id):
    """Display recipe."""
    title = request.args.get("title")
    try:
        recipe = db.execute("SELECT * FROM recipes JOIN owners ON recipes.recipe_id="
                            "owners.recipe_id WHERE recipes.recipe_id = ?",
                            (recipe_id,))[0]
        directions = loads(recipe["directions"])
    except IndexError:
        return render_template('page_not_found.html'), 404
    ingredients = db.execute("SELECT * FROM ingredients WHERE recipe_id = ?",
                             (recipe_id,))

    return render_template("recipe.html", recipe=recipe, directions=directions,
                           ingredients=ingredients)


@app.route("/share/<recipe_id>")
@login_required
def share(recipe_id):
    """Create b64 encoded text for recipe import."""
    try:
        recipe = db.execute("SELECT * FROM recipes JOIN owners ON recipes.recipe_id="
                            "owners.recipe_id WHERE recipes.recipe_id = ?",
                            (recipe_id,))[0]
        directions = loads(recipe["directions"])
    except IndexError:
        return render_template('page_not_found.html'), 404

    # recipes
    json = {}
    json["title"], json["servings"] = recipe["title"], recipe["servings"]
    json["source"], json["notes"] = recipe["source"], recipe["notes"]
    json["directions"] = loads(recipe["directions"])

    # categories
    query = db.execute("SELECT category FROM categories WHERE recipe_id = ?",
                       (recipe_id,))
    json["categories"] = [x["category"] for x in query]

    # ingredients
    query = db.execute("SELECT * FROM ingredients WHERE recipe_id = ?",
                       (recipe_id,))
    json["ingredients"] = [x["ingredient"] for x in query]
    json = dumps(json)
    encoded = b64encode(json.encode("utf-8"))

    return render_template("share.html", encoded=encoded.decode("utf-8"), recipe=recipe)


@app.route("/edit/<recipe_id>", methods=["GET", "POST"])
@login_required
def edit(recipe_id):
    """Edit recipe."""
    form = Recipe()
    categories = Categories()
    errors = None
    try:
        recipe = db.execute("SELECT * FROM recipes JOIN owners ON recipes.recipe_id="
                            "owners.recipe_id WHERE recipes.recipe_id = ?",
                            (recipe_id,))[0]
    except IndexError:
        return render_template('page_not_found.html'), 404

    ingredients = db.execute("SELECT * FROM ingredients WHERE recipe_id = ?", (recipe_id,))
    checked = [x["category"] for x in db.execute("SELECT category FROM categories WHERE recipe_id "
                                                 "= ?", (recipe_id,))]

    form.ingredients.data = "\n\n".join((x["ingredient"] for x in ingredients))
    form.directions.data = "\n\n".join(loads(recipe["directions"]))

    if form.validate_on_submit():

        # recipe table
        if recipe["title"] != request.form["title"]:
            title = request.form["title"]
            query = db.execute("SELECT title FROM recipes WHERE title = ?",
                               (title,))

            if not query:
                db.execute("UPDATE recipes SET title = ? WHERE recipe_id = ?", (title, recipe_id))

                if request.form["servings"] and recipe["servings"] != request.form["servings"]:
                    servings = request.form["servings"]
                    db.execute("UPDATE recipes SET servings = ? WHERE recipe_id = ?",
                               (servings, recipe_id))

                if request.form["source"] and recipe["source"] != request.form["source"]:
                    source = request.form["source"]
                    db.execute("UPDATE recipes SET source = ? WHERE recipe_id = ?",
                               (source, recipe_id))

                if (request.form["notes"] and recipe["notes"] !=
                        parse_paragraph("notes", request.form["notes"])):
                    notes = parse_paragraph("notes", request.form["notes"])
                    db.execute("UPDATE recipes SET notes = ? WHERE recipe_id = ?",
                               (notes, recipe_id))

                if recipe["directions"] != parse_paragraph("directions", request.form["directions"]):
                    directions = parse_paragraph("directions", request.form["directions"])
                    db.execute("UPDATE recipes SET directions = ? WHERE recipe_id = ?",
                               (directions, recipe_id))

                categories = categories.check()
                # check for new categories
                for category in categories:
                    if category not in checked:
                        db.execute("INSERT into categories (category, recipe_id) VALUES (?, ?)",
                                   (category, recipe_id))
                # check for deleted categories
                for category in checked:
                    if category not in categories:
                        db.execute("DELETE FROM categories WHERE category = ? AND recipe_id = ?",
                                   (category, recipe_id))

                # ingredients table
                updated_ingredients = parse_ingredients(request.form["ingredients"])
                # check for new ingredients
                ingredients_set = set(x["ingredient"] for x in ingredients)
                for ingredient in updated_ingredients:
                    if ingredient not in ingredients_set:
                        db.execute("INSERT INTO ingredients (ingredient, recipe_id) VALUES (?, ?)",
                                   (ingredient, recipe_id))
                # check for deleted ingredients
                updated_ingredients_set = set(updated_ingredients)
                for ingredient in ingredients:
                    if ingredient["ingredient"] not in updated_ingredients_set:
                        db.execute("DELETE FROM ingredients WHERE ingredient = ? AND recipe_id = ?",
                                   (ingredient["ingredient"], recipe_id))

                flash("Recipe edited!")
                return redirect(url_for("index"))
            else:
                errors = ["Recipe name must be unique."]

    return render_template("edit.html", form=form, errors=errors, categories=categories.categories,
                           checked=checked, recipe=recipe)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""
    form = Login()
    errors = None

    if form.validate_on_submit():
        username = request.form["username"]
        query = db.execute("SELECT * FROM users WHERE username = ?", (username,))

        # Ensure username exists and password is correct
        if query and check_password_hash(query[0]["hash"], request.form["password"]):

            # Remember which user has logged in
            session["user_id"] = query[0]["user_id"]
            return redirect(url_for("index"))
        else:
            errors = ["Invalid credentials."]

    return render_template("login.html", form=form, errors=errors)


@app.route("/logout")
def logout():
    """Log user out."""
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register new user."""
    form = Register()
    errors = None

    if form.validate_on_submit():
        username = request.form["username"]
        query = db.execute("SELECT username FROM users WHERE username = ?",
                           (username,))
        if not query:
            password = request.form["password"]
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
                       (username, generate_password_hash(password)))
            # Log user in
            query = db.execute("SELECT user_id FROM users WHERE username = ?",
                               (username,))
            session["user_id"] = query[0]["user_id"]
            flash("Registered!")
            return redirect(url_for("index"))
        else:
            errors = ["Username already taken."]

    return render_template("register.html", form=form, errors=errors)


@app.route("/new", methods=["GET", "POST"])
@login_required
def new():
    """Create new recipe."""
    form = Recipe()
    categories = Categories()
    errors = None

    if form.validate_on_submit():
        # recipe table
        title = request.form["title"]
        query = db.execute("SELECT title FROM recipes WHERE title = ?",
                           (title,))

        if not query:
            if request.form["servings"]:
                servings = request.form["servings"]
            else:
                servings = None
            if request.form["source"]:
                source = request.form["source"]
            else:
                source = None
            notes = parse_paragraph("notes", request.form["notes"])
            directions = parse_paragraph("directions", request.form["directions"])
            db.execute("INSERT INTO recipes (title, servings, source, notes, directions) VALUES "
                       "(?, ?, ?, ?, ?)", (title, servings, source, notes, directions))

            # categories table
            categories = categories.check()
            recipe_id = db.execute("SELECT recipe_id FROM recipes WHERE title = ?",
                                   (title,))[0]["recipe_id"]
            for category in categories:
                db.execute("INSERT INTO categories (category, recipe_id) VALUES (?, ?)",
                           (category, recipe_id))

            # ingredients table
            ingredients = parse_ingredients(request.form["ingredients"])
            for ingredient in ingredients:
                db.execute("INSERT INTO ingredients (ingredient, recipe_id) VALUES (?, ?)",
                           (ingredient, recipe_id))

            # owners table
            db.execute("INSERT INTO owners (recipe_id, user_id) VALUES (?, ?)",
                       (recipe_id, session["user_id"]))

            flash("New recipe added!")
            return redirect(url_for("index"))
        else:
            errors = ["Recipe name must be unique."]

    return render_template("new.html", form=form, errors=errors, categories=categories.categories)


@app.errorhandler(404)
def page_not_found(error):
    """404 page not found."""
    return render_template('page_not_found.html'), 404
