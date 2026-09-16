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
- **PostgreSQL** in production on Render, selected through `DATABASE_URL`.
  SQLite remains the local-development default when `DATABASE_URL` is absent.
- **Pillow** for product image support.
- **HTML**, **CSS**, and **JavaScript** for the user interface and
  interactions.
- **Three.js** for the interactive 3D demonstration, loaded through an
  import map.

The Django application is located in `shop_project/`. The root
`index.html` and `styles.css` contain the original static interface, while the
integrated catalogue is implemented in `shop_project/catalog/`.

## Render deployment

For the normal deployment, use the following Render build command so
dependencies are installed, the database migrations run, and static files are
collected for WhiteNoise:

```text
pip install -r shop_project/requirements.txt && python shop_project/manage.py migrate && python shop_project/manage.py collectstatic --noinput
```

### Temporary first-admin setup

Render Free does not provide an interactive Shell. To create the first Django
administrator, temporarily add these three environment variables to the Web
Service:

- `DJANGO_ADMIN_USERNAME`
- `DJANGO_ADMIN_EMAIL`
- `DJANGO_ADMIN_PASSWORD`

Use a strong, temporary password and do not commit it to the repository. While
those variables are present, temporarily change the Render build command to:

```text
pip install -r shop_project/requirements.txt && python shop_project/manage.py migrate && python shop_project/manage.py ensure_admin && python shop_project/manage.py collectstatic --noinput
```

After the deploy finishes, sign in to `/admin/` with the configured username
and password and change the password immediately. Then remove all three
`DJANGO_ADMIN_*` variables from Render and restore the normal build command
above. The command is safe to run repeatedly and makes no changes when the
variables are absent, but remove `shop_project/catalog/management/commands/ensure_admin.py`
and its package files from the repository after the first successful login if
this temporary mechanism is no longer needed.

Use this start command:

```text
gunicorn --chdir shop_project shop_project.wsgi:application
```

Set `DATABASE_URL` to the internal PostgreSQL URL provided by Render. Also set
`DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS`, and
`DJANGO_CSRF_TRUSTED_ORIGINS` for production. If `DATABASE_URL` is not set,
the project intentionally uses local SQLite instead of attempting PostgreSQL.
