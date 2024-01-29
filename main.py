import random
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, asc

app = Flask(__name__)

Bootstrap5(app)
app.config['SECRET_KEY'] = 'sdsdsdsdsdsdsdsdsdsd'
# Connect to Database:
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///cafes.db"
db = SQLAlchemy()
db.init_app(app)

MY_PLACE = ''

# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)
    likes = db.Column(db.Boolean, nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route('/', methods=["GET", "POST"])
def home():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    return render_template('index.html', all=all_cafes)


@app.route("/random", methods=["GET", "POST"])
def random_cafe():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    random_choice = random.choice(all_cafes).to_dict()
    return jsonify(cafe=random_choice)


@app.route("/wifi-<name>", methods=["GET", "POST"])
def filtering(name):
    print(name)
    global MY_PLACE

    result = db.session.execute(db.select(Cafe))

    if name == 'wifi':
        result = db.session.execute(db.select(Cafe).where(Cafe.has_wifi == 1))
        print(request.url)
    elif name == "sockets":
        result = db.session.execute(db.select(Cafe).where(Cafe.has_sockets == 1))

    elif name == "can_make_call":
        result = db.session.execute(db.select(Cafe).where(Cafe.can_take_calls == 1))
    elif name == "seat":
        result = db.session.execute(db.select(Cafe).order_by(desc(Cafe.seats)))
    elif name == "less_price":
        result = db.session.execute(db.select(Cafe).order_by(asc(Cafe.coffee_price)))
    elif name == "high_price":
        result = db.session.execute(db.select(Cafe).order_by(desc(Cafe.coffee_price)))
    elif name == "restroom":
        result = db.session.execute(db.select(Cafe).where(Cafe.has_toilet == 1))
    elif name == "my_place":
        result = db.session.execute(db.select(Cafe).where(Cafe.likes == 1))
        MY_PLACE = 'http://127.0.0.1:3001/wifi-my_place'

        if not result.all():
            flash("Sorry, there is not any liked Place.")
            MY_PLACE = ''
            return redirect(url_for('home'))
        else:
            result = db.session.execute(db.select(Cafe).where(Cafe.likes == 1))

    if request.method == 'POST':
        if name == "search":
            result = db.session.execute(
                db.select(Cafe).where(Cafe.name.like(f'%{request.form.get("search")}%')))
        # if result == " ":
        #     print("dosent exixt")

    all_cafes = result.scalars().all()

    # db.session.query(Cafe).filter(Cafe.name.ilike(f'%{request.form.get('search')}%')).all()
    return render_template('index.html', all=all_cafes)


@app.route('/reset')
def dell_filters():
    global MY_PLACE
    MY_PLACE = ''
    return redirect(url_for('home'))


@app.route("/like<int:cafe_id>")
def like(cafe_id):
    db.get_or_404(Cafe, cafe_id).likes = 1
    db.session.commit()
    return redirect(f'/#{cafe_id}')


@app.route("/unlike<int:cafe_id>")
def unlike(cafe_id):
    global MY_PLACE
    db.get_or_404(Cafe, cafe_id).likes = 0
    db.session.commit()
    if MY_PLACE == 'http://127.0.0.1:3001/wifi-my_place':
        return redirect(f'/wifi-my_place#{cafe_id}')
    return redirect(f'/#{cafe_id}')


@app.route("/new_cafe", methods=['GET', 'POST'])
def new_cafe():
    if request.method == 'POST':
        new = Cafe(
            name=request.form.get('name'),
            map_url=request.form.get('map_url'),
            img_url=request.form.get('img_url'),
            location=request.form.get('location'),
            seats=request.form.get('seats'),
            has_toilet=bool(request.form.get('has_toilet')),
            has_wifi=bool(request.form.get('has_wifi')),
            has_sockets=bool(request.form.get('has_sockets')),
            can_take_calls=bool(request.form.get('can_take_calls')),
            coffee_price=request.form.get('coffee_price'),
            likes=0
        )
        db.session.add(new)
        db.session.commit()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(port=3001, debug=True)
