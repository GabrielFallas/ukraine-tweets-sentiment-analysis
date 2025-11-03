#!/bin/bash
curl -s -X POST -H 'Content-Type: application/json' -d '{"query":"SELECT COUNT(*) as total FROM ukraine_tweets_sentiment"}' http://druid-broker:8082/druid/v2/sql
