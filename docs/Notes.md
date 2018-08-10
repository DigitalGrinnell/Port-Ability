# README.md

What follows is a chronicle of my efforts to build SummittServices.com, a Dockerized orchestration of Drupal 7 and Drupal 8 sites in production on my Digital Ocean droplet.  The process was one of trial and error (mostly error) but in this document I've tried to remove all the gory detail of failed attempts, keeping only a few warnings about what NOT to do in the future, along with details of what ultimately worked.

## Goal Statement


## Following https://wodby.com/stacks/drupal/docs/local/quick-start/ Option 2

The intent here is to build a working D4D structure with one website per Drupal so that certs can be properly assigned.  Apparently, https:// certs will NOT work in a Drupal multi-site environment with different domain names assigned to the sites.

Atom's _remote_sync_ package is being used (defined in _.remote-sync.json_) to sync modifications between my MacBook Air (DEV) and my Digital Ocean droplet (PROD).

### On DEV and PROD as _centos_
#### Clean up
```
destroy-all  
docker network ls   
docker network rm _3-character-id_  
```
...repeat last command as necessary...  

#### On DEV - Option 2: Mount my Drupal Codebase

##### Step 1.
```
cd ~/Projects/Docker/SS
mkdir _d4d
wget https://github.com/wodby/docker4drupal/releases/download/5.0.6/docker4drupal.tar.gz
tar -xzf docker4drupal.tar.gz
```

##### Step 2.
Done

##### Step 3.
Built out the following project structure for the _Wieting_ site (and more to come later)...

```
SS  
|--_d4d  
|--_docs  
|--_sites
   |--wieting
      |--html
      |--mariadb-init  
      |--resources  
```
The _Wieting_ codebase is in the _html_ folder above.

Copy `.env`, `docker-compose.yml` and `traefik.yml` from the *_d4d* folder to *_sites/wieting*.

Working in *_sites/wieting* I modified values in _.env_ and matched them with values in `html/web/sites/wieting/settings.php`.

##### Step 4.
Working in *_sites/wieting* I modified values in _.env_ changing the _PROJECT_BASE_URL_ to include multiple values.  I also modified _docker-compose.yml_ changing port 8000 references to port 80, and _version:_ from '2' to '3'.  

Made sure host entries in _/etc/hosts_ match those in *PROJECT_BASE_URL*.  

##### Step 5.
Skipped

##### Step 6.
Uncommented the `volumes: | - ./mariadb-init` line in the _mariadb_ portion of _docker-compose.yml_.  The _Wieting's_ .sql files are already in the _mariadb-init_ folder.

##### Step 7.
Skipped

##### Step 8.
Using `-dev-macos` version of PHP_TAG in _docker-compose.yml_.

##### Step 9.
Irrelevant...skipped.

##### Step 10.
Performing `docker-compose up -d` on MacBook Air from the _wieting_ folder...FAILED to produce the site. So...

## restart.sh
I created the _restart.sh_ script in the *_scripts/* folder to assist with starting, or re-starting, a single site and it's containers.  

It works!  Trying `restart --wieting` enabled me to spin up a single instance of the Wieting web site.

## Adding a New Site
So, the process is intended to be pretty simple...  

1) Create a new *_sites/???* folder like *_sites/admin*.  
2) Copy the contents of a working site, like *_sites/wieting* (note that Wieting is a Drupal 8 site) to the new *_sites/???* folder.  
3) In the new <site> folder, review and as necessary make changes to the following files at a minimum...  

    .env
    _prod/_sites/<site>/.env
    html/web/sites/sites.php
    html/web/sites/<site>/settings.php
    mariadb-init/sql-dump*.sql
    mariadb-init/sql.header
    resources/<site>.aliases.drushrc.php
    main.yml

And it really, really works...even in production!    

## Making Multi-Site Work
My attempts to build a Drupal 7/8 combination of multi-sites failed because of SSL/TLS requirements... one cert per server/domain, period.  So I've returned to a different kind of multi-site arrangment, deploying one 'stack' of containers per site, fronted by a Traefik and Portainer pair of containers.  Each 'stack' condists of a `<site>_mariadb` container, plus a `<site>_php` container, and a `<site>_nginx` container and corresponding networks.

So now, when you invoke the `restart.sh` script the target site(s) is created along with a `main` stack that includes Traefik and Portainer.

Each `<site>_nginx` container references the site's own `certs` folder where a pair of `cert.pem` and `key.pem` files are held.

## Adding _Let's Encrypt_ Trusted Certs to Production

Following https://www.humankode.com/ssl/how-to-set-up-free-ssl-certificates-from-lets-encrypt-using-docker-and-nginx on my Digital Ocean droplet...

Wherever any `sudo docker-compose up -d` is used I have to substitute...   
```
sudo `which docker-compose` up -d
```
...because _docker-compose_ won't run for the _centos_ user in 'sudo'.

My command sequence for _summittservices.com_ and _admin.summittservices.com_...

```
sudo docker run -it --rm \
-v /docker-volumes/etc/letsencrypt:/etc/letsencrypt \
-v /docker-volumes/var/lib/letsencrypt:/var/lib/letsencrypt \
-v /docker/letsencrypt-docker-nginx/src/letsencrypt/letsencrypt-site:/data/letsencrypt \
-v "/docker-volumes/var/log/letsencrypt:/var/log/letsencrypt" \
certbot/certbot \
certonly --webroot \
--register-unsafely-without-email --agree-tos \
--webroot-path=/data/letsencrypt \
--staging \
-d summittservices.com -d admin.summittservices.com
```

...returned a successful staging request.  Then, this command...

```
sudo docker run --rm -it --name certbot \
-v /docker-volumes/etc/letsencrypt:/etc/letsencrypt \
-v /docker-volumes/var/lib/letsencrypt:/var/lib/letsencrypt \
-v /docker/letsencrypt-docker-nginx/src/letsencrypt/letsencrypt-site:/data/letsencrypt \
certbot/certbot \
--staging \
certificates
```
...successfully reported that the _summittservices.com_ cert was found.

So I cleaned up the staging artifacts using...

```
sudo rm -rf /docker-volumes/
```
Then requested a new live certificate (not staging)...
```
sudo docker run -it --rm \
-v /docker-volumes/etc/letsencrypt:/etc/letsencrypt \
-v /docker-volumes/var/lib/letsencrypt:/var/lib/letsencrypt \
-v /docker/letsencrypt-docker-nginx/src/letsencrypt/letsencrypt-site:/data/letsencrypt \
-v "/docker-volumes/var/log/letsencrypt:/var/log/letsencrypt" \
certbot/certbot \
certonly --webroot \
--email admin@summittservices.com --agree-tos --no-eff-email \
--webroot-path=/data/letsencrypt \
-d summittservices.com -d admin.summittservices.com
```
Success!  The command returned...
```
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Plugins selected: Authenticator webroot, Installer None
Obtaining a new certificate
Performing the following challenges:
http-01 challenge for summittservices.com
http-01 challenge for admin.summittservices.com
Using the webroot path /data/letsencrypt for all unmatched domains.
Waiting for verification...
Cleaning up challenges

IMPORTANT NOTES:
 - Congratulations! Your certificate and chain have been saved at:
   /etc/letsencrypt/live/summittservices.com/fullchain.pem
   Your key file has been saved at:
   /etc/letsencrypt/live/summittservices.com/privkey.pem
   Your cert will expire on 2018-09-15. To obtain a new or tweaked
   version of this certificate in the future, simply run certbot
   again. To non-interactively renew *all* of your certificates, run
   "certbot renew"
 - Your account credentials have been saved in your Certbot
   configuration directory at /etc/letsencrypt. You should make a
   secure backup of this folder now. This configuration directory will
   also contain certificates and private keys obtained by Certbot so
   making regular backups of this folder is ideal.
 - If you like Certbot, please consider supporting our work by:

   Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
   Donating to EFF:                    https://eff.org/donate-le
```

Next, I stopped the temporary Nginx service using...
```
cd /docker/letsencrypt-docker-nginx/src/letsencrypt
sudo `which docker-compose` down
```

### Assumptions

Ok, the post I'm following seems to assume that the production site's root is in `/docker/letsencrypt-docker-nginx/src/production`, and that there is a `docker-compose.yml` file there. Therefore, I believe my substitution should make changes like so:
`/docker/letsencrypt-docker-nginx/src/production` -> `${PROJECT_PATH}`  

The `production-nginx-container` defined in the guide's _docker-compose.yml_ file needs to replace the `nginx` service defined in the site's `_sites/admin/docker-compose.yml` file.  Since `production-nginx-container` does not use Wodby's customized Nginx image, it simply uses `nginx:latest`, it will need to look more like the `production-nginx-container` definition than my original.

I believe that _admin_'s `nginx` service should be defined like so:

```
  nginx:  
    container_name: "${PROJECT_NAME}_nginx"
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./production.conf:/etc/nginx/conf.d/default.conf
#      - ./html:/var/www/html  
      - ./dh-param/dhparam-2048.pem:/etc/ssl/certs/dhparam-2048.pem
      - /docker-volumes/etc/letsencrypt/live/summittservices.com/fullchain.pem:/etc/letsencrypt/live/summittservices.com/fullchain.pem
      - /docker-volumes/etc/letsencrypt/live/summittservices.com/privkey.pem:/etc/letsencrypt/live/summittservices.com/privkey.pem
    labels:
      - 'traefik.backend=${PROJECT_NAME}_nginx'
      - 'traefik.port=80'
      - 'traefik.frontend.rule=Host:${PROJECT_FULL_URL}'
    networks:
      - docker-network
```     

To accommodate this change we should also up the _version_ of the _docker-compose.yml_ file to `3.1`, and add the `networks: | docker-network` specification to `main.yml` (which also should be bumped up to version `3.1`).

And the all-important `production.conf` file should exist next to the site's `docker-compose.yml` and look like so:

```
server {
    listen      80;
    listen [::]:80;
    server_name summittservices.com admin.summittservices.com;

    location ^~ /.well-known/acme-challenge {
        root   /var/www/html/web;
        default_type text/plain;
        allow all;
    }

    location / {
        rewrite ^ https://$host$request_uri? permanent;
    }
}

#https://summittservices.com
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name summittservices.com;

    server_tokens off;

    ssl_certificate /etc/letsencrypt/live/summittservices.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/summittservices.com/privkey.pem;

    ssl_buffer_size 8k;

    ssl_dhparam /etc/ssl/certs/dhparam-2048.pem;

    ssl_protocols TLSv1.2 TLSv1.1 TLSv1;
    ssl_prefer_server_ciphers on;

    ssl_ciphers ECDH+AESGCM:ECDH+AES256:ECDH+AES128:DH+3DES:!ADH:!AECDH:!MD5;

    ssl_ecdh_curve secp384r1;
    ssl_session_tickets off;

    # OCSP stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8;

    location ^~ /.well-known/acme-challenge {
        root   /var/www/html/web;
        default_type text/plain;
        allow all;
    }

    return 301 https://admin.summittservices.com$request_uri;
}

#https://admin.summittservices.com
server {
    server_name admin.summittservices.com;
    listen 443 ssl http2;
    listen [::]:443 ssl http2;

    server_tokens off;

    ssl on;

    ssl_buffer_size 8k;
    ssl_dhparam /etc/ssl/certs/dhparam-2048.pem;

    ssl_protocols TLSv1.2 TLSv1.1 TLSv1;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDH+AESGCM:ECDH+AES256:ECDH+AES128:DH+3DES:!ADH:!AECDH:!MD5;

    ssl_ecdh_curve secp384r1;
    ssl_session_tickets off;

    # OCSP stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4;

    ssl_certificate /etc/letsencrypt/live/summittservices.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/summittservices.com/privkey.pem;

    location ^~ /.well-known/acme-challenge {
        root   /usr/share/nginx/html;
        default_type text/plain;
        allow all;
    }

    root /var/www/html/web;
    index index.php;
}
```
Next we make a `dh-param` folder at `/home/centos/Projects/Docker/SS/_sites/admin/dh-param` and generate a 2048 bit DH Param file and place it in our new folder using...

```
sudo openssl dhparam -out /home/centos/Projects/Docker/SS/_sites/admin/dh-param/dhparam-2048.pem 2048
```

## Switching Gears

I'm now working from https://www.digitalocean.com/community/tutorials/how-to-use-traefik-as-a-reverse-proxy-for-docker-containers-on-ubuntu-16-04 to try and get all the networking crap figured out.

Also, be sure to pay attention to additional `traefik.toml` config in the comments, especially https://www.digitalocean.com/community/tutorials/how-to-use-traefik-as-a-reverse-proxy-for-docker-containers-on-ubuntu-16-04?comment=67894.

### Step 1 — Configuring and Running Traefik

On my DO droplet as _centos_...  
```
sudo yum install httpd-tools
htpasswd -nb admin Digit@10c3@n
  ...generated...
admin:$apr1$LvBXFbG8$u8kbNVplrUY9qLQaQ9ZhA0
```

In the _~/Projects/Docker/SS_ project folder I created a new `traefik` folder and `traefik.toml` file within as instructed in the subject guide.

### Step 2 – Running the Traefik Container

Next, as _centos_ on my DO droplet...
```
docker network create proxy
```

Then I created `traefik/acme.json` and set its permissions to _600_.

Next, as _centos_ on my DO droplet with `SS/traefik` as my working directory I created my `traefik` container using...

```
docker run -d \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $PWD/traefik.toml:/traefik.toml \
  -v $PWD/acme.json:/acme.json \
  -p 80:80 \
  -p 443:443 \
  -l traefik.frontend.rule=Host:traefik.summittservices.com \
  -l traefik.port=8080 \
  --network proxy \
  --name traefik \
  traefik:1.5.2-alpine --docker
```

It works!  Traefik is available at `https://traefik.summittservices.com`.

### Step 3 — Registering Containers with Traefik

I opened `SS/_sites/admin/docker-compose.yml` and added the following network specs near the top of the file...

```
networks:
  proxy:
    external: true
  internal:
    external: false
```
In the `nginx` service portion of my `docker-compose.yml` I changed _labels_ and _networks_ to read...

```
networks:
  - internal
  - proxy
labels:
  - traefik.backend=${PROJECT_NAME}_nginx
  - traefik.port=80
  - traefik.frontend.rule=Host:${PROJECT_FULL_URL}
  - traefik.docker.network=proxy
depends_on:
  - php
```
The `mariadb` and `php` portions of `docker-compose.yml` should include the following...
```
networks:
  - internal
labels:
  - 'traefik.enable:false'
```

## Final (?) Thoughts

So, I think this is all working now.  The _restart.sh_ script has been revised to take care of everything, if possible, and _portainer_ has been added as a 'site' answering to https://portainer.summittservices.com.  _restart.sh_ also checks to see if the _traefik_ service is running (it should answer at https://traefik.summittservices.com and should pick up new containers as they come up) and starts it up if needed.
