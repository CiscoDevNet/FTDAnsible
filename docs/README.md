# Documentation for FTD Ansible and FTD API

This module contains generators that create documentation for FTD Ansible modules and FTD REST API.  
Documentation is written using [Markdown](https://daringfireball.net/projects/markdown/)
markup language with [Github Flavor](https://gist.github.com/stevenyap/7038119). Docs describing models
and operations are automatically generated from Swagger specification using [Jinja](http://jinja.pocoo.org/)
template engine.

`docs` folder contains static and generated doc files that are published on [DevNet](https://developer.cisco.com/)
 using PubHub. PubHub takes care of fetching the latest docs from the repository, converting them to HTML and
 hosting on the web site.

### Doc Generation

Docs for FTD Ansible modules and FTD REST API can be automatically generated from Swagger specification.

1. Complete ["Common environment setup"](../README.md#common-environment-setup) section;

1. Generate docs for Ansible or REST API (check the `--doctype` parameter) by running command from the root project folder:
    
    ```
    python -m docs.build SWAGGER_HOST_URL USERNAME PASSWORD --doctype [ftd-api|ftd-ansible]
    ```
    To generate docs for a few models only, use `--models` parameter:
    ```
    python -m docs.build SWAGGER_HOST_URL USERNAME PASSWORD --models MODEL1 MODEL2
    ```
    To change the distribution folder (by default, `docs/dist` is the output directory), use `--dist` parameter. __The 
    generator recursively removes all files from the distibution folder before generating the docs.__
    ```
    python -m docs.build SWAGGER_HOST_URL USERNAME PASSWORD --dist /tmp/ftd-ansible-docs
    ```
    
