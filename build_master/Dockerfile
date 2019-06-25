FROM ubuntu:18.04

# This dockerfile follows the setup in
# https://github.com/apache/trafficserver/blob/master/tests/bootstrap.py

# Install packages to build trafficserver
RUN ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime \
 && sed -i 's/^# deb-src/deb-src/' /etc/apt/sources.list \
 && apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get build-dep -y trafficserver \
 && apt-get install -y git \
 && apt-get install -y python3 python3-virtualenv virtualenv python3-dev curl netcat net-tools \
 && useradd -r -m -s /bin/bash build

USER build

# Get the source and configure trafficserver
RUN mkdir -p ~/dev \
 && cd ~/dev \
 && git clone --depth 1 https://github.com/apache/trafficserver \
 && cd trafficserver \
 && git log -1 \
 && autoreconf -if

# NOTE: Add patches here if available

# Build trafficserver
RUN cd ~/dev/trafficserver \
 && ./configure --enable-experimental-plugins \
 && make

USER root
RUN cd ~build/dev/trafficserver \
 && make install \
 && echo /usr/local/lib > /etc/ld.so.conf.d/trafficserver.conf \
 && ldconfig

USER build

# Set up test environment
RUN cd ~/dev/trafficserver/tests \
 && virtualenv --python=python3 env-test \
 && env-test/bin/pip install pip --upgrade \
 && env-test/bin/pip install autest==1.7.2 hyper hyper requests dnslib httpbin traffic-replay

# Run trafficserver existing gold_tests
COPY run-trafficserver-tests.sh /usr/local/bin/

USER root
RUN chmod 777 /usr/local/bin/run-trafficserver-tests.sh
RUN echo "127.0.0.1    origin.example.com" >> /etc/hosts

USER build
RUN /usr/local/bin/run-trafficserver-tests.sh

# Run multiple cache control headers gold_tests
COPY --chown=build:build tests/gold_tests/multiple-cache-control/ /tmp/multiple-cache-control/
RUN mkdir ~/tmp
RUN cd ~/dev/trafficserver/tests/gold_tests/ \
 && mv * ~/tmp/ \
 && mv ~/tmp/autest-site ~/dev/trafficserver/tests/gold_tests/
RUN mv /tmp/multiple-cache-control ~/dev/trafficserver/tests/gold_tests/
RUN /usr/local/bin/run-trafficserver-tests.sh

ENTRYPOINT ["/bin/bash"]
