# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
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
# ==============================================================================

"""A LazyLoader class."""

import importlib
import types
from tensorflow.python.platform import tf_logging as logging


class LazyLoader(types.ModuleType):
  """Lazily import a module, mainly to avoid pulling in large dependencies.

  `contrib`, and `ffmpeg` are examples of modules that are large and not always
  needed, and this allows them to only be loaded when they are used.
  """

  # The lint error here is incorrect.
  def __init__(self, local_name, parent_module_globals, name, warning=None):
    self._local_name = local_name
    self._parent_module_globals = parent_module_globals
    self._warning = warning

    # These members allows doctest correctly process this module member without
    # triggering self._load(). self._load() mutates parant_module_globals and
    # triggers a dict mutated during iteration error from doctest.py.
    # - for from_module()
    self.__module__ = name.rsplit(".", 1)[0]
    # - for is_routine()
    self.__wrapped__ = None

    super(LazyLoader, self).__init__(name)

  def _load(self):
    """Load the module and insert it into the parent's globals."""
    # Import the target module and insert it into the parent's namespace
    module = importlib.import_module(self.__name__)
    self._parent_module_globals[self._local_name] = module

    # Emit a warning if one was specified
    if self._warning:
      logging.warning(self._warning)
      # Make sure to only warn once.
      self._warning = None

    # Update this object's dict so that if someone keeps a reference to the
    #   LazyLoader, lookups are efficient (__getattr__ is only called on lookups
    #   that fail).
    self.__dict__.update(module.__dict__)

    return module

  def __getattr__(self, item):
    module = self._load()
    return getattr(module, item)

  def __repr__(self):
    # Carefully to not trigger _load, since repr may be called in very
    # sensitive places.
    return f"<LazyLoader {self.__name__} as {self._local_name}>"

  def __dir__(self):
    module = self._load()
    return dir(module)
