#!/bin/bash
set -e

cd ~build/dev/trafficserver/tests
. env-test/bin/activate
env-test/bin/autest -D gold_tests --ats-bin /usr/local/bin
