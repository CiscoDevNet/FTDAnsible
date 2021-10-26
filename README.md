# FTD Ansible Modules

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
ansible-doc -M ansible_collections/cisco/ftdansible/plugins/modules/ ftd_configuration
ansible-doc -M ansible_collections/cisco/ftdansible/plugins/modules/ ftd_file_download
ansible-doc -M ansible_collections/cisco/ftdansible/plugins/modules/ ftd_file_upload
ansible-doc -M ansible_collections/cisco/ftdansible/plugins/modules/ ftd_install
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
ansible-galaxy collection install git+https://github.com/meignw2021/ftd-ansible.git#/cisco/

Starting collection install process
Installing 'cisco.ftdansible:3.3.3' to '/root/.ansible/collections/ansible_collections/cisco/ftdansible'
Created collection for cisco.ftdansible at /root/.ansible/collections/ansible_collections/cisco/ftdansible
cisco.ftdansible (3.3.3) was installed successfully
```

3. List installed collections.
```
ansible-galaxy collection list
```

3. Validate your ansible.cfg file contains a path to ansible collections:

```
cat ansible.cfg
```

4. Reference the collection from your playbook

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
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/access_rule_with_applications.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/access_policy.yml
```

### Running playbooks locally with Docker

1. Build the default Python 3.6, Ansible 2.10 Docker image:
    ```
    docker build -t ftd-ansible .
    ```
    **NOTE**: The default image is based on the release v0.4.0 of the [`FTD-Ansible`](https://github.com/CiscoDevNet/FTDAnsible) and Python 3.6. 

2. You can build the custom Docker image:
    ```
    docker build -t ftd-ansible \
    --build-arg PYTHON_VERSION=<2.7|3.5|3.6|3.7> \
    --build-arg FTD_ANSIBLE_VERSION=<tag name | branch name> .
    ```

3. Create an inventory file that tells Ansible what devices to run the tasks on. [`sample_hosts`](./inventory/sample_hosts) shows an example of inventory file.

4. Run the playbook in Docker mounting playbook folder to `/ftd-ansible/playbooks` and inventory file to `/etc/ansible/hosts`:
    ```
    docker run -v $(pwd)/samples:/ftd-ansible/playbooks \
    -v $(pwd)/inventory/sample_hosts:/etc/ansible/hosts \
    ftd-ansible playbooks/ftd_configuration/network_object.yml
    ```

### Running playbooks locally 

1. Create a virtual environment and activate it:
```
python -m venv venv
. venv/bin/activate
```

2. Install dependencies:
`pip install -r requirements.txt`

3. Update Python path to include the project's directory:
```
export PYTHONPATH=.:$PYTHONPATH
```

4. Install the collection

5. Run the playbook:
``` 
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/access_rule_with_applications.yml
```

## Unit Tests

The project contains unit tests for Ansible modules, HTTP API plugin and util files. They can be found in `test/unit` directory. Ansible has many utils for mocking and running tests, so unit tests in this project also rely on them and including Ansible test module to the Python path is required.

### Running unit tests in Docker

1. Build the Docker image: 
```
docker build -t ftd-ansible-test -f Dockerfile.tests . 
```
**NOTE**: Dockerfile uses Ansible version from `requirements.txt`. You can change it by replacing the version in `requirements.txt` and rebuilding the Docker image.

**NOTE**: There is a separate Dockerfile for Ansible 2.9.  Use this command to build that.
```
docker build -t ftd-ansible-test -f Dockerfile.ansible29.tests . 
```

2. Run unit tests with:
```
docker run ftd-ansible-test
```

To run a single test, specify the filename at the end of command:
```
docker run ftd-ansible-test test/unit/test_ftd_configuration.py
docker run ftd-ansible-test test/unit/test_ftd_file_download.py
docker run ftd-ansible-test test/unit/test_ftd_file_upload.py
docker run ftd-ansible-test test/unit/test_ftd_install.py

docker run ftd-ansible-test test/unit/module_utils/test_common.py
docker run ftd-ansible-test test/unit/module_utils/test_configuration.py
docker run ftd-ansible-test test/unit/module_utils/test_device.py
docker run ftd-ansible-test test/unit/module_utils/test_fdm_swagger_parser.py
docker run ftd-ansible-test test/unit/module_utils/test_fdm_swagger_validator.py
docker run ftd-ansible-test test/unit/module_utils/test_fdm_swagger_with_real_data.py
docker run ftd-ansible-test test/unit/module_utils/test_upsert_functionality.py

docker run ftd-ansible-test test/unit/httpapi_plugins/test_ftd.py

```

**NOTE**: You need to rebuild the Docker image on every change of the code.

#### Troubleshooting

```
import file mismatch:
imported module 'test.unit.module_utils.test_common' has this __file__ attribute: ...
which is not the same as the test file we want to collect:
  /ftd-ansible/test/unit/module_utils/test_common.py
HINT: remove __pycache__ / .pyc files and/or use a unique basename for your test file modules
```

In case you experience the following error while running the tests in Docker, remove compiled bytecode files files with 
`find . -name "*.pyc" -type f -delete` command and try again.

### Running unit tests locally

1. Clone [Ansible repository](https://github.com/ansible/ansible) from GitHub;
```
git clone https://github.com/ansible/ansible.git
```

**NOTE**: The next steps can be hosted in docker container
```
docker run -it -v `pwd`:/ftd-ansible python:3.6 bash
cd /ftd-ansible
pip download $(grep ^ansible ./requirements.txt) --no-cache-dir --no-deps -d /tmp/pip 
mkdir /tmp/ansible
tar -C /tmp/ansible -xf /tmp/pip/ansible*
mv /tmp/ansible/ansible* /ansible
rm -rf /tmp/pip /tmp/ansible
```

2. Install Ansible and test dependencies:
```
export ANSIBLE_DIR=`pwd`/ansible
pip install -r requirements.txt
pip install -r $ANSIBLE_DIR/requirements.txt
pip install -r test-requirements.txt
```

3. Add Ansible modules to the Python path:
```
export PYTHONPATH=$PYTHONPATH:$ANSIBLE_DIR/lib:$ANSIBLE_DIR/test
```

4. Run unit tests:
```
cd /ftd-ansible
pytest --cov-report term \
  --cov=ansible_collections/cisco/ftdansible/plugins \
  ansible_collections/cisco/ftdansible/tests
```


5. Run individual unit tests:

```
pytest ansible_collections/cisco/ftdansible/tests/unit/test_ftd_configuration.py
pytest ansible_collections/cisco/ftdansible/tests/unit/test_ftd_file_download.py
pytest ansible_collections/cisco/ftdansible/tests/unit/test_ftd_file_upload.py
pytest ansible_collections/cisco/ftdansible/tests/unit/test_ftd_install.py

pytest ansible_collections/cisco/ftdansible/tests/unit/module_utils/test_common.py
pytest ansible_collections/cisco/ftdansible/tests/unit/module_utils/test_configuration.py
pytest ansible_collections/cisco/ftdansible/tests/unit/module_utils/test_device.py
pytest ansible_collections/cisco/ftdansible/tests/unit/module_utils/test_fdm_swagger_parser.py
pytest ansible_collections/cisco/ftdansible/tests/unit/module_utils/test_fdm_swagger_validator.py
pytest ansible_collections/cisco/ftdansible/tests/unit/module_utils/test_fdm_swagger_with_real_data.py
pytest ansible_collections/cisco/ftdansible/tests/unit/module_utils/test_upsert_functionality.py

pytest ansible_collections/cisco/ftdansible/tests/unit/httpapi_plugins/test_ftd.py
```
 
### Running tests with [TOX](https://tox.readthedocs.io/en/latest/) 
**NOTE**: To be able to run tests with the specific version of Python using tox you need to have this version of Python installed locally  

Install tox locally:
```
pip install tox
```
Check the list of currently supported environments:
```
tox -l
```
**NOTE**: environments with _-integration_ postfix preconfigured for integration tests:

Setup `PYTHONPATH` as described in the previous section
Run unit tests in virtualenvs using tox:
```
tox -e py27,py35,py36,py37
```
Run integration tests in virtualenvs using tox:
```
export REPORTS_DIR=<path to the folder where JUnit reports will be stored>
tox -e py27-integration,py35-integration,py36-integration,py37-integration -- samples/network_object.yml -i inventory/sample_hosts
```
### Running style check locally
1. Install [Flake8](http://flake8.pycqa.org/en/latest/) locally:
    ```
    pip install flake8
    ```

2. Run Flake8 check:
    ```
    flake8
    ```

Flake8 configuration is defined in the [tox config file](./tox.ini) file.

## Integration Tests

Integration tests are written in a form of playbooks and usually started with `ansible-test` command from Ansible repository. As this project is created outside Ansible, it does not have utils to run the tests. Thus, integration tests are written as sample playbooks with assertion and can be found in the `samples` folder. They start with `test_` prefix and can be run as usual playbooks.

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

# used when running sanity tests
ansible-galaxy collection install community.general
ansible-galaxy collection install community.network
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
```
cd /ftd-ansible
pytest --cov-report term \
  --cov=ansible_collections/cisco/ftdansible/plugins \
  ansible_collections/cisco/ftdansible/tests
```

7. Create an inventory file that tells Ansible what devices to run the tasks on. [`sample_hosts`](./inventory/sample_hosts) shows an example of inventory file.

8. Run an integration playbook.

```    
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/access_policy.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/access_rule_with_applications.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/access_rule_with_intrusion_and_file_policies.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/access_rule_with_logging.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/access_rule_with_networks.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/access_rule_with_urls.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/access_rule_with_users.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/anyconnect_package_file.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/backup.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/data_dns_settings.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/deployment.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/dhcp_container.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/download_upload.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/ha_join.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/identity_policy.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/initial_provisioning.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/nat.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/network_object_with_host_vars.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/network_object.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/physical_interface.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/port_object.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/ra_vpn_license.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/ra_vpn.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/security_intelligence_url_policy.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/smart_license.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/ssl_policy.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/static_route_entry.yml
ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/sub_interface.yml
```

## Debugging

1. Add `log_path` with path to log file in `ansible.cfg`

2. Run `ansible-playbook` with `-vvvv`
    ```
    $ ansible-playbook -i inventory/sample_hosts samples/ftd_configuration/access_rule_with_applications.yml -vvvv
    ```

3. The log file will contain additional information (REST, etc.)
