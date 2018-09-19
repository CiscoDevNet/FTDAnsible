# FTD Ansible Documentation

Documentation for FTD Ansible modules is written with the help of [reStructuredText](http://docutils.sourceforge.net/rst.html)
markup language that is translated to HTML using [Sphinx](http://www.sphinx-doc.org/en/master/) documentation generator.

### Doc Generation for Models and Operations

Docs for models and operations are automatically generated from Swagger specification using `generator.py` file. The 
generator can be run using the following command:
```
python generator.py SWAGGER_HOST_URL USERNAME PASSWORD
```
To generate docs for a few models only, use the `--models` parameter:
```
python generator.py SWAGGER_HOST_URL USERNAME PASSWORD --models MODEL1 MODEL2
```

### HTML Generation

HTML files are generated from reStructuredText with the help of Sphinx.
```
pip install sphinx
make html
```
