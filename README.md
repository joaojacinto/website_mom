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
- Password recovery for admin users through Django's standard reset flow.
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

Use this Build Command for the Render web service:

```text
pip install -r shop_project/requirements.txt && python shop_project/manage.py migrate && python shop_project/manage.py collectstatic --noinput
```

### Admin password recovery with Resend

The reset flow is available at `/accounts/password_reset/` and is also linked
from the Django admin login. Without an API key, local development uses
Django's console email backend. To send real email on Render, add these
environment variables to the web service:

| Variable | Value |
| --- | --- |
| `RESEND_API_KEY` | API key created in the Resend dashboard |
| `RESEND_FROM_EMAIL` | Optional verified sender address in Resend |
| `DEFAULT_FROM_EMAIL` | Verified sender address in Resend, used when `RESEND_FROM_EMAIL` is absent |

When `RESEND_API_KEY` is set, password-reset messages use the Resend HTTPS API.
The sender must be a verified domain or address in Resend. Never commit API
keys or put secret values in the README. `EMAIL_TIMEOUT` may optionally be set
to a positive number of seconds (default `15`).

Resend's Free plan currently includes 3,000 transactional emails per month,
with a hard limit of 100 emails per day, up to 3 domains, ticket support, and
30-day data retention. Messages can only be sent from verified senders.
Resend may change plan limits; check the Resend dashboard before production
use.
