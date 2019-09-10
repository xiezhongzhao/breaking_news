#!/bin/bash

current_dir=$(cd `dirname $0`; pwd)
project_dir=$(dirname $current_dir)

DK_ADDR=120.131.7.143:5000
DK_DIR=data/easycrawlers

function show_usage {
    echo 'usage:' $0 '[Options]'
    echo 'Options:'
    echo '    -n            name'
    echo '    -e            env [dev|test|prod]'
    echo '    -i            Pull and show image infos, but not start'
    echo '    --version     Docker image version; Example: 0.0.1'
    echo '    -h,--help     Help!'
}

function parse_args {
    _opts=`getopt -a -o n::e::i::h:: -l version:,help:: -- "$@"`
    if [ $? != 0 ]; then show_usage && exit 1; fi

    eval set -- "$_opts"
    while [ $# -gt 0 ]
    do
        case "$1" in
            -n)
                NAME=$2 && shift 2 ;;
            -e)
                ENV=$2 && shift 2 ;;
            -i)
                IMAGE_INFO=1 && shift 2 ;;
            --version)
                IMAGE_VERSION=$2 && shift 2 ;;
            -h|--help)
                show_usage && exit 0 ;;
            --)
                shift ;;
            *)
                shift ;;
        esac
    done

    if [[ -z $ENV ]]; then echo "env is empty!" && show_usage && exit 1; fi
    if [[ -z $IMAGE_VERSION ]] && [[ -e $current_dir/.version ]]; then IMAGE_VERSION=$(cat $current_dir/.version); fi
    if [[ -z $IMAGE_VERSION ]] && [[ -e $project_dir/.version ]]; then IMAGE_VERSION=$(cat $project_dir/.version); fi
    if [[ -z $IMAGE_VERSION ]]; then echo "version is empty!" && show_usage && exit 1; fi
}

function start_app {
    image_tag=$DK_ADDR/$DK_DIR:$IMAGE_VERSION
    docker pull $image_tag
    docker images|grep $DK_DIR
    if [[ ! -z $IMAGE_INFO ]]; then return 0; fi

    name=$NAME && if [[ -z $name ]]; then name=x; fi
    container_name=$DK_DIR.$name
    container_name=${container_name//\//.}
    found_num=`docker ps -a|grep $container_name|wc -l`
    found_name=`docker ps -a|grep $container_name|awk -F' ' '{print $NF}'`
    if [[ $found_num -gt 1 ]]; then echo -e "Found exsit containers:\n$found_name" && exit 1; fi
    if [[ $found_name == $container_name ]];then
        echo -n 'Remove: ' && docker rm -f $found_name
    fi

    group_name=ai
    gid=`id |awk -F'groups=' '{print $2}'|awk -F',' '{for(i=1;i<=NF;i++){print $i}}'|grep $group_name|awk -F'(' '{print $1}'`
    name_param='' && if [[ ! -z $NAME ]]; then name_param=-n$NAME ; fi
    mkdir -p $project_dir/logs
    mkdir -p $project_dir/data.out
    docker run -itd -w /work_dir \
            -v $project_dir/logs:/work_dir/logs \
            -v $project_dir/data.out:/work_dir/data.out \
            --privileged \
            --name $container_name $image_tag \
            src/app_main.py -e$ENV $name_param > /dev/null
    docker ps -a |grep $container_name
}

#----------------------------------------------------------------------
parse_args "$@" && [ ! $? -eq 0 ] && exit 1

start_app