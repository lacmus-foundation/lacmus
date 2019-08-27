#!/bin/bash

if [ -z "$SECRET_DOCKER_PASSWORD" ]; then
   echo SECRET_DOCKER_PASSWORD environment variable is not set. Skipping docker push.
   exit 0
fi

set -e
set -x

IMAGE=lizaalert/lacmus

if [[ -n "$TRAVIS" ]]; then
    TAG=travis-${TRAVIS_COMMIT:0:7}${TARGET#build}
elif [[ -n "$BUILDKITE" ]]; then
    TAG=bk-${BUILDKITE_COMMIT:0:7}${TARGET#build}
fi

docker login -u $SECRET_DOCKER_LOGIN -p $SECRET_DOCKER_PASSWORD
docker push $IMAGE:$TAG

if [ -n "$TRAVIS_TAG" ]; then
    docker tag $IMAGE:$TAG $IMAGE:${TRAVIS_TAG}${TARGET#build}
    docker push $IMAGE:$TRAVIS_TAG${TARGET#build}
fi

if [[ -n "$BUILDKITE_TAG" ]]; then
    docker tag $IMAGE:$TAG $IMAGE:${BUILDKITE_TAG}${TARGET#build}
    docker push $IMAGE:$TRAVIS_TAG${TARGET#build}
fi

if [[ "$TRAVIS_PULL_REQUEST" == "false" && \
      "$TRAVIS_REPO_SLUG" == "$IMAGE" && \
      "$TRAVIS_BRANCH" == "master" ]]; then
    docker tag $IMAGE:$TAG $IMAGE:latest${TARGET#build}
    docker push $IMAGE:latest${TARGET#build}
fi

if [[ "$BUILDKITE_PULL_REQUEST" == "false" && \
      "$BUILDKITE_REPO" == "https://github.com/$IMAGE.git" && \
      "$BUILDKITE_BRANCH" == "master" ]]; then
    docker tag $IMAGE:$TAG $IMAGE:latest${TARGET#build}
    docker push $IMAGE:latest${TARGET#build}
fi
