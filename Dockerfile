ARG PYTHON_VERSION=3.6
FROM python:${PYTHON_VERSION}
ARG FTD_ANSIBLE_VERSION=0.1.0
ARG FTD_ANSIBLE_FOLDER=ftd-ansible

RUN wget https://github.com/CiscoDevNet/FTDAnsible/archive/${FTD_ANSIBLE_VERSION}.tar.gz && \
    tar -xvf ${FTD_ANSIBLE_VERSION}.tar.gz

RUN mkdir /${FTD_ANSIBLE_FOLDER}/ && \
    mv FTDAnsible-${FTD_ANSIBLE_VERSION}/httpapi_plugins \
    FTDAnsible-${FTD_ANSIBLE_VERSION}/library \
    FTDAnsible-${FTD_ANSIBLE_VERSION}/module_utils \
    FTDAnsible-${FTD_ANSIBLE_VERSION}/ansible.cfg  /${FTD_ANSIBLE_FOLDER}

RUN pip install --no-cache-dir -r /FTDAnsible-${FTD_ANSIBLE_VERSION}/requirements.txt

ENV PYTHONPATH="$PYTHONPATH:/${FTD_ANSIBLE_FOLDER}/"
WORKDIR /${FTD_ANSIBLE_FOLDER}
ENTRYPOINT ["ansible-playbook"]
