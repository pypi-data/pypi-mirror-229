from __future__ import annotations
import csv
from io import IOBase
from pathlib import Path

from .text import skip_bom
from . import filesh


def get_csv_headers(csv_file: str|Path|IOBase, encoding: str = 'utf-8', delimiter: str = ';', quotechar: str = '"'):        
    fp = None
    fp_to_close = None

    try:        
        if isinstance(csv_file, (str,Path)):
            fp = filesh.open_file(csv_file, 'r', newline='', encoding=encoding)
            fp_to_close = fp
            if encoding == 'utf-8':
                skip_bom(fp)
        else:
            fp = csv_file
            fp.seek(0)
            
        reader = csv.reader(fp, delimiter=delimiter, quotechar=quotechar)
        try:
            return next(reader)
        except StopIteration:
            return None

    finally:
        if fp_to_close:
            fp_to_close.close()
        elif fp:
            fp.seek(0)
