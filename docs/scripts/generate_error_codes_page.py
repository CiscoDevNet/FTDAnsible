from __future__ import absolute_import, division, print_function

__metaclass__ = type

import argparse
import json

from docs import generator
from docs import build

parser = argparse.ArgumentParser(description='Generates error page')
parser.add_argument('--src', type=str, help='Path to json file with error code definition', required=True)
parser.add_argument('--dist', type=str, help='An output directory for generated page with error codes', required=True)
args = parser.parse_args()

with open(args.src, 'r') as src_file:
    error_codes = json.load(src_file)

generator.ErrorDocGenerator(build.DEFAULT_TEMPLATE_DIR, {}).generate_doc_files(args.dist, error_codes)
