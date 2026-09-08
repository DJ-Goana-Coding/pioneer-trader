#!/usr/bin/env python3
"""Unit tests for backend/core/personas.py Persona model and detect_persona."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, Mock, MagicMock

from backend.core.personas import Persona, PERSONA_REGISTRY, detect_persona


class TestPersonaRegistry(unittest.TestCase):
    """Test PERSONA_REGISTRY contents."""

    def test_registry_has_four_entries(self):
        self.assertEqual(len(PERSONA_REGISTRY), 4)

    def test_tia_fields(self):
        tia = PERSONA_REGISTRY["TIA"]
        self.assertEqual(tia.id, "TIA")
        self.assertEqual(tia.name, "T.I.A.")
        self.assertEqual(tia.role, "Captain")
        self.assertEqual(tia.style, "green")
        self.assertIn("status", tia.triggers)

    def test_goanna_fields(self):
        goanna = PERSONA_REGISTRY["GOANNA"]
        self.assertEqual(goanna.id, "GOANNA")
        self.assertEqual(goanna.name, "DJ Goanna")
        self.assertEqual(goanna.role, "DJ")
        self.assertEqual(goanna.style, "purple")
        self.assertIn("bass", goanna.triggers)

    def test_void_fields(self):
        void = PERSONA_REGISTRY["VOID"]
        self.assertEqual(void.id, "VOID")
        self.assertEqual(void.name, "The Void")
        self.assertEqual(void.role, "Oracle")
        self.assertEqual(void.style, "red")
        self.assertIn("truth", void.triggers)

    def test_hippy_fields(self):
        hippy = PERSONA_REGISTRY["HIPPY"]
        self.assertEqual(hippy.id, "HIPPY")
        self.assertEqual(hippy.name, "Hippy")
        self.assertEqual(hippy.role, "Guide")
        self.assertEqual(hippy.style, "blue")
        self.assertIn("peace", hippy.triggers)


class TestDetectPersona(unittest.TestCase):
    """Test detect_persona function."""

    def test_detect_tia(self):
        result = detect_persona("system status")
        self.assertIsNotNone(result)
        self.assertEqual(result.id, "TIA")

    def test_detect_goanna(self):
        result = detect_persona("play bass")
        self.assertIsNotNone(result)
        self.assertEqual(result.id, "GOANNA")

    def test_detect_void(self):
        result = detect_persona("dark prediction")
        self.assertIsNotNone(result)
        self.assertEqual(result.id, "VOID")

    def test_detect_hippy(self):
        result = detect_persona("peace and love")
        self.assertIsNotNone(result)
        self.assertEqual(result.id, "HIPPY")

    def test_detect_none_unrecognized(self):
        result = detect_persona("xyzzy foobar blah")
        self.assertIsNone(result)

    def test_case_insensitive(self):
        result = detect_persona("SYSTEM STATUS")
        self.assertIsNotNone(result)
        self.assertEqual(result.id, "TIA")


class TestPersonaModel(unittest.TestCase):
    """Test Persona pydantic model validation."""

    def test_valid_persona(self):
        p = Persona(id="X", name="Test", role="Tester", style="white", triggers=["test"])
        self.assertEqual(p.id, "X")
        self.assertEqual(p.triggers, ["test"])

    def test_missing_field_raises(self):
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            Persona(id="X", name="Test")


if __name__ == "__main__":
    unittest.main()
