from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Service, ServiceBooking, User, Favorite
from app import db
from app.utils import role_required
from datetime import datetime

services = Blueprint('services', __name__)

@services.route('/')
def index():
    # Filter functionality
    category = request.args.get('category')
    location = request.args.get('location')
    
    query = Service.query.filter_by(status='active')
    
    if location:
        query = query.filter(Service.location.ilike(f'%{location}%'))
        
    items = query.order_by(Service.created_at.desc()).all()
    return render_template('services/index.html', services=items)

@services.route('/<int:service_id>')
def details(service_id):
    service = Service.query.get_or_404(service_id)
    is_favorite = False
    if current_user.is_authenticated:
        is_favorite = Favorite.query.filter_by(user_id=current_user.id, item_type='service', item_id=service.id).first() is not None
    return render_template('services/details.html', service=service, is_favorite=is_favorite)

@services.route('/add', methods=['GET', 'POST'])
@login_required
@role_required(['service_provider', 'admin'])
def add():
    if request.method == 'POST':
        service_name = request.form.get('service_name')
        description = request.form.get('description')
        price = request.form.get('price')
        location = request.form.get('location')
        availability = request.form.get('availability')
        
        if not all([service_name, description, price, location, availability]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('services.add'))
            
        try:
            price = float(price)
            if price < 0:
                raise ValueError
        except (TypeError, ValueError):
            flash('Invalid price.', 'danger')
            return redirect(url_for('services.add'))
            
        new_service = Service(
            provider_id=current_user.id,
            service_name=service_name,
            description=description,
            price=price,
            location=location,
            availability=availability
        )
        
        db.session.add(new_service)
        db.session.commit()
        
        flash('Service added successfully!', 'success')
        return redirect(url_for('services.details', service_id=new_service.id))
        
    return render_template('services/add.html')

@services.route('/<int:service_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(service_id):
    service = Service.query.get_or_404(service_id)
    favorite = Favorite.query.filter_by(user_id=current_user.id, item_type='service', item_id=service.id).first()

    if favorite:
        db.session.delete(favorite)
        flash('Removed from your favorites.', 'info')
    else:
        db.session.add(Favorite(user_id=current_user.id, item_type='service', item_id=service.id))
        flash('Added to your favorites.', 'success')

    db.session.commit()
    return redirect(request.referrer or url_for('services.details', service_id=service_id))


@services.route('/<int:service_id>/book', methods=['POST'])
@login_required
def book(service_id):
    service = Service.query.get_or_404(service_id)
    
    if service.provider_id == current_user.id:
        flash('You cannot book your own service.', 'danger')
        return redirect(url_for('services.details', service_id=service_id))
        
    booking_date_str = request.form.get('booking_date')
    if not booking_date_str:
        flash('Booking date is required.', 'danger')
        return redirect(url_for('services.details', service_id=service_id))
        
    try:
        booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d')
    except ValueError:
        flash('Invalid date format.', 'danger')
        return redirect(url_for('services.details', service_id=service_id))
        
    new_booking = ServiceBooking(
        service_id=service.id,
        customer_id=current_user.id,
        booking_date=booking_date
    )
    
    db.session.add(new_booking)
    db.session.commit()
    
    flash('Service booked successfully! Waiting for provider approval.', 'success')
    return redirect(url_for('dashboards.index'))
