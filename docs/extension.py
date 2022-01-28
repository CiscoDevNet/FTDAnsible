from __future__ import absolute_import, division, print_function

__metaclass__ = type

import collections

import yaml
from jinja2.ext import Extension
from jinja2.nodes import Output

YAML_CODE_TEMPLATE = '```yaml\n{}\n```'


class IncludePlaybookTasks(Extension):
    """
    Custom extension to include tasks from Ansible playbooks to Jinja templates.

    In Jinja templates, it can be used as `include_playbook_tasks` tag:
    {% include_playbook_tasks '/tmp/test.yml' %}

    By default, all tasks are included. To limit the tasks, specify their names as
    the second argument:
    {% include_playbook_tasks '/tmp/test.yml', ["Task1", "Task2"] %}
    """

    tags = {'include_playbook_tasks'}

    def _include_tasks(self, playbook_path, include=None):
        with open(playbook_path, 'r') as playbook_file:
            playbook = ordered_load(playbook_file)[0]

        tasks = playbook.get('tasks', [])
        if include:
            tasks = [t for t in tasks if t['name'] in include]

        tasks_str = '\n'.join([ordered_dump([t], default_flow_style=False) for t in tasks])
        return YAML_CODE_TEMPLATE.format(tasks_str)

    def parse(self, parser):
        def parse_arguments():
            args = [parser.parse_expression()]
            # append task filters if any
            if parser.stream.skip_if('comma'):
                args.append(parser.parse_expression())
            return args

        lineno = next(parser.stream).lineno
        tag_args = parse_arguments()
        call = self.call_method(self._include_tasks.__name__, tag_args)
        return Output([call], lineno=lineno)


# By default, `yaml` package does not preserve field order, and
# playbook tasks do not look the same as in playbooks and in docs.
# These functions create custom Loader and Dumper to preserve field order.
# Source: https://stackoverflow.com/a/21912744

def ordered_load(stream):
    class OrderedLoader(yaml.Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return collections.OrderedDict(loader.construct_pairs(node))

    OrderedLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)
    return yaml.load(stream, OrderedLoader)


def ordered_dump(data, stream=None, **kwds):
    class OrderedDumper(yaml.Dumper):
        pass

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, data.items())

    OrderedDumper.add_representer(collections.OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)
