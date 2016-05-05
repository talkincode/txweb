FROM centos:centos7
MAINTAINER jamiesun <jamiesun.net@gmail.com>

VOLUME [ "/var/txweb" ]

RUN yum update -y
RUN yum install -y epel-release
RUN yum install -y libffi-devel openssl openssl-devel \
        git gcc crontabs python-devel python-setuptools \
        supervisor mysql-devel MySQL-python && \
        test -f /usr/local/bin/supervisord || ln -s `which supervisord` /usr/local/bin/supervisord
RUN yum clean all

RUN easy_install -U pip
RUN pip install Mako
RUN pip install Beaker
RUN pip install MarkupSafe
RUN pip install PyYAML
RUN pip install Twisted
RUN pip install tablib
RUN pip install cyclone
RUN pip install six
RUN pip install pycrypto
RUN pip install pyOpenSSL>=0.14
RUN pip install service_identity
RUN pip install SQLAlchemy
RUN pip install redis
RUN pip install -U --no-deps https://github.com/talkincode/txweb/archive/master.zip


ADD entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh


ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]





