# -*- coding: utf-8 -*-

"""

tests.test_trees

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
import os
import pathlib

from tempfile import TemporaryDirectory
from typing import Tuple
from unittest import TestCase

from serializable_trees import basics, trees


SIMPLE_YAML = """levels:
  one:
    two:
      three_1:
      - a
      - b
      - c
      three_2: 999
"""

SIMPLE_JSON_PRETTY = """{
  "levels": {
    "one": {
      "two": {
        "three_1": [
          "a",
          "b",
          "c"
        ],
        "three_2": 999
      }
    }
  }
}"""

SIMPLE_JSON_ONELINE = (
    '{"levels": {"one": {"two": {"three_1": ["a", "b", "c"],'
    ' "three_2": 999}}}}'
)

JOIN_1_YAML = """herbs:
  common:
    - basil
    - oregano
    - parsley
    - thyme
fruits:
vegetables:
  common:
    - bell peppers
    - carrots
    - potatoes
    - tomatoes
  disputed:
    - garlic
    - spinach
"""

JOIN_2_YAML = """fruits:
  - apples
  - bananas
  - oranges
herbs:
  disputed:
    - anise
    - coriander
vegetables:
  disputed:
    - Brussels sprouts
    - celery
    - capers
  trend:
    - eggplant
    - zucchini
"""

EXPECTED_JOINED_TREE_LIST_EXTEND_YAML = """herbs:
  common:
    - basil
    - oregano
    - parsley
    - thyme
  disputed:
    - anise
    - coriander
fruits:
  - apples
  - bananas
  - oranges
vegetables:
  common:
    - bell peppers
    - carrots
    - potatoes
    - tomatoes
  disputed:
    - garlic
    - spinach
    - Brussels sprouts
    - celery
    - capers
  trend:
    - eggplant
    - zucchini
"""

EXPECTED_JOINED_TREE_LIST_REPLACE_YAML = """herbs:
  common:
    - basil
    - oregano
    - parsley
    - thyme
  disputed:
    - anise
    - coriander
fruits:
  - apples
  - bananas
  - oranges
vegetables:
  common:
    - bell peppers
    - carrots
    - potatoes
    - tomatoes
  disputed:
    - Brussels sprouts
    - celery
    - capers
  trend:
    - eggplant
    - zucchini
"""


class FakeTP:

    """Fake object used to test TraversalPath type checks"""

    # pylint: disable=too-few-public-methods ; just required for testing

    def __init__(self, *components: basics.ScalarType) -> None:
        """store the components internally"""
        self.__components: Tuple[basics.ScalarType, ...] = components

    def __repr__(self) -> str:
        """Return a string representation"""
        return (
            "TraversalPath"
            f"({', '.join(repr(item) for item in self.__components)})"
        )

    # pylint: enable=too-few-public-methods


class TraversalPathTest(TestCase):

    """TraversalPath instance"""

    def test_eq(self):
        """__eq__() special method"""
        components_1 = ("abc", 3, None, False)
        components_2 = (1, 5, 7)
        components_3 = (3, None, "abc", False)
        path_1 = trees.TraversalPath(*components_1)
        fake_path_1 = FakeTP(*components_1)
        with self.subTest("equal"):
            self.assertEqual(path_1, trees.TraversalPath(*components_1))
        #
        with self.subTest("not equal", case="different components"):
            self.assertNotEqual(path_1, trees.TraversalPath(*components_2))
        #
        with self.subTest("not equal", case="different components order"):
            self.assertNotEqual(path_1, trees.TraversalPath(*components_3))
        #
        with self.subTest("not equal", case="different type"):
            self.assertEqual(repr(path_1), repr(fake_path_1))
            self.assertNotEqual(path_1, fake_path_1)
        #

    def test_hash(self):
        """__hash__() special method"""
        components_1 = ("abc", 3, None, False)
        components_2 = (1, 5, 7)
        path_1 = trees.TraversalPath(*components_1)
        path_equal_1 = trees.TraversalPath(*components_1)
        path_2 = trees.TraversalPath(*components_2)
        with self.subTest("equal"):
            self.assertEqual(hash(path_1), hash(path_equal_1))
        #
        with self.subTest("not equal", case="different components"):
            self.assertNotEqual(hash(path_1), hash(path_2))
        #

    def test_repr(self):
        """__repr__() special method"""
        with self.subTest("non-empty path"):
            path = trees.TraversalPath("abc", 3, None, False, 7.239)
            self.assertEqual(
                repr(path), "TraversalPath('abc', 3, None, False, 7.239)"
            )
        #
        with self.subTest("empty path"):
            path = trees.TraversalPath()
            self.assertEqual(repr(path), "TraversalPath()")
        #

    def test_len(self):
        """__len__() special method"""
        path = trees.TraversalPath("abc", 3, None, False)
        with self.subTest("non-empty path", scope="length"):
            self.assertEqual(len(path), 4)
        #
        with self.subTest("non-empty path", scope="bool"):
            self.assertTrue(path)
        #
        path = trees.TraversalPath()
        with self.subTest("empty path", sope="length"):
            self.assertEqual(len(path), 0)
        #
        with self.subTest("empty path", scope="bool"):
            self.assertFalse(path)
        #

    def test_traverse(self):
        """traverse() method"""
        simple_tree = trees.Tree.from_yaml(SIMPLE_YAML)
        simple_path = trees.TraversalPath("levels", "one")
        with self.subTest("simple traversal"):
            self.assertEqual(
                simple_path.traverse(simple_tree.root),
                basics.MapNode(
                    two=basics.MapNode(
                        three_1=basics.ListNode(["a", "b", "c"]),
                        three_2=999,
                    ),
                ),
            )
        #
        error_path = trees.TraversalPath(
            "levels", "one", "two", "three_2", "nowhere"
        )
        with self.subTest("traversal error"):
            self.assertRaisesRegex(
                TypeError,
                "^Cannot traverse through a leaf",
                error_path.traverse,
                simple_tree.root,
            )
        #

    def test_partial_walk(self):
        """partial_walk() method"""
        simple_tree = trees.Tree.from_yaml(SIMPLE_YAML)
        error_path = trees.TraversalPath()
        with self.subTest("too short path"):
            self.assertRaisesRegex(
                IndexError,
                r"^A minimum of 1 path component\(s\) is required,"
                r" but got only 0",
                error_path.partial_walk,
                simple_tree.root,
            )
        #
        error_path = trees.TraversalPath(
            "levels", "one", "two", "three_2", "nowhere", "even_worse"
        )
        with self.subTest("too long path - walk through a leaf"):
            self.assertRaisesRegex(
                TypeError,
                "^Cannot walk through a leaf",
                error_path.partial_walk,
                simple_tree.root,
            )
        #
        error_path = trees.TraversalPath("levels", "1", "two", "three_2")
        with self.subTest("non-matching path", option="fail"):
            self.assertRaisesRegex(
                KeyError,
                "^'1'",
                error_path.partial_walk,
                simple_tree.root,
            )
        #
        with self.subTest("non-matching path", option="return"):
            self.assertEqual(
                error_path.partial_walk(
                    simple_tree.root,
                    fail_on_missing_keys=False,
                ),
                (
                    basics.MapNode(
                        one=basics.MapNode(
                            two=basics.MapNode(
                                three_1=basics.ListNode(["a", "b", "c"]),
                                three_2=999,
                            ),
                        ),
                    ),
                    ["1", "two", "three_2"],
                ),
            )
        #
        error_path = trees.TraversalPath(
            "levels", "one", "two", "three_2", "nowhere"
        )
        with self.subTest("too long path - partial walk ends in a leaf"):
            self.assertRaisesRegex(
                TypeError,
                "^End point seems to be a leaf instead of a Node instance",
                error_path.partial_walk,
                simple_tree.root,
            )
        #
        simple_path = trees.TraversalPath("levels", "one", "two")
        with self.subTest("simple partial walk"):
            self.assertEqual(
                simple_path.partial_walk(simple_tree.root),
                (
                    basics.MapNode(
                        two=basics.MapNode(
                            three_1=basics.ListNode(["a", "b", "c"]),
                            three_2=999,
                        ),
                    ),
                    ["two"],
                ),
            )
        #


class TreeTest(TestCase):

    """Tree instance"""

    def test_init(self):
        """__init__() method"""
        with self.subTest("invalid argument"):
            self.assertRaisesRegex(
                basics.ItemTypeInvalid,
                "^Tree items must be either scalar values or Node instances.",
                trees.Tree,
                [],
            )
        #
        with self.subTest("valid argument", type_="Hashable"):
            new_tree = trees.Tree("abc")
            self.assertEqual(new_tree.root, "abc")
        #
        with self.subTest("valid argument", type_="ListNode"):
            new_tree = trees.Tree(basics.ListNode(["c", "d", "e"]))
            self.assertEqual(new_tree.root, basics.ListNode(["c", "d", "e"]))
        #
        with self.subTest("valid argument", type_="MapNode"):
            new_tree = trees.Tree(basics.MapNode(a=1, b=2, c=7))
            self.assertEqual(new_tree.root, basics.MapNode(a=1, b=2, c=7))
        #

    def test_deepcopy(self):
        """__deepcopy__() special method"""
        yaml_tree = trees.Tree.from_yaml(SIMPLE_YAML)
        yaml_tree_clone = copy.deepcopy(yaml_tree)
        #
        with self.subTest("equality"):
            self.assertEqual(yaml_tree, yaml_tree_clone)
        #
        with self.subTest("identity"):
            self.assertIsNot(yaml_tree, yaml_tree_clone)
        #
        with self.subTest("inequality"):
            del yaml_tree.root.levels.one.two
            self.assertNotEqual(yaml_tree, yaml_tree_clone)
        #

    def test_eq(self):
        """__eq__() special method"""
        yaml_tree = trees.Tree.from_yaml(SIMPLE_YAML)
        json_tree = trees.Tree.from_yaml(SIMPLE_JSON_ONELINE)
        fake_branch = basics.MapNode(
            root=yaml_tree.get_branch_clone(trees.TraversalPath())
        )
        with self.subTest("equality"):
            self.assertEqual(yaml_tree, json_tree)
        #
        with self.subTest("inequality", case="different type"):
            self.assertEqual(yaml_tree.root, fake_branch.root)
            self.assertNotEqual(yaml_tree, fake_branch)
        #
        with self.subTest("inequality", case="different tree"):
            del yaml_tree.root.levels.one.two
            self.assertNotEqual(yaml_tree, json_tree)
        #

    def test_repr(self):
        """__repr__() special method"""
        with self.subTest("hashable"):
            simple_tree = trees.Tree("scalar value")
            self.assertEqual(repr(simple_tree), "Tree('scalar value')")
        #
        with self.subTest("list"):
            simple_tree = trees.Tree(
                basics.ListNode(["abc", "def", 555, None])
            )
            self.assertEqual(
                repr(simple_tree), "Tree(['abc', 'def', 555, None])"
            )
        #
        with self.subTest("map node"):
            simple_tree = trees.Tree.from_yaml(SIMPLE_YAML)
            self.assertEqual(
                repr(simple_tree),
                "Tree({'levels': {'one': {'two': "
                "{'three_1': ['a', 'b', 'c'], 'three_2': 999}}}})",
            )
        #

    def test_clone(self):
        """clone() method"""
        yaml_tree = trees.Tree.from_yaml(SIMPLE_YAML)
        yaml_tree_clone = yaml_tree.clone()
        #
        with self.subTest("equality"):
            self.assertEqual(yaml_tree, yaml_tree_clone)
        #
        with self.subTest("identity"):
            self.assertIsNot(yaml_tree, yaml_tree_clone)
        #
        with self.subTest("inequality"):
            del yaml_tree.root.levels.one.two
            self.assertNotEqual(yaml_tree, yaml_tree_clone)
        #

    def test_crop(self):
        """crop() method"""
        root_leaf_tree = trees.Tree("Scalar value")
        with self.subTest("root leaf", using="non-empty path"):
            self.assertRaisesRegex(
                TypeError,
                "^Cannot walk through a leaf",
                root_leaf_tree.crop,
                trees.TraversalPath("key"),
            )
        #
        with self.subTest("root leaf", using="empty path", scope="value"):
            self.assertEqual(
                root_leaf_tree.crop(trees.TraversalPath()), "Scalar value"
            )
        #
        with self.subTest("root leaf", using="empty path", scope="new root"):
            self.assertEqual(root_leaf_tree.root, basics.MapNode())
        #
        simple_tree = trees.Tree.from_yaml(SIMPLE_YAML)
        with self.subTest("invalid ListNode key type"):
            invalid_path = trees.TraversalPath(
                "levels", "one", "two", "three_1", "six"
            )
            self.assertRaisesRegex(
                TypeError,
                "^ListNode keys must be int, not str",
                simple_tree.crop,
                invalid_path,
            )
        #
        with self.subTest("valid ListNode key"):
            valid_path = trees.TraversalPath(
                "levels", "one", "two", "three_1", 1
            )
            self.assertEqual(simple_tree.crop(valid_path), "b")
        #
        with self.subTest("invalid ListNode key"):
            invalid_path = trees.TraversalPath(
                "levels", "one", "two", "three_1", 4
            )
            self.assertRaises(
                IndexError,
                simple_tree.crop,
                invalid_path,
            )
        #
        with self.subTest("valid MapNode key", scope="equality"):
            simple_tree = trees.Tree.from_yaml(SIMPLE_YAML)
            original_node = simple_tree.root.levels.one.two.three_1
            valid_path = trees.TraversalPath("levels", "one", "two", "three_1")
            self.assertEqual(
                simple_tree.crop(valid_path), basics.ListNode(["a", "b", "c"])
            )
        #
        with self.subTest("valid MapNode key", scope="identity"):
            simple_tree = trees.Tree.from_yaml(SIMPLE_YAML)
            original_node = simple_tree.root.levels.one.two.three_1
            valid_path = trees.TraversalPath("levels", "one", "two", "three_1")
            self.assertIs(simple_tree.crop(valid_path), original_node)
        #
        with self.subTest("invalid ListNode key"):
            invalid_path = trees.TraversalPath("levels", "one", "two", "null")
            self.assertRaises(
                KeyError,
                simple_tree.crop,
                invalid_path,
            )
        #
        with self.subTest("invalid: attempted traversal through leaf"):
            # TypeError from the TraversalPath method;
            # Line 148 remains untestable
            invalid_path = trees.TraversalPath(
                "levels", "one", "two", "three_2", "x"
            )
            self.assertRaisesRegex(
                TypeError,
                "^End point seems to be a leaf instead of a Node instance",
                simple_tree.crop,
                invalid_path,
            )
        #

    def test_get_native_item(self):
        """get_native_item() method"""
        simple_tree = trees.Tree.from_yaml(SIMPLE_YAML)
        with self.subTest("get sample native item", subject="leaf"):
            self.assertEqual(
                simple_tree.get_native_item(
                    trees.TraversalPath("levels", "one", "two", "three_1", 1)
                ),
                "b",
            )
        #
        with self.subTest("get sample native item", subject="node"):
            self.assertDictEqual(
                simple_tree.get_native_item(
                    trees.TraversalPath("levels", "one", "two")
                ),
                {"three_1": ["a", "b", "c"], "three_2": 999},
            )
        #

    def test_get_branch_clone(self):
        """get_branch_clone() method"""
        simple_tree = trees.Tree.from_yaml(SIMPLE_YAML)
        original_node = simple_tree.root.levels.one.two
        with self.subTest("get sample clone", subject="equality"):
            self.assertEqual(
                simple_tree.get_branch_clone(
                    trees.TraversalPath("levels", "one", "two")
                ),
                original_node,
            )
        #
        with self.subTest("get sample clone", subject="identity"):
            self.assertIsNot(
                simple_tree.get_branch_clone(
                    trees.TraversalPath("levels", "one", "two")
                ),
                original_node,
            )
        #

    def test_get_original_branch(self):
        """get_original_branch() method"""
        simple_tree = trees.Tree.from_yaml(SIMPLE_YAML)
        original_node = simple_tree.root.levels.one.two
        with self.subTest("get sample branch", subject="equality"):
            self.assertEqual(
                simple_tree.get_original_branch(
                    trees.TraversalPath("levels", "one", "two")
                ),
                original_node,
            )
        #
        with self.subTest("get sample branch", subject="identity"):
            self.assertIs(
                simple_tree.get_original_branch(
                    trees.TraversalPath("levels", "one", "two")
                ),
                original_node,
            )
        #

    def test_graft(self):
        """graft() method"""
        new_node = basics.MapNode(sub1=9, sub2=11, sub3=17)
        root_leaf_tree = trees.Tree("Scalar value")
        with self.subTest("root leaf"):
            self.assertRaisesRegex(
                TypeError,
                "^Cannot graft on a leaf",
                root_leaf_tree.graft,
                trees.TraversalPath("key"),
                new_node,
            )
        #
        with self.subTest("replace root"):
            root_leaf_tree.graft(trees.TraversalPath(), new_node)
            self.assertEqual(root_leaf_tree.root, new_node)
        #
        simple_tree = trees.Tree.from_yaml(SIMPLE_YAML)
        target_path = trees.TraversalPath("levels", "one", "four", "seven")
        simple_tree.graft(target_path, new_node)
        with self.subTest("valid graft", scope="equality"):
            self.assertEqual(
                simple_tree.root.levels.one.four.seven,
                new_node,
            )
        #
        with self.subTest("valid graft", scope="identity"):
            self.assertIs(simple_tree.root.levels.one.four.seven, new_node)
        #
        with self.subTest("invalid graft"):
            self.assertRaisesRegex(
                TypeError,
                "^End point seems to be a leaf instead of a Node instance",
                simple_tree.graft,
                trees.TraversalPath("levels", "one", "two", "three_2", "x"),
                new_node,
            )
        #

    def test_joined_tree(self):
        """joined_tree() function"""
        tree_1 = trees.Tree.from_yaml(JOIN_1_YAML)
        tree_2 = trees.Tree.from_yaml(JOIN_2_YAML)
        with self.subTest("extend lists strategy"):
            result_branch = tree_1.joined_tree(tree_2, extend_lists=True)
            self.assertEqual(
                result_branch,
                trees.Tree.from_yaml(EXPECTED_JOINED_TREE_LIST_EXTEND_YAML),
            )
        #
        with self.subTest("replace lists strategy"):
            result_branch = tree_1.joined_tree(tree_2, extend_lists=False)
            self.assertEqual(
                result_branch,
                trees.Tree.from_yaml(EXPECTED_JOINED_TREE_LIST_REPLACE_YAML),
            )
        #

    def test_truncate(self):
        """truncate() method"""
        root_leaf_tree = trees.Tree("Scalar value")
        with self.subTest("root leaf"):
            self.assertRaisesRegex(
                TypeError,
                r"^Cannot truncate using path TraversalPath\('key'\)"
                " with a leaf root",
                root_leaf_tree.truncate,
                trees.TraversalPath("key"),
            )
        #
        simple_tree = trees.Tree.from_yaml(SIMPLE_YAML)
        with self.subTest("truncate hashable"):
            simple_tree.truncate(
                trees.TraversalPath("levels", "one", "two", "three_2")
            )
            self.assertEqual(
                simple_tree.root.levels.one.two.three_2,
                basics.MapNode(),
            )
        #
        with self.subTest("truncate ListNode"):
            simple_tree.truncate(
                trees.TraversalPath("levels", "one", "two", "three_1")
            )
            self.assertEqual(
                simple_tree.root.levels.one.two.three_1,
                basics.ListNode([]),
            )
        #
        with self.subTest("truncate MapNode"):
            simple_tree.truncate(trees.TraversalPath("levels", "one", "two"))
            self.assertEqual(
                simple_tree.root.levels.one.two,
                basics.MapNode(),
            )
        #
        with self.subTest("truncate all", root_type="MapNode"):
            simple_tree.truncate()
            self.assertEqual(
                simple_tree.root,
                basics.MapNode(),
            )
        #
        with self.subTest("truncate all", root_type="ListNode"):
            list_tree = trees.Tree(basics.ListNode([3, 4, 5, 6]))
            list_tree.truncate()
            self.assertEqual(
                list_tree.root,
                basics.ListNode([]),
            )
        #
        with self.subTest("truncate all", root_type="ListNode"):
            leaf_tree = trees.Tree("leaf")
            leaf_tree.truncate()
            self.assertEqual(
                leaf_tree.root,
                basics.MapNode(),
            )
        #

    def test_to_json(self):
        """to_json() method"""
        simple_tree = trees.Tree.from_yaml(SIMPLE_YAML)
        with self.subTest("pretty json"):
            self.assertEqual(simple_tree.to_json(), SIMPLE_JSON_PRETTY)
        #
        with self.subTest("one-line json"):
            self.assertEqual(
                simple_tree.to_json(indent=None),
                SIMPLE_JSON_ONELINE,
            )
        #

    def test_to_yaml(self):
        """to_json() method"""
        simple_tree = trees.Tree.from_json(SIMPLE_JSON_ONELINE)
        with self.subTest("pretty yaml"):
            self.assertEqual(simple_tree.to_yaml(), SIMPLE_YAML)
        #

    def test_from_file(self):
        """from_file() classmethod"""
        file_name_data_items = {
            "data.json": SIMPLE_JSON_ONELINE,
            "data.yaml": JOIN_2_YAML,
        }.items()
        trees_by_file_name = {
            key: trees.Tree.from_yaml(data)
            for key, data in file_name_data_items
        }
        with TemporaryDirectory() as temp_dir_name:
            for file_name, serialization in file_name_data_items:
                with open(
                    os.path.join(temp_dir_name, file_name),
                    mode="w",
                    encoding="utf-8",
                ) as output_file:
                    output_file.write(serialization)
                #
            #
            base_path = pathlib.Path(temp_dir_name)
            for access_type in ("string", "path"):
                for file_name, serialization in file_name_data_items:
                    if access_type == "path":
                        str_or_path = base_path / file_name
                    else:
                        str_or_path = os.path.join(temp_dir_name, file_name)
                    #
                    loaded_tree = trees.Tree.from_file(str_or_path)
                    with self.subTest(
                        "load from file", str_or_path=str_or_path
                    ):
                        self.assertEqual(
                            loaded_tree,
                            trees_by_file_name[file_name],
                        )
                    #
                #
            #
        #


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
