CREATE TABLE IF NOT EXISTS "users" (
    "user_id" INTEGER PRIMARY KEY NOT NULL,
    "username" TEXT NOT NULL,
    "hash" TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS "recipes" (
    "recipe_id" INTEGER PRIMARY KEY NOT NULL,
    "title" TEXT NOT NULL,
    "source" TEXT,
    "servings" REAL,
    "notes" TEXT,
    "directions" TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS "owners" (
    "user_id" INTEGER NOT NULL,
    "recipe_id" INTEGER NOT NULL,
    FOREIGN KEY("user_id") REFERENCES "users"("user_id"),
    FOREIGN KEY("recipe_id") REFERENCES "recipes"("recipe_id")
);

CREATE TABLE IF NOT EXISTS "ingredients" (
    "ingredient_id" INTEGER PRIMARY KEY NOT NULL,
    "ingredient" TEXT NOT NULL,
    "recipe_id" INTEGER NOT NULL,
    FOREIGN KEY("recipe_id") REFERENCES "recipes"("recipe_id")
);

CREATE TABLE IF NOT EXISTS "categories" (
    "category_id" INTEGER PRIMARY KEY NOT NULL,
    "category" TEXT,
    "recipe_id" INTEGER NOT NULL,
    FOREIGN KEY("recipe_id") REFERENCES "recipes"("recipe_id")
);