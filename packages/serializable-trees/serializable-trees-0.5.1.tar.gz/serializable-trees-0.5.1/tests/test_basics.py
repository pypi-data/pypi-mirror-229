# -*- coding: utf-8 -*-

"""

tests.test_basics

Test the serializable_trees.basics module

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
import re

from unittest import TestCase

import yaml

from serializable_trees import basics


# List of leaves

LI_LV_SRC = """---
- abcd
- 7
- 2.375
- true
- null
"""

LI_LV_TARGET = basics.ListNode(
    [
        "abcd",
        7,
        2.375,
        True,
        None,
    ]
)

# Map of leaves

MA_LV_SRC = """---
7: abcd
2.375: 7
yes: 2.375
null: true
abcd: null
"""

MA_LV_TARGET = basics.MapNode(
    {
        7: "abcd",
        2.375: 7,
        True: 2.375,
        None: True,
        "abcd": None,
    }
)

SIMPLE_YAML = """levels:
  one:
    two:
      three_1:
      - a
      - b
      - c
      three_2: 999
    four: 4.0
    more: original data
"""

MERGE_YAML = """levels:
  one:
    two:
      three_1:
      - g
      - h
      - i
      three_3: new leaf
    more: changed data
xxx: yyy
"""

EXPECTED_MERGE_RESULT_LIST_EXTEND_YAML = """levels:
  one:
    two:
      three_1:
      - a
      - b
      - c
      - g
      - h
      - i
      three_2: 999
      three_3: new leaf
    four: 4.0
    more: changed data
xxx: yyy
"""

EXPECTED_MERGE_RESULT_LIST_REPLACE_YAML = """levels:
  one:
    two:
      three_1:
      - g
      - h
      - i
      three_2: 999
      three_3: new leaf
    four: 4.0
    more: changed data
xxx: yyy
"""


class NodeTest(TestCase):

    """Node base class"""

    def test_contains(self):
        """__contains__() special method"""
        base_node = basics.Node()
        self.assertRaises(
            NotImplementedError,
            base_node.__contains__,
            None,
        )

    def test_len(self):
        """__len__() special method"""
        base_node = basics.Node()
        self.assertRaises(
            NotImplementedError,
            len,
            base_node,
        )

    def test_iter(self):
        """__iter__() special method"""
        base_node = basics.Node()
        self.assertRaises(
            NotImplementedError,
            iter,
            base_node,
        )


class ListNodeTest(TestCase):

    """ListNode class test cases"""

    def test_init(self):
        """__init__() method"""
        list_1 = ["a", "b", "c", [1, 2, 3]]
        self.assertRaisesRegex(
            basics.ItemTypeInvalid,
            "^ListNode items must be either scalar values or Node instances",
            basics.ListNode,
            list_1,
        )

    def test_add(self):
        """__add__() special method"""
        list_1 = ["a", "b", "c"]
        list_2 = [7, None, True, basics.MapNode(a=7, x=99)]
        list_node_1 = basics.ListNode(list_1)
        list_node_2 = basics.ListNode(list_2)
        with self.subTest("adding 2 ListNodes"):
            list_node_3 = list_node_1 + list_node_2
            self.assertEqual(list_node_3, basics.ListNode(list_1 + list_2))
        #
        with self.subTest("adding a ListNode and a list"):
            list_node_4 = list_node_1 + list_2
            self.assertEqual(list_node_4, list_node_3)
        #
        with self.subTest("members", scope="equality"):
            self.assertEqual(list_node_3[-1], list_2[-1])
        #

    def test_eq(self):
        """__eq__() special method"""
        base_node = basics.ListNode(["a", "b", "c"])
        equal_node = basics.ListNode(["a", "b", "c"])
        other_length_node = basics.ListNode(["x", "y"])
        other_order_node = basics.ListNode(["c", "b", "a"])
        other_type_node = basics.MapNode({0: "a", 1: "b", 2: "c"})
        with self.subTest("equal"):
            self.assertEqual(base_node, equal_node)
        #
        with self.subTest("not equal", case="different length"):
            self.assertNotEqual(base_node, other_length_node)
        #
        with self.subTest("not equal", case="different order"):
            self.assertNotEqual(base_node, other_order_node)
        #
        with self.subTest("not equal", case="different type"):
            self.assertNotEqual(base_node, other_type_node)
        #

    def test_iadd(self):
        """__iadd__() special method"""
        list_1 = ["a", "b", "c"]
        list_2 = [7, None, True, basics.MapNode(a=7, x=99)]
        list_node_1 = basics.ListNode(list_1)
        list_node_2 = basics.ListNode(list_2)
        with self.subTest("adding 2 ListNodes"):
            list_node_1 += list_node_2
            self.assertEqual(list_node_1, basics.ListNode(list_1 + list_2))
        #
        with self.subTest("adding a ListNode and a list"):
            list_node_3 = basics.ListNode(list_2)
            list_node_3 += list_1
            self.assertEqual(list_node_3, basics.ListNode(list_2 + list_1))
        #

    def test_deepcopy(self):
        """__deepcopy__() special method"""
        base_node = basics.ListNode(
            [
                basics.ListNode([1, 2, 3]),
                basics.ListNode(["s", "b", "c"]),
            ]
        )
        nested_list_copy = copy.deepcopy(base_node)
        with self.subTest("base node", scope="equality"):
            self.assertEqual(nested_list_copy, base_node)
        #
        with self.subTest("base node", scope="identity"):
            self.assertIsNot(nested_list_copy, base_node)
        #
        for key, item in enumerate(base_node):
            with self.subTest("child node", scope="equality", key=key):
                self.assertEqual(nested_list_copy[key], item)
            #
            with self.subTest("child node", scope="identity", key=key):
                self.assertIsNot(nested_list_copy[key], item)
            #
        #

    def test_reversed(self):
        """__reversed__() special method"""
        example_list = [1, 7, 3, 99, 0, -99, 17, basics.MapNode(a=1, x=25)]
        base_node = basics.ListNode(example_list)
        self.assertEqual(list(reversed(base_node)), example_list[::-1])

    def test_setitem(self):
        """__setitem__() special method"""
        base_node = basics.ListNode([basics.ListNode(["abc"])])
        with self.subTest("regular item setting"):
            base_node[0] = basics.ListNode(["def"])
            self.assertEqual(base_node[0][0], "def")
        #
        with self.subTest("invalid item type"):
            self.assertRaises(
                basics.ItemTypeInvalid,
                base_node.__setitem__,
                0,
                [1, 2, 3],
            )
        #
        with self.subTest("circular growth", scope="child"):
            self.assertRaisesRegex(
                basics.CircularGrowthException,
                r"^Circular reference detected in \[\['def'\]\]",
                base_node.__setitem__,
                0,
                base_node,
            )
        #
        with self.subTest("circular growth", scope="grandchild"):
            self.assertRaisesRegex(
                basics.CircularGrowthException,
                r"^Circular reference detected in \['def'\]",
                base_node[0].__setitem__,
                0,
                base_node,
            )
        #

    def test_append(self):
        """append() method"""
        base_node = basics.ListNode([basics.ListNode(["abc"])])
        with self.subTest("regular append"):
            base_node.append(basics.ListNode(["def"]))
            self.assertEqual(base_node[1][0], "def")
        #
        with self.subTest("invalid item type"):
            self.assertRaises(
                basics.ItemTypeInvalid,
                base_node.append,
                [1, 2, 3],
            )
        #
        with self.subTest("circular growth", scope="child"):
            self.assertRaisesRegex(
                basics.CircularGrowthException,
                r"^Circular reference detected in \[\['abc'\], \['def'\]\]",
                base_node.append,
                base_node,
            )
        #
        with self.subTest("circular growth", scope="grandchild"):
            self.assertRaisesRegex(
                basics.CircularGrowthException,
                r"^Circular reference detected in \['abc'\]",
                base_node[0].append,
                base_node,
            )
        #

    def test_count(self):
        """count() method"""
        example_list = [
            basics.MapNode(a=1, x=25),
            5,
            basics.MapNode(a=1, x=25),
            basics.MapNode(c=3, y=25),
            basics.MapNode(a=1, x=25),
            basics.MapNode(b=2, z="..."),
            9,
            5,
            8,
            0,
        ]
        base_node = basics.ListNode(example_list)
        for item, expected_count in (
            (basics.MapNode(a=1, x=25), 3),
            (basics.MapNode(b=2, z="..."), 1),
            (basics.MapNode(c=3, y=25), 1),
            (5, 2),
            (6, 0),
            (7, 0),
            (8, 1),
            (9, 1),
        ):
            with self.subTest("count", item=item, expected=expected_count):
                self.assertEqual(base_node.count(item), expected_count)
            #
        #

    def test_index(self):
        """count() method"""
        example_list = [
            basics.MapNode(a=1, x=25),
            5,
            basics.MapNode(a=1, x=25),
            basics.MapNode(c=3, y=25),
            basics.MapNode(a=1, x=25),
            basics.MapNode(b=2, z="..."),
            9,
            5,
            8,
            0,
        ]
        base_node = basics.ListNode(example_list)
        for item, expected_index in (
            (basics.MapNode(a=1, x=25), 0),
            (basics.MapNode(b=2, z="..."), 5),
            (basics.MapNode(c=3, y=25), 3),
            (0, 9),
            (5, 1),
            (8, 8),
            (9, 6),
        ):
            with self.subTest("index ok", item=item, expected=expected_index):
                self.assertEqual(base_node.index(item), expected_index)
            #
        #
        for item, args in (
            (basics.MapNode(b=2, z="..."), (0, 4)),
            (basics.MapNode(c=3, y=25), (4,)),
            (9, (0, 5)),
            (6, ()),
            (7, ()),
            ("abc", ()),
            (None, ()),
        ):
            with self.subTest("item not found", item=item, args=args):
                self.assertRaisesRegex(
                    ValueError,
                    f"^{re.escape(repr(item))} is not in list",
                    base_node.index,
                    item,
                    *args,
                )
            #
        #

    def test_insert(self):
        """insert() method"""
        base_node = basics.ListNode([basics.ListNode(["abc"])])
        with self.subTest("regular insert"):
            base_node.insert(0, basics.ListNode(["def"]))
            self.assertEqual(
                base_node,
                basics.ListNode(
                    [
                        basics.ListNode(["def"]),
                        basics.ListNode(["abc"]),
                    ]
                ),
            )
        #
        with self.subTest("invalid item type"):
            self.assertRaises(
                basics.ItemTypeInvalid,
                base_node.insert,
                0,
                [1, 2, 3],
            )
        #
        with self.subTest("circular growth", scope="child"):
            self.assertRaisesRegex(
                basics.CircularGrowthException,
                r"^Circular reference detected in \[\['def'\], \['abc'\]\]",
                base_node.insert,
                1,
                base_node,
            )
        #
        with self.subTest("circular growth", scope="grandchild"):
            self.assertRaisesRegex(
                basics.CircularGrowthException,
                r"^Circular reference detected in \['def'\]",
                base_node[0].insert,
                0,
                base_node,
            )
        #


class MapNodeTest(TestCase):

    """MapNode class test cases"""

    def test_init(self):
        """__init__() method"""
        with self.subTest("invalid item type", argtype="positional"):
            self.assertRaises(
                basics.ItemTypeInvalid,
                basics.MapNode,
                {"pure_list": [1, 2, 3]},
            )
        #
        with self.subTest("invalid item type", argtype="positional"):
            self.assertRaises(
                basics.ItemTypeInvalid,
                basics.MapNode,
                pure_list=[1, 2, 3],
            )
        #

    def test_deepcopy(self):
        """__deepcopy__ special method"""
        base_node = basics.MapNode(
            abcd=basics.MapNode(one=1, two=2, seven=7),
            efgh=basics.MapNode({9: "nine", True: "yes"}),
        )
        nested_list_copy = copy.deepcopy(base_node)
        with self.subTest("base node", scope="equality"):
            self.assertEqual(nested_list_copy, base_node)
        #
        with self.subTest("base node", scope="identity"):
            self.assertIsNot(nested_list_copy, base_node)
        #
        for key in base_node:
            with self.subTest("child node", scope="equality", key=key):
                self.assertEqual(nested_list_copy[key], base_node[key])
            #
            with self.subTest("child node", scope="identity", key=key):
                self.assertIsNot(nested_list_copy[key], base_node[key])
            #
        #

    def test_delattr(self):
        """__delattr__() special method"""
        base_node = basics.MapNode(abc=123, xyz=6753)
        with self.subTest("regular attribute deletion"):
            del base_node.abc
            self.assertEqual(base_node, basics.MapNode(xyz=6753))
        #
        with self.subTest("non-existing attribute"):
            self.assertRaisesRegex(
                AttributeError,
                "^'MapNode' object has no data attribute 'items'",
                base_node.__delattr__,
                "items",
            )
        #

    def test_setattr(self):
        """__setattr__() special method"""
        base_node = basics.MapNode(abc=123)
        with self.subTest("regular attribute setting"):
            base_node.clear_x = 9997
            self.assertEqual(base_node["clear_x"], 9997)
        #

    def test_setitem(self):
        """__setitem__() special method"""
        base_node = basics.MapNode(first=basics.MapNode(value="abc"))
        with self.subTest("regular item setting"):
            base_node["second"] = basics.ListNode(["xyz"])
            self.assertEqual(base_node.second[0], "xyz")
        #
        with self.subTest("invalid item type"):
            self.assertRaises(
                basics.ItemTypeInvalid,
                base_node.__setitem__,
                "pure_list",
                [1, 2, 3],
            )
        #
        with self.subTest("circular growth", scope="child"):
            self.assertRaisesRegex(
                basics.CircularGrowthException,
                "^Circular reference detected in"
                f" {re.escape(repr(base_node))}",
                base_node.__setitem__,
                "third",
                base_node,
            )
        #
        with self.subTest("circular growth", scope="grandchild"):
            self.assertRaisesRegex(
                basics.CircularGrowthException,
                "^Circular reference detected in"
                f" {re.escape(repr(base_node.second))}",
                base_node.second.__setitem__,
                0,
                base_node,
            )
        #
        with self.subTest("circular growth", scope="greatgrandchild"):
            ancestor = basics.MapNode(child=base_node)
            self.assertRaisesRegex(
                basics.CircularGrowthException,
                "^Circular reference detected in"
                f" {re.escape(repr(base_node.first))}",
                base_node.first.__setitem__,
                "loop",
                ancestor,
            )
        #


class HelperFunctionsTest(TestCase):

    """Helper functions"""

    def test_grow_branch(self):
        """grow_branch() function"""
        full_branch = basics.grow_branch(yaml.safe_load(SIMPLE_YAML))
        with self.subTest("equality"):
            self.assertEqual(
                full_branch,
                basics.MapNode(
                    {
                        "levels": basics.MapNode(
                            {
                                "one": basics.MapNode(
                                    {
                                        "two": basics.MapNode(
                                            {
                                                "three_1": basics.ListNode(
                                                    ["a", "b", "c"]
                                                ),
                                                "three_2": 999,
                                            }
                                        ),
                                        "four": 4.0,
                                        "more": "original data",
                                    }
                                ),
                            }
                        ),
                    }
                ),
            )
        #
        with self.subTest("invalid branch grow item", target="message"):
            self.assertRaises(
                TypeError,
                basics.grow_branch,
                [1, 2, 3, set([1, 3])],
            )
        #

    def test_native_types(self):
        """native_types() function"""
        full_branch = basics.grow_branch(yaml.safe_load(SIMPLE_YAML))
        with self.subTest("equality"):
            self.assertEqual(
                basics.native_types(full_branch),
                {
                    "levels": {
                        "one": {
                            "two": {
                                "three_1": ["a", "b", "c"],
                                "three_2": 999,
                            },
                            "four": 4.0,
                            "more": "original data",
                        }
                    }
                },
            )

    def test_merge_branches(self):
        """merge_branches() function"""
        full_branch = basics.grow_branch(yaml.safe_load(SIMPLE_YAML))
        to_merge_branch = basics.grow_branch(yaml.safe_load(MERGE_YAML))
        with self.subTest("extend lists strategy"):
            result_branch = basics.merge_branches(
                full_branch, to_merge_branch, extend_lists=True
            )
            self.assertEqual(
                result_branch,
                basics.grow_branch(
                    yaml.safe_load(EXPECTED_MERGE_RESULT_LIST_EXTEND_YAML)
                ),
            )
        #
        with self.subTest("replace lists strategy"):
            result_branch = basics.merge_branches(
                full_branch, to_merge_branch, extend_lists=False
            )
            self.assertEqual(
                result_branch,
                basics.grow_branch(
                    yaml.safe_load(EXPECTED_MERGE_RESULT_LIST_REPLACE_YAML)
                ),
            )
        #


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
