FROM centos:centos7
MAINTAINER jamiesun <jamiesun.net@gmail.com>

VOLUME [ "/var/txweb" ]

RUN yum update -y
RUN yum install -y epel-release
RUN yum install -y libffi-devel openssl openssl-devel  \
        git gcc crontabs python-devel python-setuptools  \
        libjpeg-devel libpng-devel czmq czmq-devel  \
        supervisor mysql-devel MySQL-python  && \
        test -f /usr/local/bin/supervisord || ln -s `which supervisord` /usr/local/bin/supervisord && \
        test -f /usr/local/bin/supervisorctl || ln -s `which supervisorctl` /usr/local/bin/supervisorctl 
RUN yum clean all

RUN easy_install -U pip
RUN pip install Mako
RUN pip install Beaker
RUN pip install MarkupSafe
RUN pip install PyYAML
RUN pip install Twisted
RUN pip install cyclone
RUN pip install six
RUN pip install pycrypto
RUN pip install pyOpenSSL>=0.14
RUN pip install service_identity
RUN pip install SQLAlchemy
RUN pip install redis
RUN pip install txzmq
RUN pip install pybeanstalk
RUN pip install requests
RUN pip install Pillow
RUN pip install qrcode
RUN pip install dict2xml
RUN pip install -U --no-deps https://github.com/talkincode/txweb/archive/master.zip







