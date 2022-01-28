ARG PYTHON_VERSION=3.6
FROM python:${PYTHON_VERSION}
ARG FTD_ANSIBLE_VERSION=v0.4.1236
ARG FTD_ANSIBLE_FOLDER=ftd-ansible

RUN apt-get update && \
    apt-get install -yq sshpass && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN wget https://github.com/meignw2021/FTDAnsible/archive/refs/tags/${FTD_ANSIBLE_VERSION}.tar.gz && \
    tar -xvf ${FTD_ANSIBLE_VERSION}.tar.gz 

RUN mkdir -p /${FTD_ANSIBLE_FOLDER}/ 
RUN export FTD_SOURCE_FOLDER=`find ./ -maxdepth 1 -type d -name '*FTDAnsible-*'` && \
    mv $FTD_SOURCE_FOLDER/ansible_collections /${FTD_ANSIBLE_FOLDER}/ && \
    mv $FTD_SOURCE_FOLDER/requirements.txt /${FTD_ANSIBLE_FOLDER}/ && \
    mv $FTD_SOURCE_FOLDER/ansible.cfg  /${FTD_ANSIBLE_FOLDER}

RUN pip install --no-cache-dir -r /${FTD_ANSIBLE_FOLDER}/requirements.txt

ENV PYTHONPATH="$PYTHONPATH:/${FTD_ANSIBLE_FOLDER}/"
WORKDIR /${FTD_ANSIBLE_FOLDER}
ENTRYPOINT ["ansible-playbook"]
