FROM python:3.6

COPY requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt

COPY ./httpapi_plugins /ftd-ansible/httpapi_plugins
COPY ./library /ftd-ansible/library
COPY ./module_utils /ftd-ansible/module_utils
COPY ./ansible.cfg /ftd-ansible/ansible.cfg

ENV PYTHONPATH="$PYTHONPATH:/ftd-ansible"

WORKDIR /ftd-ansible/playbooks

ENTRYPOINT ["ansible-playbook"]
