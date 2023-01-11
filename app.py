from flask import Flask, render_template, request, redirect
import sys
import requests
from flask_sqlalchemy import SQLAlchemy

# Flask, SqlAlchemy setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['DEBUG'] = True
db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return self.name


# API Key for OpenWeatherMap (requires free registration)
API_ID = '6db2423a8fba1d1de7cbc8057328717d'


@app.route('/')
def index():
    dict_with_weather_info = {}
    cities = City.query.all()
    for city in cities:
        response = requests.get(
            "http://api.openweathermap.org/data/2.5/weather?q={}&APPID={}&units=metric".format(city, API_ID))
        name, temp, state, city_id = response.json()['name'], \
            response.json()['main']['temp'], \
            response.json()['weather'][0]['main'], \
            response.json()['id']
        dict_with_weather_info[name.upper()] = {'temp': round(temp), 'state': state, 'id': city_id}
    return render_template('index.html', weather=dict_with_weather_info)


@app.route('/add', methods=['GET', 'POST'])
def add_city():
    if request.method == 'POST':
        city_name = request.form['city_name'].upper()
        db.session.add(City(name=city_name))
        db.session.commit()
        return redirect('/')


@app.route('/delete/<name>', methods=['POST'])
def remove_city(name):
    if request.method == 'POST':
        city = City.query.filter_by(name=name).first()
        db.session.delete(city)
        db.session.commit()
        return redirect('/')

# Flask app startup
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
