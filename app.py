from flask import Flask, render_template, request
import sys
import requests


app = Flask(__name__)
API_ID = ''

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add', methods=['GET', 'POST'])
def add_city():
    if request.method == 'POST':
        city_name = request.form['city_name']
        response = requests.get("http://api.openweathermap.org/data/2.5/weather?q={}&APPID={}&units=metric".format(city_name, API_ID))
        name, temp, state = response.json()['name'], response.json()['main']['temp'], response.json()['weather'][0]['main']
        dict_with_weather_info = {name.upper(): {'temp': round(temp), 'state': state}}
        return render_template('index.html', weather=dict_with_weather_info)


# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
