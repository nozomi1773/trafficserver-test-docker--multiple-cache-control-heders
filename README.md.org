trafficserver-test-docker
=========================

A Dockerfile for running [tests](https://github.com/apache/trafficserver/tree/master/tests) for [Apache Traffic Server](https://github.com/apache/trafficserver/) on Ubuntu 18.04 LTS.

The setup process follows the steps in [tests/bootstrap.py](https://github.com/apache/trafficserver/blob/master/tests/bootstrap.py)

## Build a docker image

Build trafficserver and run tests during docker build.

```
docker build -t ats-test .
```

## Run Bash shell

```
docker run --rm -it ats-test
```

The test logs are placed in `~build/logs/`.

To run tests again, run the following command in a docker container.

```
run-trafficserver-tests.sh
```
