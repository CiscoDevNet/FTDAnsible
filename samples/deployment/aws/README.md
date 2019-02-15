# Setup Guide

1. Create python virtual env
    ```bash
    virtualenv -p python3.6 ./venv
    source venv/bin/activate
    pip install ansible
    ```

1. Setup python AWS client
    ```bash
    pip install boto3 boto
    ```
1. Download dynamic inventory for AWS 
    ```bash
    # Get Dynamic inventory
    wget https://raw.githubusercontent.com/ansible/ansible/devel/contrib/inventory/ec2.py
    wget https://raw.githubusercontent.com/ansible/ansible/devel/contrib/inventory/ec2.ini    
    cmod +x ec2.py
    ```

1. Set environment variables
    ```bash
    export AWS_ACCESS_KEY_ID='... aws access key ...' 
    export AWS_SECRET_ACCESS_KEY='... aws secret key ...'
    export AWS_REGION='... aws region ...'
    ```

1. Verify setup
    ```bash
    ansible-inventory -i ec2.py --list 
    ```

# Build custom AMI image
1. Set FTD version in the playbook and QCOW2 file download path
1. Run playbook
    ```bash
    ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i ec2.py build_ami_vftd.yaml
    ```

# Deploy new vFTD using custom AMI image
1. Set FTD version in the playbook and custom admin password
1. Run playbook
    ```bash
    ansible-playbook -i ec2.py deploy_and_destroy.yaml
    ```
