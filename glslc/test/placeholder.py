# Copyright 2015 The Shaderc Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A number of placeholders and their rules for expansion when used in tests.

These placeholders, when used in glslc_args or expected_* variables of
GlslCTest, have special meanings. In glslc_args, they will be substituted by
the result of instantiate_for_glslc_args(), while in expected_*, by
instantiate_for_expectation(). A TestCase instance will be passed in as
argument to the instantiate_*() methods.
"""
import os
import tempfile


class PlaceHolderException(Exception):
    """Exception class for PlaceHolder."""
    pass


class PlaceHolder(object):
    """Base class for placeholders."""

    def instantiate_for_glslc_args(self, testcase):
        """Instantiation rules for glslc_args.

        This method will be called when the current placeholder appears in
        glslc_args.

        Returns:
            A string to replace the current placeholder in glslc_args.
        """
        raise PlaceHolderException('Subclass should implement this function.')

    def instantiate_for_expectation(self, testcase):
        """Instantiation rules for expected_*.

        This method will be called when the current placeholder appears in
        expected_*.

        Returns:
            A string to replace the current placeholder in expected_*.
        """
        raise PlaceHolderException('Subclass should implement this function.')


class FileShader(PlaceHolder):
    """Stands for a shader whose source code is in a file."""

    def __init__(self, source, suffix):
        assert isinstance(source, str)
        assert isinstance(suffix, str)
        self.source = source
        self.suffix = suffix
        self.filename = None

    def instantiate_for_glslc_args(self, testcase):
        """Creates a temporary file and writes the source into it.

        Returns:
            The name of the temporary file.
        """
        shader, self.filename = tempfile.mkstemp(
            dir=testcase.directory, suffix=self.suffix)
        shader_object = os.fdopen(shader, 'w')
        shader_object.write(self.source)
        shader_object.close()
        return self.filename

    def instantiate_for_expectation(self, testcase):
        assert self.filename is not None
        return self.filename


class StdinShader(PlaceHolder):
    """Stands for a shader whose source code is from stdin."""

    def __init__(self, source):
        assert isinstance(source, str)
        self.source = source
        self.filename = None

    def instantiate_for_glslc_args(self, testcase):
        """Writes the source code back to the TestCase instance."""
        testcase.stdin_shader = self.source
        self.filename = '-'
        return self.filename

    def instantiate_for_expectation(self, testcase):
        assert self.filename is not None
        return self.filename


class TempFileName(PlaceHolder):
    """Stands for a temporary file's name."""

    def __init__(self, filename):
        assert isinstance(filename, str)
        assert filename != ''
        self.filename = filename

    def instantiate_for_glslc_args(self, testcase):
        return os.path.join(testcase.directory, self.filename)

    def instantiate_for_expectation(self, testcase):
        return os.path.join(testcase.directory, self.filename)
