# Recipes

Store your recipes quickly and easily with the Recipes app.

Input your favorite recipes in an easy to use form and display them beautifully on theweb.  
Recipes can be edited and deleted at any time.

Powerful search allows you to find recipes based on title, category, or ingredient.
Want to share a recipe with a friend who also uses Recipes?  Use the share function togenerate a base64 token.

Your recipes aren't stuck in the database, with a single click all recipes can beexported as plaintext files.

Recipes is written in Python utilizing flask as a web framework, SQLite as a database,and Gunicorn as a web server.

## Register


Register an account by clicking **REGISTER** on the home page.  Choose a
unique username and a password with a length of at least eight characters.

## Login

Login by clicking **LOGIN** on the home page.  Enter your username andpassword credentials.

## Adding Recipes

Click **NEW** to enter a new recipe.  Required fields include title,ingredients, and directions.  Optional fields include servings, source, categories, andnotes.
Check any applicable category boxes.
Ingredients and directions are both entered directly in textarea fields.  Individualingredients and direction steps are entered on separate lines.
Click **CREATE** to enter the new recipe.

## Home Screen

On the home screen, each category can be accessed directly.
Recipes can also be searched by either title, category, or ingredient.  Use thedrop-down menu to the right of the search bar to switch search types.

## Editing Recipes

Edit a recipe by clicking on the **EDIT** button on an individual recipe'spage.
The recipe's current data will be shown already filled in.
Any of the recipe's data can be altered and will be updated when the **EDIT** button is clicked.
Share a recipe by clicking **SHARE** on a recipe's edit page.  A base64encoded token will be generated.  This token can be shared another Recipes server.
Download a recipe by clicking **DOWNLOAD** on a recipe's edit page.  Aplaintext version of the recipe will be generated and ready for download.
Delete a recipe by clicking **DELETE** on a recipe's edit page.  You willbe prompted before the recipe is deleted.    

## Import

On the home screen, click the **IMPORT** button to import a recipe from abase64 encoded token.  The recipe will then be available.

## Export

On the home screen, click the **EXPORT** button to export all recipes inplaintext form zipped together in a single file.