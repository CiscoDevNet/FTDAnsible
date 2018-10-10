FROM python:3.6

ARG ANSIBLE_BRANCH=devel

RUN git clone -b ${ANSIBLE_BRANCH} --single-branch https://github.com/ansible/ansible.git /ansible
RUN pip install --no-cache-dir -r /ansible/requirements.txt
ENV PYTHONPATH="$PYTHONPATH:/ansible/lib:/ansible/test"

COPY requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /ftd-ansible

CMD ["pytest", "--version"]
