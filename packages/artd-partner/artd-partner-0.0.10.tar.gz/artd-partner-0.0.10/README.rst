=================
Partner
=================

A Django app to create partners.


Quick start
-----------
1. Install artd_location and add to your INSTALLED_APPS like this:
    
        INSTALLED_APPS = [
            ...
            'artd_location',
            'artd_partner',
        ]

2. Run ``python manage.py migrate`` to create the models.

3. run ``python manage.py create_countries`` to create the countries.

4. run ``python manage.py create_regions`` to create the regions.

5. run ``python manage.py create_cities`` to create the cities.

6. Start the development server and visit http://127.0.0.1:8000/admin/