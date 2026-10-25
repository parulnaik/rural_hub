from flask import Blueprint, current_app, jsonify, render_template, url_for
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models import BarterItem, ScrapItem, Service, User

main = Blueprint('main', __name__)


def _location_coordinates(location):
    fallback = (22.7196, 75.8577)
    if not location:
        return fallback

    city_map = {
        'indore': (22.7196, 75.8577),
        'bhopal': (23.2599, 77.4126),
        'ujjain': (23.1793, 75.7849),
        'ratlam': (23.3307, 75.0423),
        'khargone': (21.8253, 75.6150),
        'neemuch': (24.4877, 74.8687),
        'dewas': (22.9625, 76.0508),
        'mhow': (22.5536, 75.7648),
        'gwalior': (26.2183, 78.1828),
        'jaipur': (26.9124, 75.7873),
        'agra': (27.1767, 78.0081),
        'delhi': (28.6139, 77.2090),
        'mumbai': (19.0760, 72.8777),
    }

    location_text = location.strip().lower()
    for city, coords in city_map.items():
        if city in location_text:
            return coords
    return fallback


@main.route('/health')
def health():
    try:
        db.session.execute(text('SELECT 1'))
    except SQLAlchemyError:
        current_app.logger.exception('Database health check failed')
        return jsonify({
            'status': 'error',
            'service': 'rural-hub',
            'database': 'unavailable',
            'environment': 'production' if __import__('os').environ.get('VERCEL') else 'development'
        }), 503

    return jsonify({
        'status': 'ok',
        'service': 'rural-hub',
        'database': 'connected',
        'environment': 'production' if __import__('os').environ.get('VERCEL') else 'development'
    })


@main.route('/map')
def map_page():
    markers = []

    for item in ScrapItem.query.filter_by(status='active').all():
        lat, lng = _location_coordinates(item.location)
        markers.append({
            'type': 'Scrap',
            'title': item.title,
            'location': item.location,
            'lat': lat,
            'lng': lng,
            'url': url_for('scrap.details', item_id=item.id)
        })

    for service in Service.query.filter_by(status='active').all():
        lat, lng = _location_coordinates(service.location)
        markers.append({
            'type': 'Service',
            'title': service.service_name,
            'location': service.location,
            'lat': lat,
            'lng': lng,
            'url': url_for('services.details', service_id=service.id)
        })

    for item in BarterItem.query.filter_by(status='active').all():
        lat, lng = _location_coordinates(item.location)
        markers.append({
            'type': 'Barter',
            'title': item.title,
            'location': item.location,
            'lat': lat,
            'lng': lng,
            'url': url_for('barter.details', item_id=item.id)
        })

    for user in User.query.filter(User.role.in_(['dealer', 'service_provider'])).all():
        if user.latitude is not None and user.longitude is not None:
            lat, lng = float(user.latitude), float(user.longitude)
        elif user.location:
            lat, lng = _location_coordinates(user.location)
        else:
            continue

        marker_type = 'Dealer' if user.role == 'dealer' else 'Service Provider'
        markers.append({
            'type': marker_type,
            'title': f"{user.name} ({user.role.replace('_', ' ').title()})",
            'location': user.location or 'Location shared by user',
            'lat': lat,
            'lng': lng,
            'url': '#'
        })

    return render_template('main/map.html', markers=markers)


@main.route('/')
def index():
    return render_template('main/index.html')

@main.route('/about')
def about():
    return render_template('main/about.html')

@main.route('/mandi')
def mandi():
    # Mock data for Mandi prices
    prices = [
        {'crop': 'Wheat', 'variety': 'Lokwan', 'min_price': 2100, 'max_price': 2350, 'modal': 2200, 'market': 'Indore'},
        {'crop': 'Soyabean', 'variety': 'Yellow', 'min_price': 4500, 'max_price': 4800, 'modal': 4650, 'market': 'Ujjain'},
        {'crop': 'Maize', 'variety': 'Hybrid', 'min_price': 1800, 'max_price': 2100, 'modal': 1950, 'market': 'Ratlam'},
        {'crop': 'Mustard', 'variety': 'Black', 'min_price': 5200, 'max_price': 5500, 'modal': 5350, 'market': 'Neemuch'},
        {'crop': 'Cotton', 'variety': 'Medium Staple', 'min_price': 6800, 'max_price': 7200, 'modal': 7000, 'market': 'Khargone'}
    ]
    return render_template('main/mandi.html', prices=prices)

@main.route('/weather')
def weather():
    # Mock data for Weather
    forecast = [
        {'day': 'Today', 'temp_max': 32, 'temp_min': 22, 'condition': 'Sunny', 'icon': '☀️'},
        {'day': 'Tomorrow', 'temp_max': 33, 'temp_min': 23, 'condition': 'Partly Cloudy', 'icon': '⛅'},
        {'day': 'Wednesday', 'temp_max': 30, 'temp_min': 21, 'condition': 'Rain Showers', 'icon': '🌧️'},
        {'day': 'Thursday', 'temp_max': 28, 'temp_min': 20, 'condition': 'Thunderstorms', 'icon': '⛈️'},
        {'day': 'Friday', 'temp_max': 29, 'temp_min': 19, 'condition': 'Mostly Sunny', 'icon': '🌤️'}
    ]
    return render_template('main/weather.html', forecast=forecast)

@main.route('/forum')
def forum():
    # Mock data for Community Forum
    posts = [
        {'title': 'Best fertilizer for late-sown wheat?', 'author': 'Ramesh', 'replies': 12, 'time': '2 hours ago'},
        {'title': 'Tractor subsidy scheme details 2024', 'author': 'Suresh', 'replies': 45, 'time': '5 hours ago'},
        {'title': 'Anyone has spare water pump for a day?', 'author': 'Mukesh', 'replies': 3, 'time': '1 day ago'},
        {'title': 'New disease affecting tomato crops in our area', 'author': 'Dr. Sharma', 'replies': 28, 'time': '2 days ago'}
    ]
    return render_template('main/forum.html', posts=posts)
