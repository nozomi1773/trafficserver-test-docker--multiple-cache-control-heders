FROM ubuntu:18.04

# Install packages to build trafficserver
RUN ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime \
 && sed -i 's/^# deb-src/deb-src/' /etc/apt/sources.list \
 && apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get build-dep -y trafficserver \
 && apt-get install -y git \
 && apt-get install -y python3 python3-virtualenv virtualenv python3-dev curl netcat \
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
 && env-test/bin/pip install autest==1.7.2 hyper hyper requests dnslib httpbin

# Run tests for trafficserver
RUN cd ~/dev/trafficserver/tests \
 && . env-test/bin/activate \
 && env-test/bin/autest -D gold_tests --ats-bin /usr/local/bin

USER root
CMD ["/bin/bash"]
