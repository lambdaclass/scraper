#!/usr/bin/env bash

set -eo pipefail

CMD=$2

if [ $CMD == 'backup' ]; then
  if [ -z $S3_BUCKET ] && [ -z $AWS_ACCESS_KEY_ID ] && [ -z $AWS_SECRET_ACCESS_KEY]; then
    echo '[ERROR] To backup data you must set env variables $S3_BUCKET, $AWS_ACCESS_KEY_ID and $AWS_SECRET_ACCESS_KEY.'
    exit 1
  fi
fi

if [ -z $SCRAPER_DATA_PATH ]; then
  echo '[ERROR] Environment variable $SCRAPER_DATA_PATH not set.'
  exit 1
fi

if [ $CRAWLER == 'tiingo' ] && [ -z $TIINGO_API_KEY ]; then
  echo '[ERROR] Environment variable $TIINGO_API_KEY not set.'
  exit 1
fi

if [ -z $SLACK_WEBHOOK ]; then
  echo '[WARNING] Environment variable $SLACK_WEBHOOK not set. Notifications disabled.'
fi

# Run the original command
exec "$@"
