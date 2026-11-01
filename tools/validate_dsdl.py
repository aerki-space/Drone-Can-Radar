#!/usr/bin/env python3
"""Parse dsdl/aerki with the DroneCAN parser and print IDs, max sizes and signatures.

    pip install -r tools/requirements.txt && python3 tools/validate_dsdl.py
"""
import os
import sys

import dronecan
from dronecan import dsdl

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'dsdl', 'aerki')
STD = os.path.join(os.path.dirname(dronecan.__file__), 'dsdl_specs', 'uavcan')

types = [t for t in dsdl.parse_namespaces([ROOT], [STD]) if t.full_name.startswith('aerki.')]
if not types:
    sys.exit('no aerki types found')
for t in sorted(types, key=lambda t: t.full_name):
    if t.kind == t.KIND_SERVICE:
        print(f'{t.full_name:28s} service id {t.default_dtid:5}  request <= {(t.get_max_bitlen_request()+7)//8} B, '
              f'response <= {(t.get_max_bitlen_response()+7)//8} B')
    else:
        dtid = t.default_dtid if t.default_dtid is not None else '-'
        print(f'{t.full_name:28s} message id {dtid:>5}  <= {(t.get_max_bitlen()+7)//8} B  '
              f'signature 0x{t.get_data_type_signature():016x}')
