# Recipes

Store your recipes quickly and easily with the Recipes app.

Input your favorite recipes in an easy to use form and display them beautifully on the web.  Recipes can be edited and deleted at any time.  A Powerful search feature allows you to find recipes easily based on title, category, or ingredient.  Want to share a recipe with a friend who also uses Recipes? Use the share function to generate a base64 token.  Take your recipes with you!  With a single click all recipes can be exported as plaintext files.

Recipes is written in Python utilizing flask as a web framework, SQLite as a database, and Gunicorn as a web server.

## Register

Register an account by clicking **REGISTER** on the home page. Choose a unique username and a password with a length of at least eight characters.

## Login

Login by clicking **LOGIN** on the home page. Enter your username and password credentials.

## Adding Recipes

Click **NEW** to enter a new recipe. Required fields include title, ingredients, and directions.  Optional fields include servings, source, categories, and notes.  Check any applicable category boxes.  Ingredients and directions are both entered directly in textarea fields. Individual ingredients and direction steps are entered on separate lines.  Click **CREATE** to finalize the new recipe.

## Home Screen

On the home screen, each category can be accessed directly.  Recipes can also be searched by either title, category, or ingredient. Use the drop-down menu to the right of the search bar to switch search types.

## Editing Recipes

Edit a recipe by clicking on the <strong>EDIT</strong> button on an individual recipe's page.  The recipe's current data will be shown already filled in.  Any of the recipe's data can be altered and will be updated when the **EDIT** button is clicked.  

Share a recipe by clicking **SHARE** on a recipe's edit page. A base64 encoded token will be generated. This token can be shared to another Recipes server.

Download a recipe by clicking **DOWNLOAD** on a recipe's edit page. A plaintext version of the recipe will be generated and ready for download.

Delete a recipe by clicking **DELETE** on a recipe's edit page. You will be prompted before the recipe is permanently deleted.

## Import

On the home screen, click the **IMPORT** button to import a recipe from a base64 encoded token. The recipe will be immediately available.

## Export

On the home screen, click the **EXPORT** button to export all recipes in plaintext form zipped together into a single file.

## Usage

A few example container configs.

### Docker
```
docker run -d \
  -- name recipes \
  -p 8288:8288 \
  -v recipe_config:/config \
  --restart unless-stopped \
  petebuffon/recipes
```

### Docker-compose
```yaml
version: "2"
services:
  recipes:
    image: petebuffon/recipes
    container_name: recipes
    ports:
      - 8288:8288
    volumes:
      - recipes_config:/config
    restart: unless-stopped

volumes:
  recipes:config:
```
