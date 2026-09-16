# 3D Design and Printing Website

This project is a catalogue website for presenting original 3D designs and
printed products. Visitors can choose between downloadable digital files and
finished physical pieces, view product details and images, and contact the shop
about orders, quotes, or custom work.

## Features

- Public catalogue of active products, ordered according to the catalogue
  configuration.
- Separate presentation for digital files and printed items.
- Product details tailored to each type: print time and weight for digital
  products, or material and lead time for physical products.
- Product image galleries with an enlarged modal viewer.
- Product pricing and download or order actions.
- Contact form for quote requests, orders, and custom products.
- Django administration for managing products, product images, and contact
  requests.
- About section describing the design and 3D-printing focus.
- Animated 3D Benchy demonstration powered by Three.js.

## Technologies

- **Python** and **Django 5** for the web application, routing, data models,
  catalogue, contact handling, and administration.
- **SQLite** for the application database.
- **Pillow** for product image support.
- **HTML**, **CSS**, and **JavaScript** for the user interface and
  interactions.
- **Three.js** for the interactive 3D demonstration, loaded through an
  import map.

The Django application is located in `shop_project/`. The root
`index.html` and `styles.css` contain the original static interface, while the
integrated catalogue is implemented in `shop_project/catalog/`.

## Render deployment

Use the following Render build command so dependencies are installed, the
database migrations run, and static files are collected for WhiteNoise:

```text
pip install -r shop_project/requirements.txt && python shop_project/manage.py migrate && python shop_project/manage.py collectstatic --noinput
```
