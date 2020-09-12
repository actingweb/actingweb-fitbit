#!/usr/bin/env bash
stage="$1"
if [[ $stage == "" ]]; then
  stage="dev"
fi
p=`aws ecr get-login --no-include-email --region us-west-2`
eval "$p"
docker build -t fitbit-fargate-${stage} .
docker tag fitbit-fargate-${stage}:latest 473852420549.dkr.ecr.us-west-2.amazonaws.com/fitbit-fargate-${stage}:latest
docker push 473852420549.dkr.ecr.us-west-2.amazonaws.com/fitbit-fargate-${stage}:latest
