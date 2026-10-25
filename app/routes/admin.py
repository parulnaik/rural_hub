from flask import Blueprint, render_template
from flask_login import login_required
from app.models import User, ScrapItem, Bid, Service, ServiceBooking, BarterItem
from app.utils import role_required

admin = Blueprint('admin', __name__)

@admin.route('/')
@login_required
@role_required('admin')
def index():
    stats = {
        'total_users': User.query.count(),
        'total_dealers': User.query.filter_by(role='dealer').count(),
        'total_providers': User.query.filter_by(role='service_provider').count(),
        'active_scrap': ScrapItem.query.filter_by(status='active').count(),
        'total_bids': Bid.query.count(),
        'total_services': Service.query.count(),
        'total_bookings': ServiceBooking.query.count(),
        'active_barter': BarterItem.query.filter_by(status='active').count(),
    }
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('dashboards/admin.html', stats=stats, recent_users=recent_users)
