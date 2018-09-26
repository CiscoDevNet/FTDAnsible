# FTD Ansible Documentation

Documentation for FTD Ansible modules is written using [Markdown](https://daringfireball.net/projects/markdown/)
markup language with [Github Flavor](https://gist.github.com/stevenyap/7038119). Docs describing models
and operations are automatically generated from Swagger specification using [Jinja](http://jinja.pocoo.org/)
template engine. 

`docsite` folder contains static and generated doc files that are published on [DevNet](https://developer.cisco.com/)
 using PubHub. PubHub takes care of fetching the latest docs from the repository, converting them to HTML and
 hosting on the web site.

### Doc Generation for Models and Operations

Docs for models and operations can be automatically generated from Swagger using the following command:
```
python generator.py SWAGGER_HOST_URL USERNAME PASSWORD
```
To generate docs for a few models only, use the `--models` parameter:
```
python generator.py SWAGGER_HOST_URL USERNAME PASSWORD --models MODEL1 MODEL2
```
