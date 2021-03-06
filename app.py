from flask import Flask, render_template, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
import sys
import requests
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
db = SQLAlchemy(app)
app.secret_key = os.urandom(32)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f"<City {repr(self.name)}>"


def get_daytime(time, response):
    """
    :param time: timestamp in unix seconds
    :param response: response from weather api
    :return: str day/evening-morning/night
    """
    hr_gap = 1
    if response['sys']['sunrise'] < time <= response['sys']['sunset'] \
            - 3600 * hr_gap:
        return "day"
    # if hr_gap before and after sunrise or hr_gap before after sunset
    elif response['sys']['sunrise'] - 3600 * hr_gap < time < \
        response['sys']['sunrise'] + 3600 * hr_gap or \
            response['sys']['sunset'] - 3600 * hr_gap < time < \
            response['sys']['sunset'] + 3600 * hr_gap:
        return "evening-morning"
    else:
        return "night"


def call_weather_api(city, url, key, units="metric") -> dict:
    """

    :param city: city name
    :param url: url of weather api site
    :param key: API key
    :param units: metric/imperial
    :return: dict{city:response}
             with response
             condition: weather state
             temp: temperature
             time_now: current time UTC
             time_of_day: day state
    """
    params = {'q': city, 'appid': key, 'units': units}
    r = requests.get(url, params=params)
    resp = r.json()
    if not r.raise_for_status():
        time_now = int(datetime.now(timezone.utc).timestamp())
        time_of_day = get_daytime(time_now, resp)
        return {'name': resp['name'], 'condition': resp['weather'][0]['main'],
                'temp': str(resp['main']['temp']),
                'conditions_icon': resp['weather'][0]['icon'],
                'time_now': datetime.fromtimestamp(
                    datetime.now(timezone.utc).timestamp() + resp['timezone'],
                    tz=timezone.utc).strftime("%H : %M"),
                'time_of_day': time_of_day}


@app.route('/', methods=['GET', 'POST'])
def list_cities():
    try:
        session.setdefault('weather_info', [])
        session.setdefault('api_key', os.environ.get('WEATHER_API_KEY'))
        session.setdefault('weather_endpoint',
                           "https://api.openweathermap.org/data/2.5/weather")

        session['weather_info'] = []
        for city in City.query.all():
            session['weather_info'].append(
                {'id': city.id, **call_weather_api(city.name,
                                                   session['weather_endpoint'],
                                                   session['api_key'])})
        app.logger.info(session['weather_info'])

        return render_template('index.html', weather=session['weather_info'])
    except requests.HTTPError as e:
        app.logger.error(str(e))
        if e.response.status_code == 404:
            flash("The city doesn't exist!")
        else:
            flash("Request failure, please try again")

    except requests.RequestException as e:
        app.logger.error(str(e))
        flash("Unable to connect to Weather API site, please try later!")


@app.route('/add', methods=['POST'])
def add_city():
    if request.method == 'POST':
        # Request to check if city name exists
        try:
            session.setdefault('weather_info', [])
            session.setdefault('api_key', os.environ.get('WEATHER_API_KEY'))
            session.setdefault(
                'weather_endpoint',
                "https://api.openweathermap.org/data/2.5/weather")

            resp = call_weather_api(
                request.form['city_name'], session['weather_endpoint'],
                session['api_key'])
            if resp:
                new_city = City(name=request.form['city_name'])
                db.session.add(new_city)
                db.session.commit()

        except IntegrityError as e:
            db.session.rollback()
            app.logger.error(str(e))
            flash('The city has already been added to the list!')

        except requests.HTTPError as e:
            app.logger.error(str(e))
            if e.response.status_code == 404:
                flash("The city doesn't exist!")
            else:
                flash("Request failure, please try again")
        return redirect('/')


@app.route('/delete/<city_id>', methods=['POST'])
def delete(city_id):
    try:
        city = City.query.filter_by(id=city_id).first()
        db.session.delete(city)
        db.session.commit()
    except Exception as e:
        app.logger.error(str(e))
    return redirect('/')


# don't change the following way to run flask:
if __name__ == '__main__':
    try:
        db.create_all()
        if len(sys.argv) > 1:
            arg_host, arg_port = sys.argv[1].split(':')
            app.run(host=arg_host, port=arg_port)
        else:
            app.run(debug=True)
    except Exception as err:
        app.logger.error(err)
