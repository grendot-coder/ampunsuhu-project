import os
import requests
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'vintage-swiss-poster-secret-key'

# Simple user mock database
USERS = {
    'admin': {
        'name': 'Budiyono',
        'role': 'Bapak-bapak from Surabaya',
        'location': 'Darjo, Indonesia',
        'email': 'budiyono@ekonom.id',
        'password': '1234',
        'badge': '17 // CORE'
    }
}

WEATHER_CONDITIONS = {
    0: 'Cerah',
    1: 'Sebagian Besar Cerah',
    2: 'Cerah Berawan',
    3: 'Mendung / Berawan Tebal',
    45: 'Berkabut',
    48: 'Kabut Tebal',
    51: 'Gerimis Ringan',
    53: 'Gerimis Sedang',
    55: 'Gerimis Lebat',
    61: 'Hujan Ringan',
    63: 'Hujan Sedang',
    65: 'Hujan Lebat',
    80: 'Hujan Rintik-rintik',
    81: 'Hujan Cukup Deras',
    82: 'Hujan Sangat Lebat',
    95: 'Hujan Disertai Petir',
    96: 'Badai Petir & Hujan Es Ringan',
    99: 'Badai Petir & Hujan Es Lebat'
}

def get_weather_data(city="Sumberpucung", latitude=-8.1567, longitude=112.4831):
    
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m&hourly=temperature_2m&timezone=auto"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            curr = data.get('current', {})
            code = curr.get('weather_code', 0)
            is_day = curr.get('is_day', 1) == 1
            
            status_text = WEATHER_CONDITIONS.get(code, 'Cerah' if is_day else 'Malam Cerah')
            if not is_day and code == 0:
                status_text = 'Malam Cerah'

            return {
                'city': city,
                'temp': round(curr.get('temperature_2m', 28.0), 1),
                'feels_like': round(curr.get('apparent_temperature', 30.0), 1),
                'humidity': curr.get('relative_humidity_2m', 75),
                'wind': curr.get('wind_speed_10m', 6.5),
                'status': status_text,
                'success': True
            }
    except Exception as e:
        print(f"Weather API Error: {e}")
    
    # Fallback default jika offline
    return {
        'city': city,
        'temp': 9.10,
        'feels_like': 21.0,
        'humidity': 67,
        'wind': 8.0,
        'status': 'Kabut Asap(Offline)',
        'success': False
    }

def search_city_coordinates(query):
    """Search coordinates for any city worldwide using Open-Meteo Geocoding API"""
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=1&language=id&format=json"
        res = requests.get(geo_url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            results = data.get('results')
            if results and len(results) > 0:
                first = results[0]
                city_name = first.get('name')
                country = first.get('country', '')
                display_name = f"{city_name}, {country}" if country else city_name
                return first.get('latitude'), first.get('longitude'), display_name
    except Exception as e:
        print(f"Geocoding Error: {e}")
    return None, None, None

@app.route('/')
@app.route('/dashboard')
def dashboard():
    weather = get_weather_data('Sumberpucung', -8.1567, 112.4831)
    return render_template('dashboard.html', weather=weather)

@app.route('/temperature', methods=['GET'])
def temperature():
    search_query = request.args.get('search', '').strip()
    city = request.args.get('city', 'Sumberpucung')
    
    preset_cities = {
        'Sumberpucung': (-8.1567, 112.4831),
        'Kepanjen': (-8.1306, 112.5714),
        'Malang': (-7.9797, 112.6304),
        'Surabaya': (-7.2575, 112.7521),
        'Yogyakarta': (-7.7956, 110.3695),
        'Kesamben': (-8.1333, 112.3333)
    }

    error_msg = None

    if search_query:
        lat, lon, found_name = search_city_coordinates(search_query)
        if lat is not None and lon is not None:
            city = found_name
            weather = get_weather_data(city, lat, lon)
        else:
            error_msg = f'Lokasi "{search_query}" tidak ditemukan.'
            lat, lon = preset_cities['Sumberpucung']
            weather = get_weather_data('Sumberpucung', lat, lon)
            city = 'Sumberpucung'
    else:
        lat, lon = preset_cities.get(city, preset_cities['Sumberpucung'])
        weather = get_weather_data(city, lat, lon)

    return render_template('temperature.html', weather=weather, selected_city=city, cities=list(preset_cities.keys()), error=error_msg)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('username'):
        return redirect(url_for('dashboard'))
    
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = USERS.get(username)
        if user and user['password'] == password:
            session['username'] = username
            return redirect(url_for('profile'))
        error = 'Kredensial tidak cocok. Silakan periksa kembali username & password.'
    return render_template('login.html', error=error)

@app.route('/profile')
def profile():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    user_info = USERS.get(username, {
        'name': username,
        'role': 'Guest Explorer',
        'location': 'Indonesia',
        'email': f'{username}@domain.com',
        'badge': '01 // ARCHIVE'
    })
    return render_template('profile.html', user=user_info)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)