# -*- coding: utf-8 -*-

"""

serializable_trees.trees

TraversalPath and Tree data types

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
import json
import pathlib

from typing import List, Dict, Optional, Tuple, Union

import yaml

from serializable_trees import basics


DEFAULT_INDENT = 2

# Type aliases from the basics module
ScalarType = basics.ScalarType
NodeSubclassType = Union[basics.ListNode, basics.MapNode]
BranchType = basics.BranchType

# Types tuples from the basics module for isinstance() checks
SCALAR_TYPES = basics.SCALAR_TYPES
NODE_SUBCLASS_TYPES = (basics.ListNode, basics.MapNode)
BRANCH_TYPES = (*SCALAR_TYPES, *NODE_SUBCLASS_TYPES)


class TraversalPath:

    """A traversal path"""

    def __init__(self, *components: ScalarType) -> None:
        """store the components internally"""
        self.__components: Tuple[ScalarType, ...] = components

    def __eq__(self, other) -> bool:
        """True if both representations are equal"""
        if self.__class__ != other.__class__:
            return False
        #
        return repr(self) == repr(other)

    def __hash__(self) -> int:
        """Return a hash over the representation"""
        return hash(repr(self))

    def __len__(self) -> int:
        """Return the length of the components"""
        return len(self.__components)

    def __repr__(self) -> str:
        """Return a string representation"""
        return (
            f"{self.__class__.__name__}"
            f"({', '.join(repr(item) for item in self.__components)})"
        )

    def traverse(
        self,
        start: BranchType,
    ) -> BranchType:
        """Traverse through a branch starting at the start node,
        and return the node or ScalarType at the end point
        """
        pointer = start
        for key in self.__components:
            if isinstance(pointer, NODE_SUBCLASS_TYPES):
                pointer = pointer[key]  # type: ignore
            else:
                raise TypeError("Cannot traverse through a leaf")
            #
        #
        return pointer

    def partial_walk(
        self,
        start: NodeSubclassType,
        fail_on_missing_keys: bool = True,
        minimum_remaining_components: int = 1,
    ) -> Tuple[NodeSubclassType, List[ScalarType]]:
        """Traverse through a branch starting at the start node,
        and ending minimum_remaining_components before the-last path component.
        If fail_on_missing_keys is True (default setting),
        re-raise the keyError on missing keys. If it is set to false,
        end the walk just before the missing key.
        Return a tuple containing the last node encountered
        and the remaining path component(s).
        """
        if len(self) < minimum_remaining_components:
            raise IndexError(
                f"A minimum of {minimum_remaining_components}"
                f" path component(s) is required, but got only {len(self)}^"
            )
        #
        pointer: BranchType = start
        remaining_components = list(self.__components)
        while len(remaining_components) > minimum_remaining_components:
            if not isinstance(pointer, NODE_SUBCLASS_TYPES):
                raise TypeError("Cannot walk through a leaf")
            #
            key = remaining_components[0]
            try:
                pointer = pointer[key]  # type: ignore
            except KeyError as error:
                if fail_on_missing_keys:
                    raise KeyError(key) from error
                #
                break
            else:
                del remaining_components[0]
            #
        #
        if isinstance(pointer, NODE_SUBCLASS_TYPES):
            return (pointer, remaining_components)
        #
        raise TypeError(
            "End point seems to be a leaf instead of a Node instance"
        )


class Tree:

    """A tree consisting of Nodes and ScalarTypes"""

    def __init__(self, root: BranchType) -> None:
        """Set the root node"""
        if not isinstance(root, BRANCH_TYPES):
            raise basics.ItemTypeInvalid(self)
        #
        self.root: BranchType = root

    def __deepcopy__(self, memo: Dict) -> "Tree":
        """Return a deep copy"""
        return self.__class__(copy.deepcopy(self.root, memo))

    def __eq__(self, other) -> bool:
        """True if both root objects are of the same class and equal"""
        if self.__class__ != other.__class__:
            return False
        #
        return self.root == other.root

    def __repr__(self) -> str:
        """Return a string representation"""
        return f"{self.__class__.__name__}({repr(self.root)})"

    def clone(self) -> "Tree":
        """Return a deep copy"""
        return copy.deepcopy(self)

    def crop(
        self,
        path: TraversalPath,
    ) -> BranchType:
        """Remove and return the item determined by the path
        (hint: "crop" rhymes with "pop").
        The result can be a partial tree (= a branch of nested
        NODE_SUBCLASS_TYPES instances) or a leaf (= a scalar value).
        Might re-raise a KeyError from the underlying Node object
        """
        if not isinstance(self.root, NODE_SUBCLASS_TYPES):
            # Allow cropping a leaf at the root node
            # only with an empty path – seplace the root by an empty
            # MapNode in that case.
            if path:
                raise TypeError("Cannot walk through a leaf")
            #
            root_leaf = self.root
            self.root = basics.MapNode()
            return root_leaf
        #
        parent_node, remaining_components = path.partial_walk(
            self.root, fail_on_missing_keys=True
        )
        last_key = remaining_components[0]
        if isinstance(parent_node, basics.ListNode):
            if isinstance(last_key, int):
                value = parent_node.pop(last_key)
            else:
                raise TypeError(
                    "ListNode keys must be int,"
                    f" not {last_key.__class__.__name__}"
                )
            #
        elif isinstance(parent_node, basics.MapNode):
            value = parent_node.pop(last_key)
        else:
            # Hypothetical branch for the type checker
            raise TypeError(  # NOT TESTABLE
                "parent_node must be either a ListNode or MapNode"
            )
        #
        return value

    def get_branch_clone(self, path: TraversalPath) -> BranchType:
        """Return a deep copy of the item determined by the path.
        The result can be a partial tree (= a branch of nested
        NODE_SUBCLASS_TYPES instances) or a leaf (= a scalar value).
        Might re-raise a KeyError from the underlying Node object
        """
        return copy.deepcopy(self.get_original_branch(path))

    def get_native_item(
        self, path: TraversalPath
    ) -> Union[ScalarType, Dict, List]:
        """Return the native type of the item determined by the path.
        The result can be a list, dict, or ScalarType,
        or any combination of them.
        Might re-raise a KeyError from the underlying Node object
        """
        return basics.native_types(self.get_original_branch(path))

    def get_original_branch(self, path: TraversalPath) -> BranchType:
        """Return the item determined by the path.
        The result can be a partial tree (= a branch of nested
        NODE_SUBCLASS_TYPES instances) or a leaf (= a scalar value).
        Might re-raise a KeyError from the underlying Node object
        """
        return path.traverse(self.root)

    def graft(
        self,
        path: TraversalPath,
        sprout: BranchType,
    ) -> None:
        """Add a sprout on top of the specified path."""
        if not path:
            self.root = sprout
            return
        #
        if not isinstance(self.root, NODE_SUBCLASS_TYPES):
            # Do not allow grafting with a leaf at the root
            raise TypeError("Cannot graft on a leaf")
        #
        last_existing_node, remaining_components = path.partial_walk(
            self.root, fail_on_missing_keys=False
        )
        if len(remaining_components) > 1:
            # build a new intermediate structure using the remaining components
            for new_key in remaining_components[:-1]:
                last_existing_node[new_key] = basics.MapNode()
                pointer = last_existing_node[new_key]  # type: ignore
                # Hypothetical branch for the type checker
                if isinstance(pointer, NODE_SUBCLASS_TYPES):
                    last_existing_node = pointer
                else:
                    raise TypeError(  # NOT TESTABLE
                        "Cannot grow a branch through a leaf"
                    )
                #
            #
        #
        last_existing_node[remaining_components[-1]] = sprout

    def joined_tree(self, other: "Tree", extend_lists: bool = False) -> "Tree":
        """Return a new tree from self and other joined (resp. merged)"""
        return self.__class__(
            basics.merge_branches(
                self.root, other.root, extend_lists=extend_lists
            )
        )

    def truncate(self, path: Optional[TraversalPath] = None) -> None:
        """Truncate the tree at (below) the specified path"""
        if path is None:
            path = TraversalPath()
        #
        if not isinstance(self.root, NODE_SUBCLASS_TYPES):
            # Do not allow a leaf at the root with a path
            if path:
                raise TypeError(
                    f"Cannot truncate using path {path} with a leaf root"
                )
            #
            self.root = basics.MapNode()
            return
        #
        last_remaining_node = path.traverse(self.root)
        if isinstance(last_remaining_node, SCALAR_TYPES):
            parent_node, keys = path.partial_walk(self.root)
            parent_node[keys[0]] = basics.MapNode()
        elif isinstance(last_remaining_node, basics.ListNode):
            while last_remaining_node:
                last_remaining_node.pop()
            #
        elif isinstance(last_remaining_node, basics.MapNode):
            keys = list(last_remaining_node)
            for single_key in keys:
                last_remaining_node.pop(single_key)
            #
        #

    def to_json(
        self,
        indent: Optional[int] = DEFAULT_INDENT,
        sort_keys: bool = False,
    ) -> str:
        """Return a JSON representation"""
        return json.dumps(
            basics.native_types(self.root),
            ensure_ascii=True,
            indent=indent,
            sort_keys=sort_keys,
        )

    def to_yaml(
        self,
        indent: Optional[int] = DEFAULT_INDENT,
        sort_keys: bool = False,
    ) -> str:
        """Return a YAML representation"""
        return yaml.safe_dump(
            basics.native_types(self.root),
            allow_unicode=True,
            default_flow_style=False,
            indent=indent,
            sort_keys=sort_keys,
            explicit_end=False,
        )

    @classmethod
    def from_file(
        cls,
        str_or_path: Union[str, pathlib.Path],
        encoding: str = "utf-8",
    ) -> "Tree":
        """Return a tree from a file"""
        with open(str_or_path, mode="r", encoding=encoding) as input_file:
            serialization = input_file.read()
        #
        return cls.from_yaml(serialization)

    @classmethod
    def from_json(cls, json_serialization: str) -> "Tree":
        """Return a tree from a JSON representation"""
        return cls(basics.grow_branch(json.loads(json_serialization)))

    @classmethod
    def from_yaml(cls, yaml_serialization: str) -> "Tree":
        """Return a tree from a YAML representation"""
        return cls(basics.grow_branch(yaml.safe_load(yaml_serialization)))


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
