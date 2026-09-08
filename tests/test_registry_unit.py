#!/usr/bin/env python3
"""Unit tests for registry/registry.py models and Registry.load."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import unittest
from unittest.mock import patch, Mock, MagicMock

from registry.registry import StrategySpec, EngineSpec, OverlaySpec, Registry


class TestStrategySpec(unittest.TestCase):
    """Test StrategySpec model."""

    def test_creation_minimal(self):
        s = StrategySpec(id="s1", name="Strat1", family="fam1")
        self.assertEqual(s.id, "s1")
        self.assertEqual(s.name, "Strat1")
        self.assertEqual(s.family, "fam1")

    def test_defaults(self):
        s = StrategySpec(id="s1", name="Strat1", family="fam1")
        self.assertTrue(s.enabled)
        self.assertEqual(s.ingredients, {})
        self.assertEqual(s.regimes, [])


class TestEngineSpec(unittest.TestCase):
    """Test EngineSpec model."""

    def test_creation(self):
        e = EngineSpec(id="e1", name="Engine1")
        self.assertEqual(e.id, "e1")
        self.assertEqual(e.name, "Engine1")


class TestOverlaySpec(unittest.TestCase):
    """Test OverlaySpec model."""

    def test_creation(self):
        o = OverlaySpec(id="o1", name="Overlay1")
        self.assertEqual(o.id, "o1")
        self.assertEqual(o.name, "Overlay1")


class TestRegistry(unittest.TestCase):
    """Test Registry model and load method."""

    def test_creation_with_dict(self):
        strat = StrategySpec(id="s1", name="Strat1", family="fam1")
        eng = EngineSpec(id="e1", name="Engine1")
        ovl = OverlaySpec(id="o1", name="Overlay1")
        reg = Registry(strategies={"s1": strat}, engines=[eng], overlays=[ovl])
        self.assertIn("s1", reg.strategies)
        self.assertEqual(len(reg.engines), 1)
        self.assertEqual(len(reg.overlays), 1)

    def test_load_from_json(self):
        data = {
            "strategies": [
                {"id": "s1", "name": "Strat1", "family": "fam1"},
                {"id": "s2", "name": "Strat2", "family": "fam2"},
            ],
            "engines": [{"id": "e1", "name": "Engine1"}],
            "overlays": [{"id": "o1", "name": "Overlay1"}],
        }
        filepath = os.path.join(os.path.dirname(__file__), "_test_registry_tmp.json")
        try:
            with open(filepath, "w") as f:
                json.dump(data, f)
            reg = Registry.load(filepath)
            self.assertIn("s1", reg.strategies)
            self.assertIn("s2", reg.strategies)
            self.assertEqual(reg.strategies["s1"].name, "Strat1")
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    def test_load_converts_list_to_dict(self):
        data = {
            "strategies": [{"id": "a", "name": "A", "family": "f"}],
            "engines": [],
            "overlays": [],
        }
        filepath = os.path.join(os.path.dirname(__file__), "_test_registry_conv.json")
        try:
            with open(filepath, "w") as f:
                json.dump(data, f)
            reg = Registry.load(filepath)
            self.assertIsInstance(reg.strategies, dict)
            self.assertIn("a", reg.strategies)
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    def test_load_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            Registry.load("/nonexistent/path/to/file.json")


if __name__ == "__main__":
    unittest.main()
