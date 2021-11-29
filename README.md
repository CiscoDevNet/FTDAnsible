# FTD Ansible Modules

IMPORTANT: When cloning this repository place it under ansible_collections/cisco (requirement to run some of the Ansible tools like ansible-test).

An Ansible Collection that automates configuration management 
and execution of operational tasks on Cisco Firepower Threat Defense (FTD) devices using FTD REST API.  

_This file describes the development and testing aspects. In case you are looking for 
the user documentation, please check [FTD Ansible docs on DevNet](https://developer.cisco.com/site/ftd-ansible/)._

## Installation Guide

The collection contains four Ansible modules:

* [`ftd_configuration.py`](./ansible_collections/plugins/modules/ftd_configuration.py) - manages device configuration via REST API. The module configures virtual and physical devices by sending HTTPS calls formatted according to the REST API specification;
* [`ftd_file_download.py`](./ansible_collections/plugins/modules//ftd_file_download.py) - downloads files from FTD devices via HTTPS protocol;
* [`ftd_file_upload.py`](./ansible_collections/plugins/modules//ftd_file_upload.py) - uploads files to FTD devices via HTTPS protocol;
* [`ftd_install.py`](./ansible_collections/plugins/modules//ftd_install.py) - installs FTD images on hardware devices. The module performs a complete reimage of the Firepower system by downloading the new software image and installing it. 

Sample playbooks are located in the [`samples`](./samples) folder.

## View Collection Documentation With ansible-docs

The following commands will generate ansible-docs for each of the collection modules

```
ansible-doc -M ./plugins/modules/ ftd_configuration
ansible-doc -M ./plugins/modules/ ftd_file_download
ansible-doc -M ./plugins/modules/ ftd_file_upload
ansible-doc -M ./plugins/modules/ ftd_install
```


## Using the collection in Ansible

1. Setup docker environment

```
docker run -it -v $(pwd)/samples:/ftd-ansible/playbooks \
-v $(pwd)/ansible.cfg:/ftd-ansible/ansible.cfg \
-v $(pwd)/requirements.txt:/ftd-ansible/requirements.txt \
-v $(pwd)/inventory/sample_hosts:/etc/ansible/hosts \
python:3.6 bash

cd /ftd-ansible
pip install -r requirements.txt
```

2. Install the ansible collection

```
ansible-galaxy collection install git+https://github.com/meignw2021/FTDAnsible.git,ftd-7

Starting collection install process
Installing 'cisco.ftdansible:3.3.3' to '/root/.ansible/collections/ansible_collections/cisco/ftdansible'
Created collection for cisco.ftdansible at /root/.ansible/collections/ansible_collections/cisco/ftdansible
cisco.ftdansible (3.3.3) was installed successfully
```

3. List installed collections.
```
ansible-galaxy collection list
```

4. Validate your ansible.cfg file contains a path to ansible collections:

```
cat ansible.cfg
```

5. Reference the collection from your playbook

**NOTE**: The tasks in the playbook reference the collection

```
- hosts: all
  connection: httpapi
  tasks:
    - name: Find a Google application
      cisco.ftdansible.ftd_configuration:
        operation: getApplicationList
        filters:
          name: Google
        register_as: google_app_results
```        

Run the sample playbook.

```
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/download_upload.yml
```

## Tests

The project contains unit tests for Ansible modules, HTTP API plugin and util files. They can be found in `test/unit` directory. Ansible has many utils for mocking and running tests, so unit tests in this project also rely on them and including Ansible test module to the Python path is required.

### Running Sanity Tests In Docker

```
rm -rf tests/output 
ansible-test sanity --docker -v --color --python 3.6
ansible-test sanity --docker -v --color --python 3.7
```

### Running Units Tests In Docker

```
rm -rf tests/output 
ansible-test units --docker -v --python 3.6
ansible-test units --docker -v --python 3.7
```

To run a single test, specify the filename at the end of command:
```
rm -rf tests/output 
ansible-test units --docker -v tests/unit/httpapi_plugins/test_ftd.py --color --python 3.6
ansible-test units --docker -v tests/unit/module_utils/test_upsert_functionality.py --color --python 3.6
```

### Integration Tests via Docker Container

Integration tests are written in a form of playbooks. Thus, integration tests are written as sample playbooks with assertion and can be found in the `samples` folder. They start with `test_` prefix and can be run as usual playbooks.  The integration tests use a local Docker container which copies the necessary code and folders from your local path into a docker container for testing.

1. Build the default Python 3.6, Ansible 2.10 Docker image:
    ```
    docker build -t ftd-ansible:local -f Dockerfile_integration.
    ```
    **NOTE**: The default image is based on the release v0.4.0 of the [`FTD-Ansible`](https://github.com/CiscoDevNet/FTDAnsible) and Python 3.6. 

2. You can build the custom Docker image:
    ```
    docker build -t ftd-ansible:local \
    -f Dockerfile_integration \
    --build-arg PYTHON_VERSION=<2.7|3.5|3.6|3.7> \
    --build-arg FTD_ANSIBLE_VERSION=<tag name | branch name> .
    ```

3. Create an inventory file that tells Ansible what devices to run the tasks on. [`sample_hosts`](./inventory/sample_hosts) shows an example of inventory file.

4. Run the playbook in Docker mounting playbook folder to `/ftd-ansible/playbooks` and inventory file to `/etc/ansible/hosts`:

    ```
    docker run -v $(pwd)/inventory/sample_hosts:/etc/ansible/hosts \
    -v $(pwd)/ansible.cfg:/root/ansible_collections/cisco/ftdansible/ansible.cfg \
    ftd-ansible:local /root/ansible_collections/cisco/ftdansible/samples/ftd_configuration/download_upload.yml

    docker run -v $(pwd)/inventory/sample_hosts:/etc/ansible/hosts \
    -v $(pwd)/ansible.cfg:/root/ansible_collections/cisco/ftdansible/ansible.cfg \
    ftd-ansible:local /root/ansible_collections/cisco/ftdansible/samples/ftd_install/install_ftd_on_2110.yml


    ```

5. To run all of the integration tests

```
bash ./all_sample_tests.txt
```


## Developing Locally With Docker

1. Setup docker environment

```
docker run -it -v $(pwd):/ftd-ansible \
python:3.6 bash
```

2. Change to working directory

```
cd /ftd-ansible
apt update && apt upgrade -y
```

3. Clone [Ansible repository](https://github.com/ansible/ansible) from GitHub;
```
cd /ftd-ansible
rm -rf ./ansible
git clone https://github.com/ansible/ansible.git

# check out the stable version
# if you want to test with 2.9 specify that in the version below
cd /ftd-ansible/ansible
git checkout stable-2.10
```

```
cd /ftd-ansible
pip download $(grep ^ansible ./requirements.txt) --no-cache-dir --no-deps -d /tmp/pip 
mkdir /tmp/ansible
tar -C /tmp/ansible -xf /tmp/pip/ansible*
mv /tmp/ansible/ansible* /ansible
rm -rf /tmp/pip /tmp/ansible
```

4. Install requirements and test dependencies:

```
cd /ftd-ansible
export ANSIBLE_DIR=`pwd`/ansible
pip install -r requirements.txt
pip install -r $ANSIBLE_DIR/requirements.txt
pip install -r test-requirements.txt

# used when running sanity tests
ansible-galaxy collection install community.general
ansible-galaxy collection install community.network
```

5. Add Ansible modules to the Python path:

```
cd /ftd-ansible
export ANSIBLE_DIR=`pwd`/ansible
export PYTHONPATH=$PYTHONPATH:.:$ANSIBLE_DIR/lib:$ANSIBLE_DIR/test
```

6. Run unit tests:

See Secion Above

7. Create an inventory file that tells Ansible what devices to run the tasks on. [`sample_hosts`](./inventory/sample_hosts) shows an example of inventory file.

8. Run an integration playbook.

See section Above 

## Debugging

1. Add `log_path` with path to log file in `ansible.cfg`

2. Run `ansible-playbook` with `-vvvv`
    ```
    $ ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/access_rule_with_applications.yml -vvvv
    ```

3. The log file will contain additional information (REST, etc.)


## Troubleshooting

```
import file mismatch:
imported module 'test.unit.module_utils.test_common' has this __file__ attribute: ...
which is not the same as the test file we want to collect:
  /ftd-ansible/test/unit/module_utils/test_common.py
HINT: remove __pycache__ / .pyc files and/or use a unique basename for your test file modules
```

In case you experience the following error while running the tests in Docker, remove compiled bytecode files files with 
`find . -name "*.pyc" -type f -delete` command and try again.

