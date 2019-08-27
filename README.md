# FTD Ansible Modules

A collection of Ansible modules that automate configuration management 
and execution of operational tasks on Cisco Firepower Threat Defense (FTD) devices using FTD REST API.

_This file describes the development and testing aspects. In case you are looking for 
the user documentation, please check [FTD Ansible docs on DevNet](https://developer.cisco.com/site/ftd-ansible/)._

## Installation Guide

The project contains four Ansible modules:

* [`ftd_configuration.py`](./library/ftd_configuration.py) - manages device configuration via REST API. The module configures virtual and physical devices by sending HTTPS calls formatted according to the REST API specification;
* [`ftd_file_download.py`](./library/ftd_file_download.py) - downloads files from FTD devices via HTTPS protocol;
* [`ftd_file_upload.py`](./library/ftd_file_upload.py) - uploads files to FTD devices via HTTPS protocol;
* [`ftd_install.py`](./library/ftd_install.py) - installs FTD images on hardware devices. The module performs a complete reimage of the Firepower system by downloading the new software image and installing it. 

Sample playbooks are located in the [`samples`](./samples) folder.

### Running playbooks in Docker

1. Build the default Docker image:
    ```
    docker build -t ftd-ansible .
    ```
    **NOTE** The default image is based on the release v0.1.0 of the [`FTD-Ansible`](https://github.com/CiscoDevNet/FTDAnsible) and Python 3.6. 

2. You can build the custom Docker image:
    ```
    docker build -t ftd-ansible --build-arg PYTHON_VERSION=<2.7|3.5|3.6|3.7> --build-arg FTD_ANSIBLE_VERSION=<tag name | branch name> .
    ```

3. Create an inventory file that tells Ansible what devices to run the tasks on. [`sample_hosts`](./inventory/sample_hosts) shows an example of inventory file.

4. Run the playbook in Docker mounting playbook folder to `/ftd-ansible/playbooks` and inventory file to `/etc/ansible/hosts`:
    ```
    docker run -v $(pwd)/samples:/ftd-ansible/playbooks -v $(pwd)/inventory/sample_hosts:/etc/ansible/hosts ftd-ansible playbooks/network_object.yml
    ```

### Running playbooks locally 

1. Create a virtual environment and activate it:
```
python3 -m venv venv
. venv/bin/activate
```

2. Install dependencies:
`pip install -r requirements.txt`

3. Update Python path to include the project's directory:
```
export PYTHONPATH=.:$PYTHONPATH
```
  
4. Run the playbook:
``` 
ansible-playbook samples/network_object.yml
```

## Unit Tests

The project contains unit tests for Ansible modules, HTTP API plugin and util files. They can be found in `test/unit` directory. Ansible has many utils for mocking and running tests, so unit tests in this project also rely on them and including Ansible test module to the Python path is required.

### Running unit tests in Docker

1. Build the Docker image: 
```
docker build -t ftd-ansible-test -f Dockerfile.tests . 
```
**NOTE**: Dockerfile uses Ansible version from `requirements.txt`. You can change it by replacing the version in `requirements.txt` and rebuilding the Docker image.

2. Run unit tests with:
```
docker run ftd-ansible-test
```
To run a single test, specify the filename at the end of command:
```
docker run ftd-ansible-test test/unit/test_ftd_configuration.py
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

2. Install Ansible and test dependencies:
```
pip install $ANSIBLE_DIR/requirements.txt
pip install test-requirements.txt
```

3. Add Ansible modules to the Python path:
```
export PYTHONPATH=$PYTHONPATH:$ANSIBLE_DIR/lib:$ANSIBLE_DIR/test
```

4. Run unit tests:
```
pytest test/unit
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

## Debugging

1. Add `log_path` with path to log file in `ansible.cfg`

2. Run `ansible-playbook` with `-vvvv`
    ```
    $ ansible-playbook samples/network_object.yml -vvvv
    ```

3. The log file will contain additional information (REST, etc.)
