#!/bin/bash
set -e

set -x
cd ~build/dev/trafficserver/tests
git log -1

. env-test/bin/activate
env-test/bin/autest -D gold_tests --ats-bin /usr/local/bin
