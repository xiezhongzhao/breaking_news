#!/bin/bash

user=$1

host=120.131.7.143
app_dir="/data/projects/data/easycrawlers"

current_dir=$(cd `dirname $0`; pwd)
project_dir=$(dirname $current_dir)
cd $project_dir
#------------------------------------------------------
ssh -i ~/.ssh/auth_x $user@$host "mkdir -p $app_dir"
rsync -a --progress bin/ $user@$host:$app_dir/bin/
rsync -a --progress src/ $user@$host:$app_dir/src/
rsync -a --progress .dockerignore $user@$host:$app_dir/
rsync -a --progress .version $user@$host:$app_dir/
ssh -i ~/.ssh/auth_x $user@$host "cd $app_dir; bin/xbuild.sh"