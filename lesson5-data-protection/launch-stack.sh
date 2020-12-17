#!/usr/bin/env bash
# Bash template based on https://github.com/eppeters/bashtemplate.sh
set -euo pipefail
IFS=$'\n\t'

aws cloudformation create-stack --stack-name csoa-5 --capabilities CAPABILITY_NAMED_IAM --disable-rollback --template-body file://csoa-5-cloudfront.yml
