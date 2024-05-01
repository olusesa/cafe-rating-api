import os 
import psycopg2
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL
import csv

app = Flask(__name__)
Bootstrap5(app)
url = os.getenv("DATABASE_URL")
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
connection = psycopg2.connect(url)

class CafeForm(FlaskForm):
    cafe_username = StringField('Cafe username', validators=[DataRequired()])
    cafe = StringField('Cafe name', validators=[DataRequired()])
    location = StringField("Cafe Location on Google Maps (URL)", validators=[DataRequired(), URL()])
    open = StringField("Opening Time e.g. 8AM", validators=[DataRequired()])
    close = StringField("Closing Time e.g. 5:30PM", validators=[DataRequired()])
    coffee_rating = SelectField("Coffee Rating", choices=["0", "2", "4", "6", "8", "10"], validators=[DataRequired()])
    wifi_rating = SelectField("Wifi Strength Rating", choices=["0", "2", "4", "6", "8", "10"], validators=[DataRequired()])
    power_rating = SelectField("Power Socket Availability", choices=["0", "2", "4", "6", "8", "10"], validators=[DataRequired()])
    submit = SubmitField('Submit')

CREATE_CAFE_SHOPS_TABLE = "CREATE TABLE IF NOT EXISTS cafe_shops (id SERIAL PRIMARY KEY, cafe_username TEXT, cafe TEXT, location TEXT, open TEXT, close TEXT, coffee_rating TEXT, wifi_rating TEXT, power_rating TEXT);"

with connection:
    with connection.cursor() as cursor:
        cursor.execute(CREATE_CAFE_SHOPS_TABLE)

INSERT_CAFE_SHOP_RETURN_ID = ("INSERT INTO cafe_shops (cafe_username, cafe, location, open, close, "
                              "coffee_rating, wifi_rating, power_rating) "
                              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;")
SELECT_ALL_CAFE_SHOPS = "SELECT * FROM cafe_shops;"
SELECT_CAFE_SHOPS_BY_ID = ("SELECT id, cafe_username, cafe, location, open, close, coffee_rating, coffee_rating, "
                           "power_rating FROM cafe_shops WHERE id = %s;")
UPDATE_CAFE_USERNAME_BY_ID = "UPDATE cafe_shops SET cafe_username = %s WHERE id = %s;"
UPDATE_CAFE_SHOPS_BY_ID = "UPDATE cafe_shops SET cafe = %s WHERE id = %s;"
UPDATE_CAFE_LOCATION_BY_ID = "UPDATE cafe_shops SET location = %s WHERE id = %s;"
UPDATE_CAFE_OPEN_BY_ID = "UPDATE cafe_shops SET open = %s WHERE id = %s;"
UPDATE_CAFE_CLOSE_BY_ID = "UPDATE cafe_shops SET close = %s WHERE id = %s;"
UPDATE_CAFE_COFFE_RATING_BY_ID = "UPDATE cafe_shops SET coffee_rating = %s WHERE id = %s;"
UPDATE_CAFE_WIFI_RATING_BY_ID = "UPDATE cafe_shops SET wifi_rating = %s WHERE id = %s;"
UPDATE_CAFE_POWER_RATING_BY_ID = "UPDATE cafe_shops SET power_rating = %s WHERE id = %s;"
DELETE_CAFE_SHOP_BY_ID = "DELETE FROM cafe_shops WHERE id = %s;"

@app.route("/add/cafe-shop/<cafe_username>", endpoint='create_cafe_shop', methods=["POST"])
def create_cafe_shop(cafe_username):
    data = request.get_json()
    form = CafeForm()
    form.cafe_username = data["cafe_username"]
    form.cafe = data["cafe"]
    form.location = data["location"]
    form.open = data["open"]
    form.close = data["close"]
    form.coffee_rating = data["coffee_rating"]
    form.wifi_rating = data["wifi_rating"]
    form.power_rating = data["power_rating"]
    if form.validate_on_submit():
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(INSERT_CAFE_SHOP_RETURN_ID, (form.cafe_username.data, form.cafe.data, form.location.data,
                                                            form.open.data, form.close.data, form.coffee_rating.data,
                                                            form.wifi_rating.data, form.power_rating.data))
    return render_template('add.html', form=form)
@app.route("/", methods=["GET"])
def get_all_cafe_shops():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_ALL_CAFE_SHOPS)
            cafe_shops = cursor.fetchall()
            if cafe_shops:
                result = []
                for cafe_shop in cafe_shops:
                    result.append({"id": cafe_shops[0], "cafe_username": cafe_shops[1]})
                return jsonify(result)
            else:
                return jsonify({"error": f"cafe_shops not found."}), 404
    return render_template("cafes.html")

@app.route("/search/cafe-shop/<int:cafe_id>", endpoint='get_cafes', methods=["GET"])
def get_cafes(cafe_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM cafe_shops WHERE id = %s", (cafe_id,))
            cafe_shop = cursor.fetchone()
            if cafe_shop:
                return jsonify({"id": cafe_shop[0], "cafe": cafe_shop[1]})
            else:
                return jsonify({"error": f"Cafe shop with ID {cafe_id} not found."}), 404
    return render_template("index.html")

@app.route("/update/cafe-entries/<int:cafe_id>", endpoint='update_cafe_entries', methods=["PUT"])
def update_cafe_entries(cafe_id):
    data = request.get_json()
    form = CafeForm()
    form.cafe_username = data["cafe_username"]
    form.cafe = data["cafe"]
    form.location = data["location"]
    form.open = data["open"]
    form.close = data["close"]
    form.coffee_rating = data["coffee_rating"]
    form.wifi_rating = data["wifi_rating"]
    form.power_rating = data["power_rating"]
    if form.validate_on_submit():
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(INSERT_CAFE_SHOP_RETURN_ID, (form.cafe_username, form.cafe, form.location,
                                                            form.open, form.close, form.coffee_rating, form.wifi_rating,
                                                            form.power_rating))
            if cursor.rowcount == 0:
                return jsonify({"error": f"Cafe shop with ID {cafe_id} not found."}), 404
        return jsonify({"id": cafe_id, "Cafe Username": form.cafe_username, "Cafe": form.cafe, "Coffee Rating": form.coffee_rating,
                    "Wifi Rating": form.wifi_rating, "Power Rating": form.power_rating, "message": f"Cafe shop with cafe username"
                                                    f"  {form.cafe_username} entries updated successfully."})
    return render_template('index.html', form=form)

@app.route("/update/cafe-shop/<int:cafe_id>", endpoint='update_cafe_username_entry', methods=["PATCH"])
def update__cafe_username_entry(cafe_id):
    data = request.get_json()
    form = CafeForm()
    form.cafe_username = data["cafe_username"]
    if form.validate_on_submit():
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(UPDATE_CAFE_USERNAME_BY_ID, (cafe_id, form.cafe_username))
            if cursor.rowcount == 0:
                return jsonify({"error": f"Cafe shop with ID {cafe_id} not found."}), 404
        return jsonify({"id": cafe_id, "cafe username": form.cafe_username, "message": f"Cafe shop with ID {cafe_id} "
                                    f"and cafe_username : {form.cafe_username} updated successfully."})

    return render_template('index.html', form=form)

@app.route("/update/cafe-shop/<int:cafe_id>", endpoint='update_location_entry', methods=["PATCH"])
def update_location_entry(cafe_id):
    data = request.get_json()
    form = CafeForm()
    form.cafe_username = data["cafe_username"]
    if form.validate_on_submit():
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(UPDATE_CAFE_LOCATION_BY_ID, (cafe_id, form.location))
            if cursor.rowcount == 0:
                return jsonify({"error": f"Cafe shop with ID {cafe_id} not found."}), 404
        return jsonify({"id": cafe_id, "location": form.location, "message": f"Cafe shop with ID {cafe_id} and "
                                                                    f"location : {form.location} updated successfully."})

    return render_template('index.html', form=form)

@app.route("/update/cafe-shop/<int:cafe_id>", endpoint='update_open_entry', methods=["PATCH"])
def update_open_entry(cafe_id):
    data = request.get_json()
    form = CafeForm()
    form.cafe_username = data["cafe_username"]
    if form.validate_on_submit():
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(UPDATE_CAFE_OPEN_BY_ID, (cafe_id, form.open))
            if cursor.rowcount == 0:
                return jsonify({"error": f"User with ID {cafe_id} not found."}), 404
        return jsonify({"id": cafe_id, "open": form.open, "message": f"Cafe shop with ID {cafe_id} "
                                                            f"and open : {form.open} updated successfully."})

    return render_template('index.html', form=form)

@app.route("/update/cafe-shop/<int:cafe_id>", endpoint='update_close_entry', methods=["PATCH"])
def update_close_entry(cafe_id):
    data = request.get_json()
    form = CafeForm()
    form.cafe_username = data["cafe_username"]
    if form.validate_on_submit():
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(UPDATE_CAFE_CLOSE_BY_ID, (cafe_id, form.close))
            if cursor.rowcount == 0:
                return jsonify({"error": f"Cafe shop with ID {cafe_id} not found."}), 404
        return jsonify({"id": cafe_id, "close": form.close, "message": f"User with ID {cafe_id} "
                                                            f"and close : {form.close} updated successfully."})

    return render_template('index.html', form=form)

@app.route("/update/cafe-shop/<int:cafe_id>", endpoint='update_coffe_rating_entry', methods=["PATCH"])
def update_coffee_rating_entry(cafe_id):
    data = request.get_json()
    form = CafeForm()
    form.cafe_username = data["cafe_username"]
    if form.validate_on_submit():
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(UPDATE_CAFE_COFFE_RATING_BY_ID, (cafe_id, form.coffee_rating))
            if cursor.rowcount == 0:
                return jsonify({"error": f"Cafe shop with ID {cafe_id} not found."}), 404
        return jsonify({"id": cafe_id, "coffee_rating": form.coffee_rating, "message": f"Cafe shop ID {cafe_id} "
                                                            f" and open : {form.cafe_username} updated successfully."})

    return render_template('index.html', form=form)

@app.route("/update/cafe-shop/<int:cafe_id>", endpoint='update_wifi_rating_entry', methods=["PATCH"])
def update_wifi_rating_entry(cafe_id):
    data = request.get_json()
    form = CafeForm()
    form.wifi_rating = data["wifi_rating"]
    if form.validate_on_submit():
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(UPDATE_CAFE_WIFI_RATING_BY_ID, (cafe_id, form.wifi_rating))
            if cursor.rowcount == 0:
                return jsonify({"error": f"Cafe shop with ID {cafe_id} not found."}), 404
        return jsonify({"id": cafe_id, "wifi_rating": form.wifi_rating, "message": f"Cafe shop with ID {cafe_id} "
                                                            f"and open : {form.wifi_rating} updated successfully."})

    return render_template('index.html', form=form)
@app.route("/update/cafe-shop/<int:cafe_id>", endpoint='update_power_rating_entry', methods=["PATCH"])
def update_power_rating_entry(cafe_id):
    data = request.get_json()
    form = CafeForm()
    form.wifi_rating = data["wifi_rating"]
    if form.validate_on_submit():
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(UPDATE_CAFE_POWER_RATING_BY_ID, (cafe_id, power_rating))
            if cursor.rowcount == 0:
                return jsonify({"error": f"Cafe shop with ID {cafe_id} not found."}), 404
        return jsonify({"id": cafe_id, "power_rating": form.power_rating, "message": f"Cafe shop with ID {cafe_id} "
                                                            f"and open : {form.power_rating} updated successfully."})

    return render_template('index.html', form=form)
@app.route("/delete/cafe-shop/<int:cafe_id>", methods=["DELETE"])
def delete_user(cafe_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(DELETE_CAFE_SHOP_BY_ID, (cafe_id,))
            if cursor.rowcount == 0:
                return jsonify({"error": f"User with ID {cafe_id} not found."}), 404
    return jsonify({"message": f"Cafe shop with ID {cafe_id} deleted."})


if __name__ == '__main__':
    app.run(debug=True)