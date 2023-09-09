from __future__ import annotations

import re
import unicodedata
from io import BufferedIOBase, TextIOWrapper
from typing import Generic, Iterable, TypeVar
from urllib.parse import quote, urlunparse

T = TypeVar('T')


class ValueString(str, Generic[T]):
    """
    A string internally associated to a value of a given type.
    """
    value: T

    def __new__(cls, strvalue: str, value: T):
        hb = super().__new__(cls, strvalue)
        hb.value = value
        return hb


def slugify(value: str, separator: str = '-', keep: str = '_', strip_separator: bool = True, strip_keep: bool = True) -> str:
    """ 
    Generate a slug.

    Compatible by default with `slugify` function from `django.utils.text.slugify`,
    but allows to change the default behavior.
    """
    separator = separator if separator is not None else ''
    keep = keep if keep is not None else ''

    # Normalize the string: replace diacritics by standard characters, lower the string, etc
    value = str(value)
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.lower()

    # Remove special characters
    remove_sequence = r'^a-zA-Z0-9\s' + re.escape(separator) + re.escape(keep)
    value = re.sub(f"[{remove_sequence}]", "", value)

    # Replace spaces and successive separators by a single separator
    replace_sequence = r'\s' + re.escape(separator)
    value = re.sub(f"[{replace_sequence}]+", separator, value)
    
    # Strips separator and kept characters
    strip_chars = (separator if strip_separator else '') + (keep if strip_keep else '')
    value = value.strip(strip_chars)

    return value


def slugify_snake(value: str, allow_unicode: bool = False) -> str:
    """
    CamèlCase => camel_case
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    
    value = re.sub(r"[^\w\s-]", "", value) # not .lower()
    value = re.sub(r"[-_\s]+", '_', value).strip('_')
    value = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', value)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', value).lower()


def remove_consecutive_whitespaces(s: str):
    if s is None:
        return None
    return re.sub(r'\s+', ' ', s).strip()


def remove_whitespaces(s):
    if s is None:
        return None
    return re.sub(r'\s', '', s)


def skip_bom(fp: TextIOWrapper|BufferedIOBase) -> str:
    """
    Reconfigure utf-8 encoding to handle the BOM if any.
    """
    data = fp.read(1)
    
    if isinstance(data, str): # text mode
        if len(data) >= 1 and data[0] == '\ufeff':
            return 'utf-8'
        
    elif isinstance(data, bytes): # binary mode
        if len(data) >= 1 and data[0] == _UTF8_BOM_BINARY[0]:
            data += fp.read(2)
            if data[0:3] == _UTF8_BOM_BINARY:
                return 'utf-8'
    
    fp.seek(0)
    return None

_UTF8_BOM_BINARY = '\ufeff'.encode('utf-8')


def build_uri(*, scheme: str = '', host: str = None, port: int = None, user: str = None, password: str = None, path: str = None, params: str = None, query: str = None, fragment: str = None, hide_password = False):
    netloc = build_netloc(host=host, port=port, user=user, password=password, hide_password=hide_password)
    return urlunparse((scheme or '', netloc or '', path or '', params or '', query or '', fragment or ''))


def build_netloc(*, host: str = None, port: int = None, user: str = None, password: str = None, hide_password = False):
    netloc = ''
    if user or host:
        if user:
            netloc += quote(user)
            if password:
                netloc += ':' + ('***' if hide_password else quote(password))
            netloc += '@'

        if host:
            netloc += quote(host)
            if port:
                netloc += f':{port}'

    return netloc


class StringFilter:
    def __init__(self, value: str, on_normalized: bool = False):
        self.value = value
        self.on_normalized = on_normalized

        if self.on_normalized:
            value = self.normalize(value)

        if '*' in value:
            name_parts = value.split('*')
            pattern_parts = [re.escape(name_part) for name_part in name_parts]
            pattern = r'^' + r'.*'.join(pattern_parts) + r'$'
            self.filter = re.compile(pattern)
        else:
            self.filter = value


    def matches(self, value: str, is_normalized: bool = False):
        if self.on_normalized and not is_normalized:
            value = self.normalize(value)

        if isinstance(self.filter, re.Pattern):
            if self.filter.match(value):
                return True
            
        elif self.filter == value:
            return True
       

    def __repr__(self) -> str:
        return self.filter.pattern if isinstance(self.filter, re.Pattern) else self.filter
        

    @classmethod
    def normalize(cls, value):
        return slugify(value, separator=None, keep='*', strip_keep=False)

    @classmethod
    def matches_any(cls, value, str_filters: Iterable[StringFilter]):
        if not str_filters:
            return False
        
        if value is None:
            value = ""
        
        normalized_value = None    

        for str_filter in str_filters:
            if str_filter.on_normalized:
                if normalized_value is None:
                    normalized_value = slugify(value, separator=None, keep=None)
                if str_filter.matches(normalized_value, is_normalized=True):
                    return True
            else:
                if str_filter.matches(value):
                    return True
                
        return False
