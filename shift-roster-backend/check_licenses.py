#!/usr/bin/env python3

from src.models.models import License
from src import create_app

app = create_app()

with app.app_context():
    licenses = License.query.all()
    if licenses:
        print(f'Found {len(licenses)} licenses:')
        for lic in licenses:
            print(f'  - ID: {lic.id}, Name: {lic.name}, Description: {lic.description}')
    else:
        print('No licenses found in database')
        print('Creating sample license...')
        sample_license = License(name="Driver's License", description="Valid driver's license for company vehicles")
        from src.models.models import db
        db.session.add(sample_license)
        db.session.commit()
        print(f'Created sample license with ID: {sample_license.id}')
