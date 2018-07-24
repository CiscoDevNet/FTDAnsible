# FTD Ansible Modules

## Common environment setup
1. Create a virtual environment:
`python3 -m venv venv`

1. Activate the virtual environment:
```. venv/bin/activate```

1. Install dependencies:
`pip install -r requirements.txt`

1. Override `ansible_python_interpreter` to point to the local python in `group_vars/vftd/vars`.

## Ansible Inventory
Inventory is used to tell Ansible what hosts to run the tasks on. By default, this project uses the inventory from `inventory/development` file. You can either update this file with a list of desired hosts or create a new inventory file and specify it in `ansible.cfg`.

## Ansible modules

The project contains Ansible modules for managing Network, Network Group, Access Policy and Access Rule objects, handling authentication and making deployment on FTD devices. 

Ansible modules are located in the `library` folder. Modules generated automatically from Swagger specification are located in `library/generated` folder. 

Sample playbooks located in `samples` folder contain examples of their usage. To run the playbook:
 
1. Complete "Common environment setup" section;

1. Run the playbook:
    ```
    $ ansible-playbook samples/network_object.yml
    ```


## Module Generator
Ansible modules can be automatically generated from Swagger specification. The generator downloads available Swagger Resources and creates
a separate module for each model per resource. Currently, modules are only generated for resources configured in `generator/module_gelerator.py` file.

To generate Ansible modules:

1. Complete "Common environment setup" section;

1. Run the generator:
    ```
    python -m generator.module_generator $HOSTNAME $USERNAME $PASSWORD
    ```

1. Generated files must be located in the `library/generated` folder.

## Testing

### Unit Tests

The project contains examples of Ansible unit tests written for `ftd_deploy` module. They can be found in `test/unit` directory. Ansible has many utils for mocking and running tests, so unit tests
in this project also rely on them and including Ansible test module to the Python path is required to run them. When the project is
developed further, modules and tests will be moved to the Ansible repository and this extra step will be no longer needed.

In order to run the unit tests: 

1. Complete "Common environment setup" section;
1. Clone [Ansible repository](https://github.com/ansible/ansible) from GitHub;
1. Add Ansible modules to the Python path:
    ```
    export PYTHONPATH=ANSIBLE_DIR/test:ANSIBLE_DIR/lib:$PYTHONPATH
    ```
1. Run unit tests:
    ```
    pytest test/unit
    ```
    
### Integration Tests

Ansible integration tests are written in a form of playbooks and are usually run with `ansible-test` utility command from Ansible repository. This project 
contains examples of integration tests written for `ftd_network_object` module that are located in `test/integration` folder.

As current project is created outside Ansible repository, copying modules/module utils/tests is required before running them. In order to run the integration tests:

1. Clone [Ansible repository](https://github.com/ansible/ansible) from GitHub;
1. Copy Ansible modules from `library` to `ANSIBLE_DIR/lib/ansible/modules/network/ftd`;
1. Copy module utils from `module_utils` to `ANSIBLE_DIR/lib/ansible/module_utils`;
1. Copy integration †ests from `test/integration` to `ANSIBLE_DIR/test/integration/targets`;
1. Configure test inventory:
    ```
    cd ANSIBLE_DIR/test/integration
    cp inventory.network.template inventory.networking
    ${EDITOR:-vi} inventory.networking
    # Add in machines for the platform(s) you wish to test
    ```
1. Define FTD modules as network modules by adding `ftd` prefix to `ANSIBLE_DIR/test/integration/target-prefixes.network` file;
1. Run integration tests for `ftd_network_object` module:
    ```
    ansible-test network-integration --inventory inventory.networking ftd_network_object
    ```