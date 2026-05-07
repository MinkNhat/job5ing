from app import create_app, db
from seed import seed_data
import os
import sys

def run_seed():
    app = create_app()
    
    with app.app_context():
        try:
            # Delete existing data and create new tables
            db.drop_all()
            db.create_all()
            
            # Run seed
            result = seed_data()
            if result is False:
                print("Database already has data")
            else:
                db.session.commit()
                print("Database seeding completed successfully")
                
        except Exception as e:
            print(f"Error: {str(e)}")
            db.session.rollback()
            sys.exit(1)

if __name__ == "__main__":
    run_seed()
