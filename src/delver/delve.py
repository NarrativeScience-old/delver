#!/usr/bin/env python
# Copyright (c) 2020, Narrative Science
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
# <COPYRIGHT HOLDER> BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.#
"""Delver is a helpful utility for stepping though nested objects"""
from __future__ import absolute_import, print_function

import argparse
import importlib
import json
import logging
import sys

import six

from delver.core import run


def _get_cli_args():
    """Parses and returns arguments passed from CLI.

    :return: parsed command line arguments
    :rtype: :py:class:`argparse.Namespace`
    """
    parser = argparse.ArgumentParser(
        description="Delve into JSON payloads from the command line."
    )
    parser.add_argument(
        "payload", type=argparse.FileType("r"), help="payload file to load"
    )
    parser.add_argument(
        "--transform-func",
        type=six.text_type,
        help=(
            "the module containing the optional json transform function, "
            'formatted like: "transform_module:transform_func". Note that the '
            "transform_func should take only a json-loaded dictionary as "
            "input and should return just the transformed dictionary."
        ),
    )
    return parser.parse_args()


def main():
    """System entry point."""
    my_args = _get_cli_args()

    payload_str = my_args.payload.read()
    try:
        payload = json.loads(payload_str)
    except ValueError:
        sys.exit('"{}" does not contain valid JSON.'.format(my_args.payload.name))

    if my_args.transform_func is not None:
        try:
            # We need to try and import the transform func and use that to
            # convert the payload before exploring
            transform_module_str, transform_func_str = my_args.transform_func.split(":")
            transform_module = importlib.import_module(transform_module_str)
            transform_func = getattr(transform_module, transform_func_str)
            payload = transform_func(payload)
        except ImportError:
            sys.exit(
                "Unable to import module `{}`. Please adjust the "
                "transform-func argument and try again.".format(transform_module_str)
            )
        except AttributeError:
            sys.exit(
                "Unable to import transform function `{}` "
                "from module `{}`. Please adjust the transform-func argument "
                "and try again.".format(transform_func_str, transform_module_str)
            )
        except Exception as error:
            logging.error(
                "Performing the transform function failed with the following "
                "error, please adjust the transform-func argument and try "
                "again:\n {}.".format(error)
            )
            raise error

    del payload_str
    my_args.payload.close()
    run(payload, use_colors=True, verbose=False)


if __name__ == "__main__":
    main()
