ARG PYTHON_VERSION=3.6
FROM python:${PYTHON_VERSION}
ARG FTD_VERSION=master
ARG DEFAULT_FOLDER=ftd-ansible

RUN wget https://github.com/CiscoDevNet/FTDAnsible/archive/${FTD_VERSION}.tar.gz; \
    tar -xvf ${FTD_VERSION}.tar.gz

RUN mkdir /${DEFAULT_FOLDER}/; \
    mv FTDAnsible-${FTD_VERSION}/httpapi_plugins \
    FTDAnsible-${FTD_VERSION}/library \
    FTDAnsible-${FTD_VERSION}/module_utils \
    FTDAnsible-${FTD_VERSION}/ansible.cfg  /${DEFAULT_FOLDER}

RUN pip install --no-cache-dir -r /FTDAnsible-${FTD_VERSION}/requirements.txt

ENV PYTHONPATH="$PYTHONPATH:/${DEFAULT_FOLDER}/"
WORKDIR /${DEFAULT_FOLDER}/playbooks
ENTRYPOINT ["ansible-playbook"]
