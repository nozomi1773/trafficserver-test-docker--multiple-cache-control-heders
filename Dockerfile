FROM centos:7

RUN yum -y install epel-release \
 && curl -sL -o /etc/yum.repos.d/hnakamur-apache-traffic-server-6.repo https://copr.fedoraproject.org/coprs/hnakamur/apache-traffic-server-6/repo/epel-7/hnakamur-apache-traffic-server-6-epel-7.repo \
 && yum -y install trafficserver @"Development Tools" git python36 python36-devel python36-virtualenv

RUN mkdir -p /home/ats/dev/trafficserver /home/ats/logs \
 && chown -R ats:ats /home/ats \
 && usermod -d /home/ats ats

# Set up test environment
COPY --chown=ats:ats tests/ /home/ats/dev/trafficserver/tests/

USER ats
RUN cd /home/ats/dev/trafficserver/tests \
 && python3 -m venv env-test \
 && env-test/bin/pip install pip --upgrade \
 && env-test/bin/pip install autest==1.7.2 hyper requests dnslib httpbin traffic-replay

# Run negative cache tests
USER root

RUN . /home/ats/dev/trafficserver/tests/env-test/bin/activate \
 && cd /home/ats/dev/trafficserver/tests/gold_tests/negative_cache \
 && HAS_NEGATIVE_CACHING_LIST=0 ./generate_and_run_negative_cache_tests.py | tee /home/ats/logs/negative_cache_tests-$(date +%Y%m%d-%H%M%S.log) || :

CMD ["/bin/bash"]
