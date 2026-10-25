from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from app.models import ScrapItem, Bid, Favorite
from app import db
from app.utils import upload_image, role_required

scrap = Blueprint('scrap', __name__)

@scrap.route('/')
def index():
    # Show active scrap listings
    items = ScrapItem.query.filter_by(status='active').order_by(ScrapItem.created_at.desc()).all()
    return render_template('scrap/index.html', items=items)

@scrap.route('/<int:item_id>')
def details(item_id):
    item = ScrapItem.query.get_or_404(item_id)
    bids = Bid.query.filter_by(item_id=item_id).order_by(Bid.bid_amount.desc()).all()
    highest_bid = bids[0] if bids else None
    is_favorite = False
    if current_user.is_authenticated:
        is_favorite = Favorite.query.filter_by(user_id=current_user.id, item_type='scrap', item_id=item.id).first() is not None
    return render_template('scrap/details.html', item=item, bids=bids, highest_bid=highest_bid, is_favorite=is_favorite)

@scrap.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    # Any authenticated user can add scrap, typically 'user' role
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        description = request.form.get('description')
        quantity = request.form.get('quantity')
        location = request.form.get('location')
        image = request.files.get('image')
        
        if not title or not category or not quantity or not location:
            flash('Required fields are missing.', 'danger')
            return redirect(url_for('scrap.add'))
            
        image_url = None
        if image and image.filename != '':
            image_url = upload_image(image)
            if not image_url:
                flash('Image upload failed. Please try a valid image file.', 'danger')
                return redirect(url_for('scrap.add'))
                
        new_item = ScrapItem(
            user_id=current_user.id,
            title=title,
            category=category,
            description=description,
            quantity=quantity,
            location=location,
            image_url=image_url
        )
        
        db.session.add(new_item)
        db.session.commit()
        
        flash('Scrap item added successfully!', 'success')
        return redirect(url_for('scrap.details', item_id=new_item.id))
        
    return render_template('scrap/add.html')

@scrap.route('/<int:item_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(item_id):
    item = ScrapItem.query.get_or_404(item_id)
    favorite = Favorite.query.filter_by(user_id=current_user.id, item_type='scrap', item_id=item.id).first()

    if favorite:
        db.session.delete(favorite)
        flash('Removed from your favorites.', 'info')
    else:
        db.session.add(Favorite(user_id=current_user.id, item_type='scrap', item_id=item.id))
        flash('Added to your favorites.', 'success')

    db.session.commit()
    return redirect(request.referrer or url_for('scrap.details', item_id=item_id))


@scrap.route('/<int:item_id>/bid', methods=['POST'])
@login_required
@role_required(['dealer', 'admin'])
def place_bid(item_id):
    item = ScrapItem.query.get_or_404(item_id)
    
    if item.status != 'active':
        flash('This listing is closed for bidding.', 'danger')
        return redirect(url_for('scrap.details', item_id=item_id))
        
    if item.user_id == current_user.id:
        flash('You cannot bid on your own listing.', 'danger')
        return redirect(url_for('scrap.details', item_id=item_id))
        
    try:
        bid_amount = float(request.form.get('bid_amount'))
        if bid_amount <= 0:
            raise ValueError
    except (TypeError, ValueError):
        flash('Invalid bid amount.', 'danger')
        return redirect(url_for('scrap.details', item_id=item_id))
        
    new_bid = Bid(
        item_id=item.id,
        dealer_id=current_user.id,
        bid_amount=bid_amount
    )
    
    db.session.add(new_bid)
    db.session.commit()
    
    flash('Bid placed successfully!', 'success')
    return redirect(url_for('scrap.details', item_id=item_id))

@scrap.route('/<int:item_id>/close', methods=['POST'])
@login_required
def close_listing(item_id):
    item = ScrapItem.query.get_or_404(item_id)
    if item.user_id != current_user.id and current_user.role != 'admin':
        abort(403)
        
    item.status = 'closed'
    
    # Accept the highest bid (if any) or a specific one if passed
    accepted_bid_id = request.form.get('accepted_bid_id')
    if accepted_bid_id:
        bid = Bid.query.get(accepted_bid_id)
        if bid and bid.item_id == item.id:
            bid.status = 'accepted'
            
    db.session.commit()
    flash('Listing closed successfully.', 'success')
    return redirect(url_for('scrap.details', item_id=item_id))
