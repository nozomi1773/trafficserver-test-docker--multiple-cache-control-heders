trafficserver-test-docker
=========================

A Dockerfile for running [tests](https://github.com/apache/trafficserver/tree/master/tests) for [Apache Traffic Server](https://github.com/apache/trafficserver/) on Ubuntu 18.04 LTS.

The setup process follows the steps in [tests/bootstrap.py](https://github.com/apache/trafficserver/blob/master/tests/bootstrap.py)

## Build a docker image

```
docker build -t ats-test .
```

## Run tests

```
script -c 'docker run --rm -it ats-test' trafficserver-test-$(date +%Y%m%d-%H%M).log
```

## Run Bash shell

```
docker run --rm -it --entrypoint bash ats-test
```
