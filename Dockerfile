FROM centos:7

RUN yum -y install epel-release \
 && curl -sL -o /etc/yum.repos.d/hnakamur-apache-traffic-server-6.repo https://copr.fedoraproject.org/coprs/hnakamur/apache-traffic-server-6/repo/epel-7/hnakamur-apache-traffic-server-6-epel-7.repo \
 && yum -y install trafficserver @"Development Tools" git python36 python36-devel python36-virtualenv \
 && useradd -r -m -s /bin/bash build

USER build

# Get the source for test files
RUN mkdir -p ~/dev \
 && cd ~/dev \
 && git clone --depth 1 https://github.com/apache/trafficserver \
 && cd trafficserver \
 && git log -1

# Set up test environment
RUN cd ~/dev/trafficserver/tests \
 && python3 -m venv env-test \
 && env-test/bin/pip install pip --upgrade \
 && env-test/bin/pip install autest==1.7.2 hyper requests dnslib httpbin traffic-replay

# Run trafficserver tests
COPY run-trafficserver-tests.sh /usr/local/bin/
RUN /usr/local/bin/run-trafficserver-tests.sh || :

# Run negative cache tests
COPY --chown=build:build tests/gold_tests/negative_cache/ /tmp/negative_cache/
RUN mv /tmp/negative_cache ~/dev/trafficserver/tests/gold_tests/
RUN . ~/dev/trafficserver/tests/env-test/bin/activate \
 && cd ~/dev/trafficserver/tests/gold_tests/negative_cache \
 && HAS_NEGATIVE_CACHING_LIST=0 ./generate_and_run_negative_cache_tests.py | tee ~/logs/negative_cache_tests-$(date +%Y%m%d-%H%M%S.log)

ENTRYPOINT ["/bin/bash"]
