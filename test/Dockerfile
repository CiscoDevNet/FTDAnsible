FROM python:3.6

ARG ANSIBLE_BRANCH=v2.7.0

# CLONE ANSIBLE
RUN wget https://github.com/ansible/ansible/archive/${ANSIBLE_BRANCH}.tar.gz && \
    tar -xvf ${ANSIBLE_BRANCH}.tar.gz && \
    mv `find ./ -maxdepth 1 -type d -name '*ansible-*'` /ansible

# INSTALL ANSIBLE REQUIREMENTS
RUN pip install \
    --disable-pip-version-check \
    --no-cache-dir \
    -c /ansible/test/runner/requirements/constraints.txt \
    -r /ansible/requirements.txt

# INSTALL FTD-ANSIBLE REQUIREMENTS
COPY requirements.txt /
RUN pip install \
    --no-cache-dir \
    -c /ansible/test/runner/requirements/constraints.txt \
    -r requirements.txt

ENV PYTHONPATH="$PYTHONPATH:/ansible/lib:/ansible/test"
WORKDIR /ftd-ansible

CMD ["pytest", "--version"]
