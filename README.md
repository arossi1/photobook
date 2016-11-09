# photobook

PhotoBook is a collection of components that catalogs / indexes unorganized directories of images to a database and exposes an interface for viewing, exploitation, and administration.  The back-end is written in Python, with a HTML/Javascript front-end UI.

Dependencies:
- Python 2.7
- peewee

The indexer has the following features:
- create Catalog (name, description, path)
- recursively searches catalog path for files / images with a defined image extension (e.g., .jpg)
- a hash is computed for each image to aid in duplication identification
- can be run on pre-existing Catalog for updates over time
  - update will add new images and mark records / images that have been deleted as "no longer existing" in the db