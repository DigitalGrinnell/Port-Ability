#!/bin/bash

cwd=`pwd`
cd ${HOME}/Port-Ability/_app
docker build -q -t port-ability-image .
docker run -it --rm \
  -e HOSTNAME=`hostname` \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ${HOME}/Port-Ability/_sites:/usr/src/Port-Ability/_sites \
  -v ${HOME}/Port-Ability/traefik:/usr/src/Port-Ability/traefik \
  -v ${HOME}/Port-Ability/_master:/usr/src/Port-Ability/_master \
  --name port-ability \
  port-ability-image $@
cd ${cwd}