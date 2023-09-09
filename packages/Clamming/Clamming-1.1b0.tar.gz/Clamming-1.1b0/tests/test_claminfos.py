# test_claminfos.py
#
# This file is part of Clamming tool.
# (C) 2023 Brigitte Bigi, Laboratoire Parole et Langage,
# Aix-en-Provence, France.
#
# Use of this software is governed by the GNU Public License, version 3.
#
# Clamming is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Clamming is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Clamming. If not, see <http://www.gnu.org/licenses/>.
#
# This banner notice must not be removed.
# ---------------------------------------------------------------------------

import unittest

from clamming import ClamInfo
from clamming import ClamInfoMarkdown

# ---------------------------------------------------------------------------


class TestClamInfo(unittest.TestCase):
    def test_clam_info_creation(self):
        clam_info = ClamInfo(
            name="test_function",
            args=["arg1", "arg2"],
            source="def test_function(arg1, arg2): pass",
            docstring="Test function docstring."
        )

        self.assertEqual(clam_info.name, "test_function")
        self.assertEqual(clam_info.args, ["arg1", "arg2"])
        self.assertEqual(clam_info.source, "def test_function(arg1, arg2): pass")
        self.assertEqual(clam_info.docstring, "Test function docstring.")

# ---------------------------------------------------------------------------


class TestClamInfoMarkdown(unittest.TestCase):
    def setUp(self):
        self.clam_info = ClamInfo(
            name="test_function",
            args=["arg1", "arg2"],
            source="def test_function(arg1, arg2): pass",
            docstring="Test function docstring."
        )

    def test_constructor(self):
        ClamInfoMarkdown(self.clam_info)

    def test_convert_name(self):
        converted_name = ClamInfoMarkdown.convert_name("test_function")
        self.assertEqual(converted_name, "#### test_function")

    def test_convert_source(self):
        converted_source = ClamInfoMarkdown.convert_source("def test_function(arg1, arg2): pass")
        expected_source = "\n```python\ndef test_function(arg1, arg2): pass\n```\n"
        self.assertEqual(converted_source, expected_source)

    def test_convert_docstring(self):
        # One line docstring. Summary.
        converted_docstring = ClamInfoMarkdown.convert_docstring("Test function docstring.")
        expected_docstring = "*Test function docstring.*"
        self.assertEqual(converted_docstring, expected_docstring)

        # One line docstring.
        converted_docstring = ClamInfoMarkdown.convert_docstring("Test function docstring")
        expected_docstring = "Test function docstring"
        self.assertEqual(converted_docstring, expected_docstring)

        # parameter. single line description
        d = """
        :param obj: Any class object; its source code must be available"""
        converted_docstring = ClamInfoMarkdown.convert_docstring(d)
        expected_docstring = "\n###### Parameters\n\n- **obj**: Any class object; its source code must be available"
        self.assertEqual(converted_docstring, expected_docstring)

        # parameter. description is multilines
        d = """
                :param obj: Any class object; 
                its source code must be available"""
        converted_docstring = ClamInfoMarkdown.convert_docstring(d)
        expected_docstring = "\n###### Parameters\n\n- **obj**: Any class object; its source code must be available"
        self.assertEqual(converted_docstring, expected_docstring)

        # parameter. with type below
        d = """
                :param a: description
                :type: int"""
        converted_docstring = ClamInfoMarkdown.convert_docstring(d)
        expected_docstring = "\n###### Parameters\n\n- **a**: description"
        self.assertEqual(converted_docstring, expected_docstring)

        # raise single line
        d = """
                :raise: Exception"""
        converted_docstring = ClamInfoMarkdown.convert_docstring(d)
        expected_docstring = "\n###### Raises\n\nException"
        self.assertEqual(converted_docstring, expected_docstring)

        # raise several
        d = """
                :raise ValueError: if value error
                :raise TypeError: if type error"""
        converted_docstring = ClamInfoMarkdown.convert_docstring(d)
        expected_docstring = "\n###### Raises\n\n- *ValueError*: if value error\n- *TypeError*: if type error"
        self.assertEqual(expected_docstring, converted_docstring)

        # example - single line
        d = """
                :example: a = fct(2)"""
        converted_docstring = ClamInfoMarkdown.convert_docstring(d)
        expected_docstring = "\n###### Example\n\n    >>> a = fct(2)"
        self.assertEqual(converted_docstring, expected_docstring)

        # example - multi lines
        d = """
                :example:
                a = fct(2)
                b = a + fct(1)"""
        converted_docstring = ClamInfoMarkdown.convert_docstring(d)
        expected_docstring = "\n###### Example\n\n    >>> a = fct(2)\n    >>> b = a + fct(1)"
        self.assertEqual(converted_docstring, expected_docstring)

        # More tests should be added here!

# ---------------------------------------------------------------------------


class TestFieldnameVariant(unittest.TestCase):

    def test_fieldname_variant_returns(self):
        field = ClamInfoMarkdown._fieldname_variant("return")
        self.assertEqual(field, "return")

    def test_fieldname_variant_returns_uppercase(self):
        field = ClamInfoMarkdown._fieldname_variant("Returns")
        self.assertEqual(field, "return")

    def test_fieldname_variant_raises(self):
        field = ClamInfoMarkdown._fieldname_variant("raises")
        self.assertEqual(field, "raise")

    def test_fieldname_variant_catch(self):
        field = ClamInfoMarkdown._fieldname_variant("Catch")
        self.assertEqual(field, "raise")

    def test_fieldname_variant_except(self):
        field = ClamInfoMarkdown._fieldname_variant("except")
        self.assertEqual(field, "raise")

    def test_fieldname_variant_code(self):
        field = ClamInfoMarkdown._fieldname_variant("code")
        self.assertEqual(field, "example")

    def test_fieldname_variant_unknown(self):
        field = ClamInfoMarkdown._fieldname_variant("  UNKNOWN  ")
        self.assertEqual(field, "unknown")

# ---------------------------------------------------------------------------


class TestExtractFieldname(unittest.TestCase):

    def test_extract_fieldname_empty_text(self):
        field_name, content = ClamInfoMarkdown._extract_fieldname("")
        self.assertIsNone(field_name)
        self.assertEqual(content, "")

    def test_extract_fieldname_no_field_start(self):
        field_name, content = ClamInfoMarkdown._extract_fieldname("This: is not a field.")
        self.assertIsNone(field_name)
        self.assertEqual(content, "This: is not a field.")

        field_name, content = ClamInfoMarkdown._extract_fieldname("This is not a field.")
        self.assertIsNone(field_name)
        self.assertEqual(content, "This is not a field.")

        field_name, content = ClamInfoMarkdown._extract_fieldname(":This is not a field.")
        self.assertIsNone(field_name)
        self.assertEqual(content, ":This is not a field.")

    def test_extract_fieldname_valid_epydoc_field(self):
        field_name, content = ClamInfoMarkdown._extract_fieldname("@param name: THE name")
        self.assertEqual(field_name, "param")
        self.assertEqual(content, "name: THE name")

    def test_extract_fieldname_valid_rest_field(self):
        field_name, content = ClamInfoMarkdown._extract_fieldname(":param name: THE name")
        self.assertEqual(field_name, "param")
        self.assertEqual(content, "name: THE name")

    def test_extract_fieldname_empty_field(self):
        field_name, content = ClamInfoMarkdown._extract_fieldname(":Return: ")
        self.assertEqual(field_name, "return")
        self.assertEqual(content, "")
        field_name, content = ClamInfoMarkdown._extract_fieldname(":example:")
        self.assertEqual(field_name, "example")
        self.assertEqual(content, "")

    def test_extract_fieldname_valid_return_field(self):
        # With whitespace
        field_name, content = ClamInfoMarkdown._extract_fieldname(":return: Something")
        self.assertEqual(field_name, "return")
        self.assertEqual(content, "Something")
        # Without whitespace
        field_name, content = ClamInfoMarkdown._extract_fieldname(":return:Something")
        self.assertEqual(field_name, "return")
        self.assertEqual(content, "Something")

    def test_extract_fieldname_variant_field(self):
        field_name, content = ClamInfoMarkdown._extract_fieldname(":catch: Something")
        self.assertEqual(field_name, "raise")
        self.assertEqual(content, "Something")

# ---------------------------------------------------------------------------


class TestPtype(unittest.TestCase):
    def test_ptype_single_type(self):
        converted_text = ClamInfoMarkdown._ptype("(str)")
        self.assertEqual(converted_text, "(*str*)")

    def test_ptype_multiple_types(self):
        converted_text = ClamInfoMarkdown._ptype("(str,int)")
        self.assertEqual(converted_text, "(*str*,*int*)")

    def test_ptype_inside_list(self):
        converted_text = ClamInfoMarkdown._ptype("(list(str))")
        self.assertEqual(converted_text, "(*list*(*str*))")
        converted_text = ClamInfoMarkdown._ptype("list(str)")
        self.assertEqual(converted_text, "list(*str*)")
        converted_text = ClamInfoMarkdown._ptype("(list[str])")
        self.assertEqual(converted_text, "(*list*[*str*])")

    def test_ptype_no_parentheses(self):
        converted_text = ClamInfoMarkdown._ptype("(any)")
        self.assertEqual(converted_text, "(any)")

    def test_ptype_text_only(self):
        converted_text = ClamInfoMarkdown._ptype("some text")
        self.assertEqual(converted_text, "some text")

    def test_ptype_text_with_whitespace(self):
        converted_text = ClamInfoMarkdown._ptype(" (some text) ")
        self.assertEqual(converted_text, "(some text)")

# ---------------------------------------------------------------------------


class TestParam(unittest.TestCase):
    def test_param_no_colon(self):
        converted_text = ClamInfoMarkdown._param("THE name")
        self.assertEqual(converted_text, "THE name")

    def test_param_basic(self):
        converted_text = ClamInfoMarkdown._param("name: THE name")
        self.assertEqual(converted_text, "- **name**: THE name")

    def test_param_with_type(self):
        converted_text = ClamInfoMarkdown._param("name: (str) THE name")
        self.assertEqual(converted_text, "- **name**: (*str*) THE name")
        converted_text = ClamInfoMarkdown._param("name: (str|int) THE name")
        self.assertEqual(converted_text, "- **name**: (*str*|*int*) THE name")

    def test_param_whitespace(self):
        converted_text = ClamInfoMarkdown._param(" name : (str) THE name ")
        self.assertEqual(converted_text, "- **name**: (*str*) THE name")

# ---------------------------------------------------------------------------


class TestReturn(unittest.TestCase):
    def test_return_basic(self):
        converted_text = ClamInfoMarkdown._return("THE name")
        self.assertEqual(converted_text, "- THE name")

    def test_return_with_type(self):
        converted_text = ClamInfoMarkdown._return("(str|int) THE name")
        self.assertEqual(converted_text, "- (*str*|*int*) THE name")

    def test_return_with_tag(self):
        converted_text = ClamInfoMarkdown._return("tag: THE name")
        self.assertEqual(converted_text, "- **tag**: THE name")

    def test_return_empty_description(self):
        converted_text = ClamInfoMarkdown._return("tag:")
        self.assertEqual(converted_text, "- **tag**")

    def test_return_whitespace(self):
        converted_text = ClamInfoMarkdown._return("   tag  :   (str)   THE name   ")
        self.assertEqual(converted_text, "- **tag**: (*str*)   THE name")

# ---------------------------------------------------------------------------


class TestRaise(unittest.TestCase):
    def test_raise_basic(self):
        converted_text = ClamInfoMarkdown._raise("THE error")
        self.assertEqual(converted_text, "THE error")

    def test_raise_with_exception(self):
        converted_text = ClamInfoMarkdown._raise("ValueError: THE problem")
        self.assertEqual(converted_text, "- *ValueError*: THE problem")

    def test_raise_empty_description(self):
        converted_text = ClamInfoMarkdown._raise("ValueError:")
        self.assertEqual(converted_text, "- *ValueError*")

    def test_raise_whitespace(self):
        converted_text = ClamInfoMarkdown._raise("   ValueError  :   THE problem   ")
        self.assertEqual(converted_text, "- *ValueError*: THE problem")

# ---------------------------------------------------------------------------


class TestExample(unittest.TestCase):
    def test_example_with_gtgtgt(self):
        converted_text = ClamInfoMarkdown._example(">>>print('Hello')")
        self.assertEqual(converted_text, "    >>> print('Hello')")

    def test_example_without_gtgtgt(self):
        converted_text = ClamInfoMarkdown._example("print('Hello')")
        self.assertEqual(converted_text, "    >>> print('Hello')")

    def test_example_empty_line(self):
        converted_text = ClamInfoMarkdown._example(">>>")
        self.assertEqual(converted_text, "    >>> ")

    def test_example_whitespace(self):
        converted_text = ClamInfoMarkdown._example("   >>>   print('Hello')   ")
        self.assertEqual(converted_text, "    >>> print('Hello')")

# ---------------------------------------------------------------------------


class TestPlist(unittest.TestCase):
    def test_plist_with_description(self):
        converted_text = ClamInfoMarkdown._plist(":Author: someone")
        self.assertEqual(converted_text, "- **Author**: someone")

    def test_plist_without_description(self):
        converted_text = ClamInfoMarkdown._plist(":Author: ")
        self.assertEqual(converted_text, "- **Author**")

    def test_plist_no_colon(self):
        converted_text = ClamInfoMarkdown._plist("Author: no ")
        self.assertEqual(converted_text, "Author: no")

    def test_plist_whitespace(self):
        converted_text = ClamInfoMarkdown._plist("  :Tag   :   Some description   ")
        self.assertEqual(converted_text, "- **Tag**: Some description")
