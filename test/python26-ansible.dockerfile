FROM lovato/python-2.6
ARG ANSIBLE_BRANCH=v2.7.0

RUN apt-get update && apt-get -y install git python-setuptools
RUN easy_install pip

RUN git clone -b ${ANSIBLE_BRANCH} --single-branch https://github.com/ansible/ansible.git /ansible
RUN pip install --no-cache-dir -r /ansible/requirements.txt
RUN mkdir /ansible/ftd-ansible

WORKDIR /ansible
