#!/bin/bash

set -e
set -x

docker login -u $SECRET_DOCKER_LOGIN -p $SECRET_DOCKER_PASSWORD
docker push rescuer/rescuer-la:travis-$TRAVIS_BUILD_NUMBER
docker tag rescuer/rescuer-la:travis-$TRAVIS_BUILD_NUMBER rescuer/rescuer-la:$TRAVIS_BRANCH
docker push rescuer/rescuer-la:$TRAVIS_BRANCH
