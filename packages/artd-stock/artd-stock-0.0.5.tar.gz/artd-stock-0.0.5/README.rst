=================
Stock
=================

A Django app to create product stocks.


Quick start
-----------

1. Add "artd_product" and "artd_stock" to your INSTALLED_APPS setting like this:
    
        INSTALLED_APPS = [
            ...
            'artd_location',
            'artd_product',
            'artd_partner',
            'artd_stock'
        ]

2. Run ``python manage.py migrate`` to create the models.

3. Run ``python manage.py create_taxes`` to create tax types.

4. run ``python manage.py create_countries`` to create the countries.

5. run ``python manage.py create_regions`` to create the regions.

6. run ``python manage.py create_cities`` to create the cities.


7. Start the development server and visit http://127.0.0.1:8000/admin/