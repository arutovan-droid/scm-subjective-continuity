"""
Tests for Black Stone mode.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock

from core.black_stone import BlackStoneMode


@pytest_asyncio.fixture
async def reset_black_stone():
    """Reset BlackStone state before each test."""
    # Save original callbacks
    old_chain = BlackStoneMode._chain_callback
    old_ite = BlackStoneMode._ite_halt_callback
    old_ecl = BlackStoneMode._ecl_silence_callback
    old_test_mode = BlackStoneMode._test_mode
    
    # Reset
    BlackStoneMode._chain_callback = None
    BlackStoneMode._ite_halt_callback = None
    BlackStoneMode._ecl_silence_callback = None
    BlackStoneMode._state.active = False
    
    # Enable test mode to avoid infinite waits
    BlackStoneMode.set_test_mode(True)
    
    yield
    
    # Restore
    BlackStoneMode._chain_callback = old_chain
    BlackStoneMode._ite_halt_callback = old_ite
    BlackStoneMode._ecl_silence_callback = old_ecl
    BlackStoneMode.set_test_mode(old_test_mode)


@pytest.mark.asyncio
async def test_black_stone_activation(reset_black_stone):
    """Test Black Stone mode activation."""
    
    # Create mock callbacks
    chain_callback = AsyncMock()
    ite_callback = AsyncMock()
    ecl_callback = AsyncMock()
    
    # Register
    BlackStoneMode.register_chain(chain_callback)
    BlackStoneMode.register_ite(ite_callback)
    BlackStoneMode.register_ecl(ecl_callback)
    
    # Activate
    await BlackStoneMode.enter("test_reason", "scar-123")
    
    # Check state
    assert BlackStoneMode.is_active() == True
    state = BlackStoneMode.get_state()
    assert state.reason == "test_reason"
    assert state.scar_id == "scar-123"
    
    # Check callbacks
    chain_callback.assert_awaited_once_with("BLACKSTONE:test_reason:scar-123")
    ite_callback.assert_awaited_once()
    ecl_callback.assert_awaited_once()


@pytest.mark.asyncio
async def test_black_stone_exit(reset_black_stone):
    """Test exit from Black Stone mode via rebirth."""
    
    await BlackStoneMode.enter("test", "scar-123")
    assert BlackStoneMode.is_active() == True
    
    # Exit with signature
    await BlackStoneMode.exit_via_rebirth(b"fake_signature")
    
    assert BlackStoneMode.is_active() == False
    assert BlackStoneMode.get_state().active == False


@pytest.mark.asyncio
async def test_black_stone_no_double_activation(reset_black_stone):
    """Test that double activation doesn't create second mode."""
    
    ite_callback = AsyncMock()
    BlackStoneMode.register_ite(ite_callback)
    
    # First activation
    await BlackStoneMode.enter("reason1", "scar1")
    assert BlackStoneMode.is_active() == True
    assert ite_callback.await_count == 1
    
    # Second activation (should be ignored)
    await BlackStoneMode.enter("reason2", "scar2")
    assert ite_callback.await_count == 1
    assert BlackStoneMode.get_state().reason == "reason1"
