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
- **Cloudinary** for persistent product images and digital files in production.
- **HTML**, **CSS**, and **JavaScript** for the user interface and
  interactions.
- **Three.js** for the interactive 3D demonstration, loaded through an
  import map.

The Django application is located in `shop_project/`. The root
`index.html` and `styles.css` contain the original static interface, while the
integrated catalogue is implemented in `shop_project/catalog/`.

## Cloudinary and Render media storage

Production media uploaded through Django Admin (`ProductImage.image` and
`Product.digital_file`) is stored in Cloudinary. Static files remain served by
WhiteNoise and are not sent to Cloudinary.

1. Create a Cloudinary account and copy the cloud name, API key, and API
   secret from the Cloudinary console.
2. In the Render **Web Service**, add these environment variables (as secret
   values where appropriate):

   ```text
   CLOUDINARY_CLOUD_NAME=<your-cloud-name>
   CLOUDINARY_API_KEY=<your-api-key>
   CLOUDINARY_API_SECRET=<your-api-secret>
   ```

   Do not commit these values or put them in documentation. The three
   variables must be set together; if they are absent, local filesystem media
   storage is used for development, and if only some are set, Django fails
   explicitly at startup.
3. Deploy/restart the Render service after saving the variables. New images and
   digital files uploaded in Django Admin will then use Cloudinary URLs.

Existing files are not copied automatically. Before switching production over,
download the files referenced by the existing database, upload them to the
Cloudinary account, and update each database record/file reference (or
re-upload every file from Django Admin after deployment). Keep the same
database records and verify the public catalogue and digital downloads before
removing any old media files. Cloudinary storage does not replace database
backups, and the free plan's quotas and delivery/access settings still apply.
