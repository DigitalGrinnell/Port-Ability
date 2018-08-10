# README.md

What follows is a chronicle of my efforts to build SummittServices.com, a Dockerized orchestration of Drupal 7 and Drupal 8 sites in production on my Digital Ocean droplet.  The process was one of trial and error (mostly error) but in this document I've tried to remove all the gory detail of failed attempts, keeping only a few warnings denoted as _**FAILED** attempts..._ about what NOT to do in the future, along with details of what ultimately worked.

## Project Goal
The goal of this project is to document and build, in Docker, a set of stacks that can simultaneously support local development and production deployment of several Drupal 7 and Drupal 8 sites in a single environment.  The local/development environment should be easily engaged with XDebug and an IDE like PHPStorm.  The deployed production services should be easy to encrypt for secure SSL/TLS access and suitable for occupying a single VPS of reasonable scale.

Where possible, the process and components created here should be suitable to repeat/reuse toward creation of sites and services on a Grinnell College Docker server (DGDockerX or DGDocker1) to support efforts like ROOTSTALK.

## Basics
Some "as-built" resources and documents...

- The project environments are:

    - DEV = OSX host, my MacBook Air
    - STAGE = CentOS 7 host, my home Docker server
    - PROD = CentOS 7 host, my personal Digital Ocean droplet


- Development and deployment are designed around the practice of "Code Up, Data Down".  Essentially, code is pushed up from DEV to PROD only, while data (databases and data files) are pulled only from PROD down to DEV.

- Network management leverages Traefik (https://docs.traefik.io/).  It makes obtaining and maintaining SSL/TLS certs a breeze.  

- Portainer (https://portainer.io/) is used to assist with management of the entire environment.  

- Lumogon (https://lumogon.com/) is used to inventory the environment as needed.  

- The project employs Wodby's Docker4Drupal (https://github.com/wodby/docker4drupal) images and stack-building techniques.

    - Option 1, documented in https://wodby.com/stacks/drupal/docs/local/quick-start/, was used early in the work to create 'experimental' site stacks.

    - The products of Option 1 then became the starting point(s) for development following Option 2.  The process around Option 2 ultimately prevailed, and Option 2 should be used exclusively going forward.

- The project includes several 'individual' Drupal stacks rather than one or two Drupal 'multi-site' stacks.  This means that each site has its own 'stack' of containers and it's own database, files and codebase.    _**FAILED** attempts were made to create a multi-site environment, but those became virtually impossible to deploy with SSL/TLS across several different domains._

- Atom was used for much of the editing and its _remote-sync_ package (defined in _.remote-sync.json_) was employed early on to sync modifications between my MacBook Air (DEV) and my Digital Ocean droplet (PROD).

- _drush_ is installed in every site but _Composer_ is used for most of the build and maintenance activity.  A workflow was developed for pulling 'custom' modules and themes from GitHub and details are provided later in this document.

## Sequence of Commands / Events

Working on DEV as user _centos_...

#### Clean-up
```
source ~/Projects/Docker/SS/_scripts/destroy-all.sh  
docker network ls   
docker network rm <3-character-network-ID>  
```
...repeat last command as necessary...  

##### On DEV - Option 2: Mount my Drupal Codebase

Step numbers here are from https://wodby.com/stacks/drupal/docs/local/quick-start/.

###### Step 1.
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
|--_prod
|--_scripts  
|--_sites
   |--wieting
      |--html
      |--mariadb-init  
      |--resources  
      |--.env  
      |--docker-compose.yml  
|--traefik  
```
The _Wieting_ codebase is in the _html_ folder above.

Copy `.env`, `docker-compose.yml` and `traefik.yml` from the *_d4d* folder to *_sites/wieting*.

Working in *_sites/wieting*, I modified values in _.env_ and matched them with values in `html/web/sites/wieting/settings.php`.

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
Performing `docker-compose up -d` on MacBook Air from the _wieting_ folder..._**FAILED** to produce the site_ presumably because the _proxy_ network and Traefik were not running.  So...

## Traefik, yay!

I started, and _**FAILED** to bring the whole project together with SSL/TLS_ by following https://www.humankode.com/ssl/how-to-set-up-free-ssl-certificates-from-lets-encrypt-using-docker-and-nginx.  After many hours of teeth gnashing I gave up on this approach...it just didn't work.  

Fortunately, I found https://www.digitalocean.com/community/tutorials/how-to-use-traefik-as-a-reverse-proxy-for-docker-containers-on-ubuntu-16-04 and it just works, IF you also pay attention to the comments, especially the `traefik.toml` config in comments in https://www.digitalocean.com/community/tutorials/how-to-use-traefik-as-a-reverse-proxy-for-docker-containers-on-ubuntu-16-04?comment=67894.

Working through the aforementioned document (and comments) I did the following...

#### Step 1 — Configuring and Running Traefik

On my PROD droplet as user _centos_...  
```
sudo yum install httpd-tools
htpasswd -nb admin mySuperSecretTraefikPassword
  ...generated...
admin:$apr1$LvBXFbG7$u8tbNVlprUY9qLQaQ9ZhA0
```

In the _~/Projects/Docker/SS_ project folder I created a new `traefik` folder and `traefik.toml` file within as instructed in the subject guide.

#### Step 2 – Running the Traefik Container

Next, as _centos_ on my PROD droplet...

```
docker network create proxy
```

  *Note that __proxy__ is the name of the Docker network created here.  You can use any name you like, but you'll see that name has to appear in subsequent bits below.*

Then I created `traefik/acme.json` and set its permissions to _600_.

Next, as _centos_ on my PROD droplet with `SS/traefik` as my working directory I created my `traefik` container using...

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

#### Step 3 — Registering Containers with Traefik

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

...since they are "internal" services, communicating on the "internal" network, and need not be visible to the whole world.


## Portainer

I have really become dependent on _Portainer_ to assist with all my Docker management activities, so much so that I decided to make it a 'site' of its own running in parallel to my other sites.  Note that _Portainer_ is launched with a `docker-compose.yml` file which includes _command_ and _volumes_ specs like this:

```
command: ${PORTAINER_AUTH} -H unix:///var/run/docker.sock
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
```

This means that a single instance of it running on your Docker host can detect EVERY container on the host.  So you only need ONE _Portainer_ per host, not one for every container as some bloggers apparently believe.

My PROD instance of _Portainer_ can be found at https://portainer.summittservices.com, but it's password protected (as is https://traefik.summittservices.com) so you can't necessarily see it.


## Scripts and Environment - Tieing It All Together

Very early on I created the *_scripts* directory to hold some of the _bash_ that I'd use to keep things tidy.  I also started with the notion of keeping all my secrets (passwords mostly) in _.env_ files.

### .env Files

Clauses like `${PORTAINER_AUTH}` that you see in the code snippet above are references to these environment variables.  The `docker-compose` command automatically reads any `.env` file it finds in the same directory as the `docker-compose.yml` it is reading, so I followed suit by putting a `.env` file in every such directory.

`.env` files are also environment-specific.  There's a set of them for DEV and a **different** set for PROD, with some different values in each environment.  For example, in DEV `${PORTAINER_AUTH}` has a value of '--no-auth' specifying that no login/authorization is required; but in PROD that variable is set to '--admin-password $2y$05$Fh2wW6kMJVo8tkirrRYYYOkwvPKMVdkRqmZOUi7bHerJTNVoQfyWC' which specifies that the _admin_ username requires a password for authentication.

@TODO  
Since I have six 'stacks' in use here, and more to come, this makes for a LOT of .env files to keep track of, and much of the information in them is redundant.  It's possible to tell _docker-compose_ to pull from a specific environment file other than `.env` so my aim is to consolidate all variables into a pair of nearly identical `ss.env` files, one for DEV and one for PROD, using some of the techniques documented in https://docs.docker.com/compose/environment-variables/.

### restart.sh

I created the _restart.sh_ script in the *_scripts/* folder to assist with starting, or re-starting, a single site and it's containers. Specifically it...

  - Ensures that the external _proxy_ network is up and running.

  - Is home to the `docker run -d...` command from Step 2 above, and it ensures that Traefik is up and running.

  - Stops, then removes, all containers and unused not-persistent volumes associated with the site(s) which are to be started or re-started.

  - Invokes a `docker-compose up -d` command for each targeted site to bring them back up one-at-a-time.

See *_scripts/restart.sh* for complete details.

### backup-sql.sh

Docker4Drupal includes a feature that allows us to populate a database during a `docker-compose up` using SQL scripts dropped into a specially-named `mariadb-init` directory.  My project leverages this feature in conjunction with the `backup-sql.sh` script which can be used to:

  - Flush a site's Drupal cache, then

  - Intelligently dump the site database to a named SQL file using `drush`

  - It appends the dumped data to a prepared `sql.header` file, and

  - Leave the resulting file in the site's `mariadb-init` directory so that the next re-start of that site will preserve the previous database contents.

See *_scripts/backup-sql.sh* for complete details.

### fix-permissions.sh

This script, patterned after https://www.drupal.org/node/244924, is provided to assist with properly setting directory and file permissions in any Drupal site.

See *_scripts/fix-permissions.sh* for complete details.

## Composer vs. Drush

I've been using _drush_ to build and maintain Drupal sites for a very long time, and it's great, but _Composer_ is clearly the path forward.  _Composer_ works beautifully in Drupal 8 where it rules supreme, but not-so-well in Drupal 7 where it more-or-less came along as an after-thought.

My dilema was how to make it work 'well' in both environments, and particulary with custom themes and code that I built long ago in Drupal 7.  I found the keys to success in the following _Composer_ practices and bits of JSON.  

Each site's individual directory structure, subordinate to the *_sites* directory, looks something like this:

```
|--_sites
   |--<site name>
      |--html
         |--drush
         |--private  
         |--scripts
         |--vendor  
         |--web  
            |--includes   
            |...  
            |--sites  
            |...  
         |--composer.json  
         |--composer.lock  
```

The key to this structure is really the _composer.json_ file and its contents.  An abridged (with ellipsis inserted where significant text has been removed), but typical, _composer.json_ file looks like this:

```
{
    "name": "drupal-composer/drupal-project",
    "description": "Project template for Drupal 7 projects with composer",
    "type": "project",
    "license": "GPL-2.0-or-later",
    "authors": [
        {
            "name": "Mark A. McFate",
            "role": "Creator"
        }
    ],
    "repositories": [
        {
            "type": "composer",
            "url": "https://packages.drupal.org/7"
        },
        {
            "type": "vcs",
            "url": "https://github.com/SummittDweller/SummittServices1.git"
        },
    ],
    "require": {
        "php": ">=5.2.5",
        ...
        "composer/installers": "^1.2",
        "composer/semver": "^1.4",
        "cweagans/composer-patches": "^1.6",
        "drupal-composer/preserve-paths": "^0.1",
        "drupal/addanother": "^2.2",
        ...
        "drupal/wysiwyg": "^2.5",
        "drush/drush": "~8.0",
        "mailgun/mailgun-php": "^2.5",
        "summittdweller/SummittServices1": "dev-master",
        "symfony/filesystem": "~2.7|^3",
        "webflo/drupal-finder": "^1.0.0"
    },
    "conflict": {
        "drupal/core": "8.*"
    },
    "minimum-stability": "dev",
    "prefer-stable": true,
    "config": {
        "sort-packages": true
    },
    "autoload": {
        "classmap": [
            "scripts/composer/ScriptHandler.php"
        ]
    },
    "scripts": {
        "pre-install-cmd": [
            "DrupalProject\\composer\\ScriptHandler::checkComposerVersion"
        ...  
        ]
    },
    "extra": {
        "installer-paths": {
            "web/": [
                "type:drupal-core"
            ],
            ...
            "web/sites/all/libraries/mailgun/": [
                "type:library", "mailgun/mailgun-php"
            ],
            "web/sites/all/modules/contrib/{$name}/": [
                "type:drupal-module"
            ],
            "web/sites/all/themes/contrib/{$name}/": [
                "type:drupal-theme"
            ],
            "web/sites/all/themes/custom/{$name}/": [
                "type:drupal-custom-theme"
            ],
            "web/sites/all/modules/custom/{$name}/": [
                "type:drupal-custom-module"
            ]
        },
        "patches": {
            "cweagans/composer-patches": {
     ...
}
```

The lines that make inclusion of custom themes and modules possible are explained below.

```
            "type": "vcs",
            "url": "https://github.com/SummittDweller/SummittServices1.git"
```
These two lines define a _repository_ of type 'vcs' with a 'url' of "https://github.com/SummittDweller/SummittServices1.git" instructing Composer to look in the referenced GitHub repo for code when necessary.

```
        "composer/installers": "^1.2",
```
This _reqiure_ specification instructs Composer to load version 1.2 (or greater) of the 'composer/installers' package.  This is a package that makes the other Composer behavior possible.

```
        "summittdweller/SummittServices1": "dev-master",
```
This _require_ specification instructs Composer to look for a 'dev-master' version of the 'summittdweller/SummittServices1' package.  This particular package can be found in https://github.com/SummittDweller/SummittServices1.git, a repository we declared above, and Composer will pull the 'dev-master' branch of this code PLUS any dependencies that this package demands.

```
            "web/sites/all/themes/custom/{$name}/": [
                "type:drupal-custom-theme"
            ],
            "web/sites/all/modules/custom/{$name}/": [
                "type:drupal-custom-module"
```
These lines instruct Composer to deposit packages of type=drupal-custom-theme, and type=drupal-custom-module, into the _web/sites/all/themes/custom_ or _web/sites/all/modules/custom_ directories, respectively.  The _{$name}_ spec at the end of each path tells Composer to use the _name:_ attribute of the package to define the last leg of the destination path.

Please browse to and open  https://github.com/SummittDweller/SummittServices1/blob/master/composer.json, paying particular attention to lines 2, 19-21, and 23-25.

  Line 2 contains the complete _name:_ or path to this package, and it matches what we specified in the _require_ statement above.

  Lines 19-21 declare the _name:_, _version:_, and _type:_ of this package as 'summittservices1', 'dev-master', and 'drupal-custom-theme', respectifely.  These declarations subsequently tell Composer that the package destination will be _web/sites/all/themes/custom/summittservices1_ because it's a 'drupal-custom-theme' named 'summittservices1'.

  Lines 23-25 identify where the source code for the project is found, namely in the 'master' branch of 'https://github.com/SummittDweller/summittservices1.git'.

Note that if this custom theme had requirements of its own, they would be listed in a _require_ portion of this package's _composer.json_ file, and Composer would work to satisfy those requirements in a similar fashion.


## Adding a New Site

So, the process is intended to be pretty simple...  

1) Create a new *_sites/???* folder like *_sites/admin*.  
2) Copy the contents of a working site, like *_sites/wieting* (note that Wieting is a Drupal 8 site) to the new *_sites/???* folder.  
3) In the new _site_ folder, make necessary changes to the following files at a minimum...  

    .env
    _prod/_sites/<site>/.env
    html/web/sites/sites.php
    html/web/sites/<site>/settings.php
    mariadb-init/sql-dump*.sql
    mariadb-init/sql.header
    resources/<site>.aliases.drushrc.php

And it really, really works...even in production, with FREE, valid certs that are automatically renewed!    
