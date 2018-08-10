The `_prod` folder contains a directory tree with production copies of all `.env` files.

Since `.env` files are not remote sync'd by Atom (see `.remote-sync.json`) the `_scripts/update_env.sh` script can be used to push/distribute all `_prod/*/.env` files to the production server.
