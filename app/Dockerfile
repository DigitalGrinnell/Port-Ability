# Port-Ability Dockerfile
#
# Define the following symbolic link in your path and use it to launch Port-Ability, like so:
#   sudo ln -s ~/Port-Ability/app/port-ability.sh /usr/local/bin/port-ability
#
# Then, to run Port-Ability just use a command like:
#   port-ability -vv test portainer admin
#
#
# BUILD-USING:  docker build -t port-ability-image .
#   RUN-USING:  docker run -it --rm -v /var/run/docker.sock:/var/run/docker.sock \
#                                   -v ${HOME}/Port-Ability/_stacks:/usr/src/Port-Ability/_stacks \
#                                   -v ${HOME}/Port-Ability/traefik:/usr/src/Port-Ability/traefik \
#                                   -v ${HOME}/Port-Ability/_master:/usr/src/Port-Ability/_master
#                                   -e HOSTNAME=`hostname` \
#                                   --name port-ability port-ability-image
#
#    See https://jpetazzo.github.io/2015/09/03/do-not-use-docker-in-docker-for-ci/, "The Solution", for
#      an explanation of the significance of the first -v clause.
#

FROM python:alpine

RUN apk add docker
RUN apk update

WORKDIR /usr/src/Port-Ability

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT [ "python", "port_ability.py" ]
