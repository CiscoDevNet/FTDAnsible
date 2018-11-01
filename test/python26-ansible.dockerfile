FROM lovato/python-2.6
ARG ANSIBLE_BRANCH=v2.7.0

# SETUP SYSTEM PACKAGES
RUN apt-get update && apt-get -y install git wget build-essential libssl-dev libffi-dev python3-dev

# PREPARE PY2.6
RUN wget https://github.com/pypa/setuptools/archive/bootstrap-2.x.tar.gz && \
    tar -xvf bootstrap-2.x.tar.gz && \
    cd setuptools-bootstrap-2.x && \
    python2.6 setup.py install

RUN wget https://github.com/pypa/pip/archive/9.0.3.tar.gz && \
    tar -xvf 9.0.3.tar.gz && \
    cd pip-9.0.3 && \
    python2.6 setup.py install

# CLONE ANSIBLE
RUN wget https://github.com/ansible/ansible/archive/${ANSIBLE_BRANCH}.tar.gz && \
    tar -xvf ${ANSIBLE_BRANCH}.tar.gz && \
    mv `find ./ -maxdepth 1 -type d -name '*ansible-*'` /ansible

# INSTALL PYTHON REQUIREMENTS
RUN python2.6 /usr/local/bin/pip install pycparser==2.18 cryptography==2.0 && \
    python2.6 /usr/local/bin/pip install \
    --disable-pip-version-check \
    -c /ansible/test/runner/requirements/constraints.txt \
    -r /ansible/test/runner/requirements/units.txt

ENV PYTHONPATH="$PYTHONPATH:/ansible/lib:/ansible/test"
WORKDIR /ftd-ansible
CMD ["pytest", "--version"]
