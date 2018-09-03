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

The project contains Ansible modules for managing device configuration (`library/ftd_configuration.py`), uploading (`library/ftd_file_upload.py`) and downloading (`library/ftd_file_download.py`) files.  

Sample playbooks located in `samples` folder contain examples of their usage. To run the playbook:
 
1. Complete "Common environment setup" section;

1. Run the playbook:
    ```
    export PYTHONPATH=.:$PYTHONPATH
    $ ansible-playbook samples/network_object.yml
    ```

## Testing

### Unit Tests

The project contains unit tests for Ansible modules, HTTP API plugin and util files. They can be found in `test/unit` directory. Ansible has many utils for mocking and running tests, so unit tests
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

Integration tests are written in a form of playbooks and are usually run with `ansible-test` utility command from Ansible repository. As this project is created outside Ansible, it 
does not have utils to run the tests. Thus, integration tests are written as sample playbooks with assertion and can be found in the `samples` folder. They start with `test_` prefix and can be 
run as usual playbooks.

### Debugging

1. Add `log_path` with path to log file in `ansible.cfg`
2. Run `ansible-playbook` with `-vvvv`
    ```
    $ ansible-playbook samples/network_object.yml -vvvv
    ```
3. The log file will contain additional information(REST etc.)