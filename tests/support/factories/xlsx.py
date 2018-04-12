#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from collections import OrderedDict

import six


def to_native_dict(ordered_dict):
    return json.loads(json.dumps(ordered_dict))


def to_dict(table_list):
    ordered_dict = OrderedDict(table_list)
    if six.PY3:
        return to_native_dict(ordered_dict)
    else:
        return ordered_dict


CSV_TABLE = [
    to_dict([('Plato', 'Milanesa'), ('Precio', 'Bajo'), ('Sabor', '666')]),
    to_dict([('Plato', 'Thoné, Vitel'), ('Precio', 'Alto'), ('Sabor',
                                                             '8000')]),
    to_dict([('Plato', 'Aceitunas'), ('Precio', ''), ('Sabor', '15')])
]

WRITE_XLSX_TABLE = [
    to_dict([('Plato', 'Milanesa'), ('Precio', 'Bajo'), ('Sabor', 666)]),
    to_dict([('Plato', 'Thoné, Vitel'), ('Precio', 'Alto'), ('Sabor', 8000)]),
    to_dict([('Plato', 'Aceitunas'), ('Precio', None), ('Sabor', 15)])
]

READ_XLSX_TABLE = [
    to_dict([('Plato', 'Milanesa'), ('Precio', 'Bajo'), ('Sabor', 666)]),
    to_dict([('Plato', 'Thoné, Vitel'), ('Precio', 'Alto'), ('Sabor', 8000)]),
    to_dict([('Plato', 'Aceitunas'), ('Sabor', 15)])
]
