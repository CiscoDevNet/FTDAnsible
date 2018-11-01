ARG PYTHON_VERSION=3.6
FROM python:${PYTHON_VERSION}
ARG FTD_ANSIBLE_VERSION=v0.1.0
ARG FTD_ANSIBLE_FOLDER=ftd-ansible

RUN wget https://github.com/CiscoDevNet/FTDAnsible/archive/${FTD_ANSIBLE_VERSION}.tar.gz && \
    tar -xvf ${FTD_ANSIBLE_VERSION}.tar.gz

RUN mkdir /${FTD_ANSIBLE_FOLDER}/ && \
    export ARCHIVED_FOLDER=`find ./ -maxdepth 1 -type d -name '*FTDAnsible-*'` && \
    mv $ARCHIVED_FOLDER/httpapi_plugins \
    $ARCHIVED_FOLDER/library \
    $ARCHIVED_FOLDER/module_utils \
    $ARCHIVED_FOLDER/requirements.txt \
    $ARCHIVED_FOLDER/ansible.cfg  /${FTD_ANSIBLE_FOLDER}

RUN pip install --no-cache-dir -r /${FTD_ANSIBLE_FOLDER}/requirements.txt

ENV PYTHONPATH="$PYTHONPATH:/${FTD_ANSIBLE_FOLDER}/"
WORKDIR /${FTD_ANSIBLE_FOLDER}
ENTRYPOINT ["ansible-playbook"]
