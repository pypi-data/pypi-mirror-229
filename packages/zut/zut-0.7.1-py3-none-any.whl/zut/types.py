from __future__ import annotations
from typing import Iterable


def get_iterable_element_type(iterable: Iterable, *possible_types: type) -> type|None:
    """
    Get the type of all elements of the iterable amongst the possible types given as argument.
    """
    if not possible_types:
        raise NotImplementedError() # TODO: requires more thinking
    
    remaining_types = list(possible_types)

    for element in iterable:
        types_to_remove = []

        for possible_type in remaining_types:
            if not issubclass(type(element), possible_type):
                types_to_remove.append(possible_type)

        for type_to_remove in types_to_remove:
            remaining_types.remove(type_to_remove)
    
    return remaining_types[0] if remaining_types else None


def is_iterable_of(iterable: Iterable, element_type: type|tuple[type]):
    for element in iterable:
        if not isinstance(element, element_type):
            return False
        
    return True
