"""Tests for the controller module with mocked view."""

from unittest.mock import patch, MagicMock

import pytest
import pygame


class TestHandleInput:
    """Tests for the handle_input function."""

    @patch('kanvas.controller.view')
    def test_handle_input_no_events(self, mock_view: MagicMock) -> None:
        """Verify empty events return no actions."""
        from kanvas.controller import handle_input
        
        mock_view.poll_events.return_value = {
            "QUIT": False,
            "KEYDOWN": [],
            "KEYUP": []
        }
        
        result = handle_input()
        
        assert result["quit"] is False
        assert result["save"] is False

    @patch('kanvas.controller.view')
    def test_handle_input_quit_event(self, mock_view: MagicMock) -> None:
        """Verify QUIT event sets quit flag."""
        from kanvas.controller import handle_input
        
        mock_view.poll_events.return_value = {
            "QUIT": True,
            "KEYDOWN": [],
            "KEYUP": []
        }
        
        result = handle_input()
        
        assert result["quit"] is True
        assert result["save"] is False

    @patch('kanvas.controller.view')
    def test_handle_input_escape_key(self, mock_view: MagicMock) -> None:
        """Verify ESC key sets quit flag."""
        from kanvas.controller import handle_input
        
        mock_view.poll_events.return_value = {
            "QUIT": False,
            "KEYDOWN": [pygame.K_ESCAPE],
            "KEYUP": []
        }
        
        result = handle_input()
        
        assert result["quit"] is True
        assert result["save"] is False

    @patch('kanvas.controller.view')
    def test_handle_input_save_key(self, mock_view: MagicMock) -> None:
        """Verify S key sets save flag."""
        from kanvas.controller import handle_input
        
        mock_view.poll_events.return_value = {
            "QUIT": False,
            "KEYDOWN": [pygame.K_s],
            "KEYUP": []
        }
        
        result = handle_input()
        
        assert result["quit"] is False
        assert result["save"] is True

    @patch('kanvas.controller.view')
    def test_handle_input_multiple_keys(self, mock_view: MagicMock) -> None:
        """Verify multiple keys are handled correctly."""
        from kanvas.controller import handle_input
        
        mock_view.poll_events.return_value = {
            "QUIT": False,
            "KEYDOWN": [pygame.K_s, pygame.K_a, pygame.K_w],
            "KEYUP": []
        }
        
        result = handle_input()
        
        assert result["quit"] is False
        assert result["save"] is True

    @patch('kanvas.controller.view')
    def test_handle_input_quit_and_save(self, mock_view: MagicMock) -> None:
        """Verify both quit and save can be set simultaneously."""
        from kanvas.controller import handle_input
        
        mock_view.poll_events.return_value = {
            "QUIT": True,
            "KEYDOWN": [pygame.K_s],
            "KEYUP": []
        }
        
        result = handle_input()
        
        assert result["quit"] is True
        assert result["save"] is True

    @patch('kanvas.controller.view')
    def test_handle_input_escape_and_save(self, mock_view: MagicMock) -> None:
        """Verify escape key and save key together."""
        from kanvas.controller import handle_input
        
        mock_view.poll_events.return_value = {
            "QUIT": False,
            "KEYDOWN": [pygame.K_ESCAPE, pygame.K_s],
            "KEYUP": []
        }
        
        result = handle_input()
        
        assert result["quit"] is True
        assert result["save"] is True

    @patch('kanvas.controller.view')
    def test_handle_input_keyup_ignored(self, mock_view: MagicMock) -> None:
        """Verify KEYUP events don't trigger actions."""
        from kanvas.controller import handle_input
        
        mock_view.poll_events.return_value = {
            "QUIT": False,
            "KEYDOWN": [],
            "KEYUP": [pygame.K_ESCAPE, pygame.K_s]
        }
        
        result = handle_input()
        
        assert result["quit"] is False
        assert result["save"] is False

    @patch('kanvas.controller.view')
    def test_handle_input_other_keys_ignored(self, mock_view: MagicMock) -> None:
        """Verify other keys don't affect quit/save flags."""
        from kanvas.controller import handle_input
        
        mock_view.poll_events.return_value = {
            "QUIT": False,
            "KEYDOWN": [pygame.K_a, pygame.K_b, pygame.K_SPACE, pygame.K_RETURN],
            "KEYUP": []
        }
        
        result = handle_input()
        
        assert result["quit"] is False
        assert result["save"] is False