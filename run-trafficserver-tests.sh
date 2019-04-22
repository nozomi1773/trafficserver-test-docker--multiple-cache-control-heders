#!/bin/bash
set -e

mkdir -p ~build/logs

(cd ~build/dev/trafficserver/tests \
 && echo "=== test target trafficserver git commit ===" \
 && git log -1 \
 && . env-test/bin/activate \
 && echo "" \
 && echo "=== test results ===" \
 && env-test/bin/autest -D gold_tests --ats-bin /usr/local/bin) \
 | tee ~build/logs/trafficserver-test-$(date +%Y%m%d-%H%M).log
