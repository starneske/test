#!/bin/bash
set -o allexport

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/..

if [ -e .env ]; then
	source .env
fi
echo $TEST_DOCKER_IMAGE_LOCAL

docker build -t $TEST_DOCKER_IMAGE_LOCAL:$TEST_IMAGE_VERSION . 
