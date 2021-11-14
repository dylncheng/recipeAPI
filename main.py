from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
import pandas as pd

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##recipe TABLE Configuration
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(250),  nullable=True)
    minutes = db.Column(db.String(250), nullable=True)
    tags = db.Column(db.String(250), nullable=True)
    n_steps = db.Column(db.String(250), nullable=True)
    steps = db.Column(db.String(250), nullable=True)
    description = db.Column(db.String(250), nullable=True)
    ingredients = db.Column(db.String(250), nullable=True)



    def to_dict(self):
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}


#CREATE DATABASE
# db.create_all()


def insert_data():
    df = pd.read_csv('RAW_recipes.csv')
    for index, row in df.iterrows():
        row['tags'] = row['tags'].replace("'", '').replace('[', '').replace(']', '').replace('"', '')
        row['steps'] = row['steps'].replace("'", '').replace('[', '').replace(']', '').replace('"', '')
        row['ingredients'] = row['ingredients'].replace("'", '').replace('[', '').replace(']', '').replace('"', '')
        new_recipe = Recipe(
            name=row['name'],
            minutes=row['minutes'],
            tags=row['tags'],
            n_steps=row['n_steps'],
            steps=row['steps'],
            description=row['description'],
            ingredients=row['ingredients']
        )
        db.session.add(new_recipe)
        db.session.commit()



@app.route("/")
def home():
    # insert_data() - POPULATE DATABASE
    return render_template("index.html")


## HTTP GET - Read Record

@app.route("/random")
def get_random_recipes():
    recipes = db.session.query(Recipe).all()
    random_recipe = random.choice(recipes)
    # Simply convert the random_recipe data record to a dictionary of key-value pairs.
    return jsonify(recipe=random_recipe.to_dict())


@app.route("/all")
def get_all_recipes():
    recipes = db.session.query(Recipe).all()
    return jsonify(recipes=[recipe.to_dict() for recipe in recipes])


@app.route("/search")
def get_recipe_by_name():
    query_name = request.args.get("name")
    # recipe = db.session.query(Recipe).filter_by(name=query_name).first()
    recipes = Recipe.query.filter(Recipe.name.contains(query_name))
    recipes = [recipe.to_dict() for recipe in recipes]
    if recipes:
        return jsonify(recipes=recipes)
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have that recipe."})

    # if recipe:
    #     return jsonify(recipe=recipe.to_dict())
    # else:
    #     return jsonify(error={"Not Found": "Sorry, we don't have that recipe."})

@app.route("/search-by-id")
def get_recipe_by_id():
    query_id = request.args.get("id")
    recipe = Recipe.query.get(query_id)
    if recipe:
        return jsonify(recipe=recipe.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have that recipe."})


@app.route("/add", methods=["POST"])
def post_new_recipe():
    new_recipe = Recipe(
        name=request.form.get("name"),
        minutes=request.form.get("minutes"),
        tags=request.form.get("tags"),
        n_steps=request.form.get("n_steps"),
        steps=request.form.get("steps"),
        description=request.form.get("description"),
        ingredients=request.form.get("ingredients")
    )
    db.session.add(new_recipe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new recipe.", "id": new_recipe.id}) #add id confirmation later


@app.route("/update-recipe/<recipe_id>", methods=["PATCH"])
def update_price(recipe_id):
    recipe = db.session.query(Recipe).get(recipe_id)
    if recipe:
        recipe.name = request.args.get('new_name') #add more fields
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the name."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry, a recipe with that id was not found in the database."}), 404


@app.route("/delete_recipe/<recipe_id>", methods=["DELETE"])
def delete_recipe(recipe_id):
    recipe = db.session.query(Recipe).get(recipe_id)
    api_key = request.args.get('api_key')
    if api_key == "TopSecretAPIKey":
        if recipe:
            db.session.delete(recipe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted recipe."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry, a recipe with that id was not found in the database."}), 404
    else:
        return jsonify(error={"error": "Sorry, that's not allowed. Make sure you have the correct api-key."}), 403



if __name__ == '__main__':
    app.run(debug=True)
