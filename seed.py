from app import create_app, db
from app.models.service import Service

app = create_app()

with app.app_context():
    # Clear existing data
    Service.query.delete()

    # Add test services
    services = [
        Service(
            name='Haircut',
            duration_mins=60,
            price=45.00,
            description='Classic haircut and style',
            is_active=True
        ),
        Service(
            name='Colour Treatment',
            duration_mins=120,
            price=120.00,
            description='Full colour treatment',
            is_active=True
        ),
        Service(
            name='Event Styling',
            duration_mins=90,
            price=80.00,
            description='Styling for special occasions',
            is_active=True
        ),
    ]

    db.session.add_all(services)
    db.session.commit()
    print(f'Added {len(services)} services.')