# Port-Ability

This project is a copy of my earlier SummittServices.com (SS) project work.  It's essentially a stripped-down version of _SS_ with only _Traefik_ and _Portainer_ left in the original.  Much of the _Traefix_ and cert handling here was informed by https://www.digitalocean.com/community/tutorials/how-to-use-traefik-as-a-reverse-proxy-for-docker-containers-on-ubuntu-16-04.  

## Project Goal

The goal of this project is to document and build, in Docker, a pair of stack "management" tools, namely _Traefik_ and _Portainer_, along with the ability to declare a home for application "stacks".  The stacks can be a mix of application types such as Python, Flask, Drupal versions 6, 6 and 8, etc.  The project should support easy local development (DEV), staging (STAGE), and deployment to production (PROD) environments.  Local (DEV) environments should be easily engaged with XDebug and IDEs like PyCharm and PHPStorm.  The deployed production services should be easy to encrypt for secure SSL/TLS access and suitable for occupying a single Docker-ready VPS of reasonable scale.  The configuration of this tool and the "stacks" it manages should be easy to define in a single file.

## Project Structure

```
Port-Ability  
|--app
  |--port-ability.sh
  |--port_ability.py
  |--requirements.txt  
|--docs
|--portainer
  |--docker-compose.yml
|--traefik  
  |--acme.json               <-- do NOT share
  |--traefik.toml.dev
  |--traefik.toml.stage
  |--traefik.toml.prod
|--_master
  |--master.env.sample  
|--README.md
```

## Basics
Some "as-built" resources and documents...

- The project environments are:

    - DEV = OSX host, my MacBook Air
    - STAGE = CentOS 7 host, my home Docker server
    - PROD = Grinnell College's DGDockerX CentOS 7 host

- Development and deployment are designed around the practice of "Code Up, Data Down".  Essentially, code is pushed up from DEV to PROD only, while data (databases and data files) are pulled only from PROD down to DEV.

- Network management leverages Traefik (https://docs.traefik.io/).  It makes obtaining and maintaining SSL/TLS certs a breeze.  

- Portainer (https://portainer.io/) is used to assist with management of the entire environment.  

- Lumogon (https://lumogon.com/) is used to inventory the environment as needed.  

- Atom is used for much of the editing and its _remote-sync_ package (defined in a _.remote-sync.json_ file) is employed to sync modifications between my DEV and PROD.


## Portainer

I have really become dependent on _Portainer_ to assist with all my Docker management activities, so much so that I decided to make it a 'site' of its own running in parallel to my other sites.  Note that _Portainer_ is launched with a `docker-compose.yml` file which includes _command_ and _volumes_ specs like this:

```
command: ${PORTAINER_AUTH} -H unix:///var/run/docker.sock
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
```

This means that a single instance of it running on your Docker host can detect EVERY container on the host.  So you only need ONE _Portainer_ per host, not one for every container as some bloggers apparently believe.

My PROD instance of _Portainer_ can be found at https://portainer.grinnell.edu, but it's password protected (as is https://traefik.grinnell.edu) so you can't necessarily see it.


## Scripts and Environment - Tieing It All Together

Very early on I created the *_scripts* directory to hold some of the _bash_ that I'd use to keep things tidy.  I also started with the notion of keeping all my secrets (passwords mostly) in _.env_ files, but this became cumbersome so I have consolidated all secrets here into a single _.master.env_ file and _restart.sh_ takes care of distribution.

### .env File

Clauses like `${PORTAINER_AUTH}` that you see in the code snippet above are references to these environment variables.  The `docker-compose` command automatically reads any `.env` file it finds in the same directory as the `docker-compose.yml` it is reading, so I followed suit by putting a `.env` file in every such directory.

`.env` files are also environment-specific.  There's a .master.env for DEV and a **different** copy for PROD, with some different values in each environment.  For example, in DEV `${PORTAINER_AUTH}` has a value of '--no-auth' specifying that no login/authorization is required; but in PROD that variable is set to '--admin-password $2abcdefg2tt2kMJhijklmnopxxxOkwvPqrstuvqmZOUiwxyzrJjibberish' which specifies that the _admin_ username requires a password for authentication.

A technique documented in https://docs.docker.com/compose/environment-variables/ is employed here to manage environment variables.

### restart.sh

I created the _restart.sh_ script in the *_scripts/* folder to assist with starting, or re-starting, a single site and it's containers. Specifically it...

  - Ensures that the external _port-ability-proxy_ network is up and running.

  - Is home to the `docker run -d...` command used to launch Traefik, and it ensures that the _traefik_ service is up and running.

  - In a loop, working on each target site...

      - Stops, then removes, all containers and unused not-persistent volumes associated with the site.

      - Temporarily copies _.master.env_ into the target *_sites* directory as _.env_ to provide environment settings to the container.

      - Invokes a `docker-compose up -d` command to bring the site's containers back up.

Suggested use of _restart.sh_ is to create a symbolic link on your host to launch it.  Ensure that the script is executable (`chmod u+x restart.sh`) and try something like this...

```
sudo ln -s /path/to/Port-Ability/_scripts/restart.sh /usr/local/bin/port-ability-restart
```
Launch the script by typing something like `port-ability-restart --portainer` in a host terminal.

See *_scripts/restart.sh* for complete details.

## Notes

Used https://docs.python.org/3/tutorial/venv.html to build the 'app' virtual environment on each node.

Requires Python 3 (with a python3 alias) which I installed on DGDockerX with help https://medium.com/@gkmr.aus/python-3-6-x-installation-centos-7-4-55ada041a03
