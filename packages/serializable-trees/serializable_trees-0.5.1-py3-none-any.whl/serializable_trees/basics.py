# -*- coding: utf-8 -*-

"""

serializable_trees.basics

Basic data types

Copyright (C) 2023 Rainer Schwarzbach

This file is part of serializable_trees.

serializable_trees is free software:
you can redistribute it and/or modify it under the terms of the MIT License.

serializable_trees is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the LICENSE file for more details.

"""


import copy

from collections.abc import Collection
from typing import Dict, List, Optional, SupportsIndex, Union


# Type alias: scalar type
ScalarType = Union[bool, float, int, str, None]

# Types tuple for isinstance() checks; scalar types
SCALAR_TYPES = (bool, float, int, str, type(None))


class CircularGrowthException(Exception):

    """Raised on detected circular growth"""

    def __init__(self, affected_instance) -> None:
        """Store the affected instance for output"""
        self.affected_instance = affected_instance

    def __str__(self) -> str:
        """String representation"""
        return f"Circular reference detected in {self.affected_instance}"


class ItemTypeInvalid(TypeError):

    """Raised on invalid item types"""

    def __init__(self, affected_instance) -> None:
        """Initialize the super class"""
        super().__init__(
            f"{affected_instance.__class__.__name__} items must be"
            " either scalar values or Node instances."
        )


class Node(Collection):

    """Abstract node // containing ScalarTypes or other nodes"""

    def __contains__(self, item):
        """Return true if the collection
        contains the specified item
        """
        raise NotImplementedError

    def __iter__(self):
        """iterator over self"""
        raise NotImplementedError

    def __len__(self):
        """length of self"""
        raise NotImplementedError

    def _avoid_circular_growth(self, *ancestors: "Node") -> None:
        """Raise CircularGrowthException
        if self is any of the ancestors – or self – appears
        in the collection or any contained node at any level
        """
        child_ancestors: List[Node] = [self]
        for single_ancestor in ancestors:
            if self is single_ancestor:
                raise CircularGrowthException(self)
            #
            child_ancestors.append(single_ancestor)
        #
        if isinstance(self, dict):
            values_iterable: Collection = self.values()
        else:
            values_iterable = self
        #
        for child in values_iterable:
            if isinstance(child, Node):
                # pylint: disable = protected-access
                child._avoid_circular_growth(*child_ancestors)
            #
        #


# Type alias: branch (item) type
BranchType = Union["ListNode", "MapNode", bool, float, int, str, None]

# Types tuple for isinstance() checks: branch (item) types
BRANCH_TYPES = (bool, float, int, str, type(None), Node)


class ListNode(list, Node):

    """List node containing a list of scalars and/or other nodes"""

    def __init__(self, sequence) -> None:
        """Store the sequence internally"""
        collection: List[BranchType] = list(sequence)
        if not all(isinstance(item, BRANCH_TYPES) for item in sequence):
            raise ItemTypeInvalid(self)
        #
        super().__init__(collection)

    def __setitem__(self, key, value) -> None:
        """Set the specified item in the internal collection"""
        if isinstance(value, Node):
            value._avoid_circular_growth(self)
        elif not isinstance(value, SCALAR_TYPES):
            raise ItemTypeInvalid(self)
        #
        super().__setitem__(key, value)

    def append(self, item: BranchType) -> None:
        """Append an item to the internal list"""
        if isinstance(item, Node):
            # pylint: disable = protected-access
            item._avoid_circular_growth(self)
        elif not isinstance(item, SCALAR_TYPES):
            raise ItemTypeInvalid(self)
        #
        super().append(item)

    def insert(self, key: SupportsIndex, item: BranchType) -> None:
        """Insert an item into the internal list"""
        if isinstance(item, Node):
            # pylint: disable = protected-access
            item._avoid_circular_growth(self)
        elif not isinstance(item, SCALAR_TYPES):
            raise ItemTypeInvalid(self)
        #
        super().insert(key, item)


class MapNode(dict, Node):

    """Map node containing a dict of scalars and/or other nodes"""

    def __init__(self, mapping: Optional[Dict] = None, **kwargs) -> None:
        """Store the collection internally"""
        collection: Dict[ScalarType, Union[ScalarType, Node]] = dict(
            mapping or {}
        )
        if not all(
            isinstance(item, BRANCH_TYPES) for key, item in collection.items()
        ):
            raise ItemTypeInvalid(self)
        #
        for key, value in kwargs.items():
            if not isinstance(value, BRANCH_TYPES):
                raise ItemTypeInvalid(self)
            #
            collection[key] = value
        #
        super().__init__(collection)

    def __getattr__(self, name: str) -> BranchType:
        """Get an item (indexed by a string) as attribute"""
        try:
            return self[name]
        except KeyError as error:
            raise AttributeError(
                f"{self.__class__.__name__!r} object has no attribute {name!r}"
            ) from error
        #

    def __setattr__(self, name: str, value: BranchType) -> None:
        """Set an item (indexed by a string) as attribute"""
        self[name] = value

    def __delattr__(self, name: str) -> None:
        """Delete an item (indexed by a string) from the attributes"""
        try:
            del self[name]
        except KeyError as error:
            raise AttributeError(
                f"{self.__class__.__name__!r} object has no"
                f" data attribute {name!r}"
            ) from error
        #

    def __setitem__(self, key, value: BranchType) -> None:
        """Set the specified item in the internal collection"""
        if isinstance(value, Node):
            value._avoid_circular_growth(self)
        elif not isinstance(value, SCALAR_TYPES):
            raise ItemTypeInvalid(self)
        #
        super().__setitem__(key, value)


#
# Module-level functions
#


def grow_branch(data_structure: Union[ScalarType, Dict, List]) -> BranchType:
    """Factory function: return nested nodes"""
    if isinstance(data_structure, SCALAR_TYPES):
        return copy.deepcopy(data_structure)
    #
    if isinstance(data_structure, dict):
        return MapNode(
            {key: grow_branch(item) for key, item in data_structure.items()}
        )
    #
    if isinstance(data_structure, list):
        return ListNode(grow_branch(item) for item in data_structure)
    #
    raise TypeError(
        "Branches can only be grown from nested dicts and/or lists"
        " of scalar values."
    )


def native_types(branch_root: BranchType) -> Union[ScalarType, Dict, List]:
    """Return native types from nested Node instances"""
    if isinstance(branch_root, SCALAR_TYPES):
        return branch_root
    #
    if isinstance(branch_root, MapNode):
        return {key: native_types(value) for key, value in branch_root.items()}
    #
    if isinstance(branch_root, ListNode):
        return [native_types(item) for item in branch_root]
    #
    # Hypothetical statement for the type checker
    raise ItemTypeInvalid(branch_root)  # NOT TESTABLE


def merge_branches(
    branch_1: BranchType,
    branch_2: BranchType,
    extend_lists: bool = False,
) -> BranchType:
    """Return a new branch containing branch_2
    merged into branch_1.
    """
    if isinstance(branch_1, MapNode) and isinstance(branch_2, MapNode):
        new_map = MapNode()
        seen_in_branch_2 = set()
        for key in branch_1:
            try:
                new_map[key] = merge_branches(
                    branch_1[key], branch_2[key], extend_lists=extend_lists
                )
            except KeyError:
                new_map[key] = copy.deepcopy(branch_1[key])
            else:
                seen_in_branch_2.add(key)
            #
        #
        for key in branch_2:
            if key in seen_in_branch_2:
                continue
            #
            new_map[key] = copy.deepcopy(branch_2[key])
        #
        return new_map
    #
    if isinstance(branch_1, ListNode) and isinstance(branch_2, ListNode):
        new_list = ListNode([])
        if extend_lists:
            for item in branch_1:
                new_list.append(copy.deepcopy(item))
            #
        #
        for item in branch_2:
            new_list.append(copy.deepcopy(item))
        #
        return new_list
    #
    return grow_branch(native_types(branch_2))


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
