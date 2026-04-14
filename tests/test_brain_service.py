"""
Comprehensive test suite for SkinWalkerBrain service
Tests persona management, learning, and text processing
"""

import pytest
from unittest.mock import patch, MagicMock
from backend.services.brain import SkinWalkerBrain, brain


class TestSkinWalkerBrainInitialization:
    """Test SkinWalkerBrain initialization"""

    def test_brain_initialization(self):
        """Test that brain initializes with default TIA persona"""
        test_brain = SkinWalkerBrain()
        assert test_brain.persona is not None
        assert test_brain.persona.name == "TIA"
        assert test_brain.vortex is not None

    def test_brain_singleton(self):
        """Test that brain module exports a singleton instance"""
        assert brain is not None
        assert isinstance(brain, SkinWalkerBrain)


class TestSkinWalkerBrainPersonaDetection:
    """Test persona detection and switching"""

    @pytest.mark.asyncio
    async def test_persona_switches_on_detection(self):
        """Test that persona changes when detected in text"""
        test_brain = SkinWalkerBrain()

        with patch('backend.services.brain.detect_persona') as mock_detect:
            # Mock a different persona being detected
            mock_persona = MagicMock()
            mock_persona.name = "ADMIRAL"
            mock_detect.return_value = mock_persona

            result = await test_brain.process("admiral mode activate")

            # Verify persona was switched
            assert test_brain.persona.name == "ADMIRAL"
            mock_detect.assert_called_once()

    @pytest.mark.asyncio
    async def test_persona_remains_when_not_detected(self):
        """Test that persona stays same when no new persona detected"""
        test_brain = SkinWalkerBrain()
        original_persona = test_brain.persona.name

        with patch('backend.services.brain.detect_persona') as mock_detect:
            mock_detect.return_value = None

            result = await test_brain.process("regular text")

            # Verify persona didn't change
            assert test_brain.persona.name == original_persona


class TestSkinWalkerBrainLearning:
    """Test knowledge learning functionality"""

    @pytest.mark.asyncio
    async def test_learn_command_saves_fact(self):
        """Test that 'learn' keyword triggers knowledge saving"""
        test_brain = SkinWalkerBrain()

        with patch('backend.services.brain.knowledge_base.save_fact') as mock_save, \
             patch('backend.services.brain.detect_persona') as mock_detect:
            mock_detect.return_value = None

            result = await test_brain.process("learn that Bitcoin is digital gold")

            # Verify save_fact was called
            mock_save.assert_called_once_with("learn that Bitcoin is digital gold")
            assert "Learned" in result["msg"]
            assert result["persona"] == test_brain.persona.name

    @pytest.mark.asyncio
    async def test_learn_case_insensitive(self):
        """Test that learning works with different cases"""
        test_brain = SkinWalkerBrain()

        with patch('backend.services.brain.knowledge_base.save_fact') as mock_save, \
             patch('backend.services.brain.detect_persona') as mock_detect:
            mock_detect.return_value = None

            # Test uppercase LEARN
            result = await test_brain.process("LEARN this important fact")
            assert mock_save.called

            # Test mixed case Learn
            result = await test_brain.process("Learn another fact")
            assert mock_save.call_count == 2


class TestSkinWalkerBrainProcessing:
    """Test text processing functionality"""

    @pytest.mark.asyncio
    async def test_process_regular_text(self):
        """Test processing text without special commands"""
        test_brain = SkinWalkerBrain()

        with patch('backend.services.brain.detect_persona') as mock_detect:
            mock_detect.return_value = None

            result = await test_brain.process("Hello, how are you?")

            # Verify response contains text and persona
            assert "msg" in result
            assert "Hello, how are you?" in result["msg"]
            assert result["persona"] == test_brain.persona.name

    @pytest.mark.asyncio
    async def test_process_returns_persona_name(self):
        """Test that process always returns current persona name"""
        test_brain = SkinWalkerBrain()

        with patch('backend.services.brain.detect_persona') as mock_detect:
            mock_detect.return_value = None

            result = await test_brain.process("test message")

            assert "persona" in result
            assert isinstance(result["persona"], str)
            assert result["persona"] == test_brain.persona.name

    @pytest.mark.asyncio
    async def test_process_includes_persona_in_message(self):
        """Test that processed message includes persona prefix"""
        test_brain = SkinWalkerBrain()

        with patch('backend.services.brain.detect_persona') as mock_detect:
            mock_detect.return_value = None

            result = await test_brain.process("status check")

            # Verify persona name is in message
            assert f"[{test_brain.persona.name}]" in result["msg"]


class TestSkinWalkerBrainIntegration:
    """Integration tests for SkinWalkerBrain"""

    @pytest.mark.asyncio
    async def test_persona_switch_and_learn_integration(self):
        """Test persona switching followed by learning"""
        test_brain = SkinWalkerBrain()

        with patch('backend.services.brain.detect_persona') as mock_detect, \
             patch('backend.services.brain.knowledge_base.save_fact') as mock_save:
            # First, switch persona
            new_persona = MagicMock()
            new_persona.name = "VORTEX"
            mock_detect.return_value = new_persona

            result1 = await test_brain.process("activate vortex")
            assert test_brain.persona.name == "VORTEX"

            # Then, learn something with new persona
            mock_detect.return_value = None
            result2 = await test_brain.process("learn new strategy")

            assert mock_save.called
            assert result2["persona"] == "VORTEX"
