# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# python3
"""Helps define a foreign key relationship between two models"""

import importlib

from spanner_orm.condition import columns_equal
from spanner_orm.model import Model


class ModelRelationship(object):
  """Helps define a foreign key relationship between two models"""

  def __init__(self, origin, destination_name, constraints, is_parent=False):
    """Creates a ModelRelationship

    Args:
      origin: Model that the relationship originates from
      destination_name: Fully qualified class name of the destination model
      constraints: Maps origin columns to destination columns
      is_parent: True if the destination is a parent table of the origin
    """
    self._origin = origin
    self._destination = self._load_model(destination_name)
    self._conditions = self._parse_constraints(constraints)
    self._is_parent = is_parent

  def conditions(self):
    return self._conditions

  def destination(self):
    return self._destination

  def origin(self):
    return self._origin

  def _parse_constraints(self, constraints):
    """Validates the dictionary of constraints and turns it into Conditions"""
    conditions = []
    for origin_column, destination_column in constraints.items():
      assert origin_column in self._origin.schema()
      assert destination_column in self._destination.schema()
      # This is backward from what you might imagine because the condition will
      # be processed from the context of the destination model
      conditions.append(
          columns_equal(destination_column, self._origin, origin_column))

    return conditions

  def _load_model(self, model_name):
    parts = model_name.split('.')
    path = '.'.join(parts[:-1])
    module = importlib.import_module(path)
    model = getattr(module, parts[-1])
    assert issubclass(model, Model)
    return model