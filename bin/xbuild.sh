#!/bin/bash

current_dir=$(cd `dirname $0`; pwd)
project_dir=$(dirname $current_dir)

DK_ADDR=120.131.7.143:5000
DK_DIR=data/easycrawlers
IMAGE_VERSION=$(cat $project_dir/.version)

function build_img {
    _dockerfile=$1

    image_tag=$DK_ADDR/$DK_DIR:$IMAGE_VERSION
    docker pull $image_tag
    docker build -t $image_tag -f $_dockerfile $project_dir
    [ $? -eq 0 ] && docker push $image_tag
}

build_img $project_dir/bin/Dockerfile.txt