import os
from flask import Flask, render_template, request, redirect, flash
from dotenv import load_dotenv
import sys
import requests
from flask_sqlalchemy import SQLAlchemy
import secrets
import datetime


# Flask, SqlAlchemygit  setup
load_dotenv()
secret = secrets.token_urlsafe(32)
app = Flask(__name__)
app.secret_key = secret
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['DEBUG'] = True
db = SQLAlchemy(app)

# API Key for OpenWeatherMap (requires free registration)
API_ID = os.getenv('API_ID')


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return self.name


def get_city_data(city):
    response = requests.get(
        "http://api.openweathermap.org/data/2.5/weather?q={}&APPID={}"
        "&units=metric".format(city, API_ID)).json()
    return response


@app.route('/')
def index():
    dict_with_weather_info = {}
    cities = City.query.all()
    for city in cities:
        response_curr_weather = get_city_data(city)
        response_future_weather = get_detailed_city_data(city)
        if (response_curr_weather['cod'] == '404' or
                response_future_weather['cod'] == '404'):
            flash('city cannot be found')
        name, curr_temp, state, city_id = response_curr_weather['name'], \
            response_curr_weather['main']['temp'], \
            response_curr_weather['weather'][0]['main'], \
            response_curr_weather['id']
        first_day_temp = round(response_future_weather['list'][7]['main']['temp'])
        second_day_temp = round(response_future_weather['list'][15]['main']['temp'])
        third_day_temp = round(response_future_weather['list'][23]['main']['temp'])
        fourth_day_temp = round(response_future_weather['list'][31]['main']['temp'])
        fifth_day_temp = round(response_future_weather['list'][39]['main']['temp'])
        dict_with_weather_info[name.upper()] = {
            'curr_temp': round(curr_temp),
            'curr_state': state,
            'id': city_id,
            'first_day_temp': first_day_temp,
            'second_day_temp': second_day_temp,
            'third_day_temp': third_day_temp,
            'fourth_day_temp': fourth_day_temp,
            'fifth_day_temp': fifth_day_temp
        }
    return render_template('index.html', weather=dict_with_weather_info)


@app.route('/add', methods=['GET', 'POST'])
def add_city():
    if request.method == 'POST':
        city_name = request.form['city_name'].upper()
        exists = db.session.query(
            db.session.query(City).filter_by(name=city_name).exists()
        ).scalar()
        if not exists:
            db.session.add(City(name=city_name))
            db.session.commit()
            flash("city has been successfully added")
        flash("cannot add the same city twice")
        return redirect('/')


@app.route('/<name>', methods=['GET'])
def get_detailed_city_data(city):
    if request.method == 'GET':
        response = requests.get(
            "http://api.openweathermap.org/data/2.5/forecast?q={}&APPID={}"
            "&units=metric".format(city, API_ID)).json()
        # city_name = response['city']['name']
        return response


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
