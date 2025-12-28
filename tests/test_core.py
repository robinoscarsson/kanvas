"""Tests for core loop functions."""

import pytest

from kanvas import core


class TestLoopControl:
    """Tests for loop control functions (noLoop, loop, isLooping)."""

    def setup_method(self) -> None:
        """Reset loop state before each test."""
        # Ensure we start with looping enabled
        core._loop_enabled = True

    def teardown_method(self) -> None:
        """Reset loop state after each test."""
        # Reset to default state
        core._loop_enabled = True

    def test_noLoop_sets_flag(self) -> None:
        """Verify noLoop() sets _loop_enabled to False."""
        assert core._loop_enabled is True
        
        core.noLoop()
        
        assert core._loop_enabled is False

    def test_loop_sets_flag(self) -> None:
        """Verify loop() sets _loop_enabled to True."""
        core._loop_enabled = False
        
        core.loop()
        
        assert core._loop_enabled is True

    def test_isLooping_returns_state(self) -> None:
        """Verify isLooping() returns correct state."""
        core._loop_enabled = True
        assert core.isLooping() is True
        
        core._loop_enabled = False
        assert core.isLooping() is False

    def test_noLoop_then_loop(self) -> None:
        """Verify noLoop() followed by loop() restores looping."""
        assert core.isLooping() is True
        
        core.noLoop()
        assert core.isLooping() is False
        
        core.loop()
        assert core.isLooping() is True

    def test_multiple_noLoop_calls(self) -> None:
        """Verify multiple noLoop() calls don't cause issues."""
        core.noLoop()
        core.noLoop()
        core.noLoop()
        
        assert core.isLooping() is False

    def test_multiple_loop_calls(self) -> None:
        """Verify multiple loop() calls don't cause issues."""
        core.noLoop()
        
        core.loop()
        core.loop()
        core.loop()
        
        assert core.isLooping() is True


class TestFrameTimer:
    """Tests for the _FrameTimer helper class."""

    def test_frame_timer_initialization(self) -> None:
        """Verify FrameTimer initializes with correct frame time."""
        timer = core._FrameTimer(60)
        
        assert timer.frame_time == pytest.approx(1.0 / 60, rel=1e-6)

    def test_frame_timer_initialization_30fps(self) -> None:
        """Verify FrameTimer initializes correctly for 30 FPS."""
        timer = core._FrameTimer(30)
        
        assert timer.frame_time == pytest.approx(1.0 / 30, rel=1e-6)

    def test_frame_timer_update_returns_delta(self) -> None:
        """Verify update() returns delta time in milliseconds."""
        timer = core._FrameTimer(60)
        
        # First update should return some positive delta
        delta_ms = timer.update()
        
        # Delta should be a positive number (time since initialization)
        assert delta_ms >= 0

    def test_frame_timer_update_updates_last_time(self) -> None:
        """Verify update() updates the last_time attribute."""
        timer = core._FrameTimer(60)
        initial_time = timer.last_time
        
        # Small delay to ensure time passes
        import time
        time.sleep(0.001)
        
        timer.update()
        
        assert timer.last_time > initial_time