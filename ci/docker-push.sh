#!/bin/bash

if [ -z "$SECRET_DOCKER_PASSWORD" ]; then
   echo SECRET_DOCKER_PASSWORD environment variable is not set. Skipping docker push.
   exit 0
fi

set -e
set -x

IMAGE=lizaalert/lacmus
TAG=travis-${TRAVIS_COMMIT:0:7}${TARGET#build}

docker login -u $SECRET_DOCKER_LOGIN -p $SECRET_DOCKER_PASSWORD
docker push $IMAGE:$TAG

if [ -n "$TRAVIS_TAG" ]; then
    docker tag $IMAGE:$TAG $IMAGE:${TRAVIS_TAG}${TARGET#build}
    docker push $IMAGE:$TRAVIS_TAG${TARGET#build}
fi

if [ "$TRAVIS_PULL_REQUEST" == "false" && \
     "$TRAVIS_REPO_SLUG" == "$IMAGE" && \
     "$TRAVIS_BRANCH" == "master" ]; then
    docker tag $IMAGE:$TAG $IMAGE:latest
    docker push $IMAGE:latest
fi
