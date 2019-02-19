# Setup Guide

## Setup dependencies
1. Create Python virtual environment
    ```bash
    virtualenv -p python3.6 ./venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

1. Download dynamic inventory for AWS 
    ```bash
    # Get Dynamic inventory
    wget https://raw.githubusercontent.com/ansible/ansible/devel/contrib/inventory/ec2.py
    wget https://raw.githubusercontent.com/ansible/ansible/devel/contrib/inventory/ec2.ini    
    chmod +x ec2.py
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

## Build a custom AMI image

1. Set FTD version and QCOW2 file download path in the playbook 

1. Run the playbook
    ```bash
    ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i ec2.py build_ami_vftd.yaml
    ```

## Deploy a new vFTD using the custom AMI image
1. Set FTD version and custom admin password in the playbook 
1. Run the playbook
    ```bash
    ansible-playbook -i ec2.py deploy_and_destroy.yaml
    ```

## References
- https://aws.amazon.com/blogs/apn/getting-started-with-ansible-and-dynamic-amazon-ec2-inventory-management/
