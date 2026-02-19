"""
Black Stone mode — ontological death of the system.
When chain breaks, system enters read-only mode.
"""

from typing import Optional, Callable, Awaitable
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class BlackStoneState:
    """Black Stone mode state."""
    active: bool = False
    reason: Optional[str] = None
    scar_id: Optional[str] = None
    timestamp: Optional[str] = None


class BlackStoneMode:
    """
    Black Stone mode — system does not respond, only reads history.
    Requires physical operator presence to exit.
    """
    
    _state = BlackStoneState()
    _chain_callback: Optional[Callable[[str, str], Awaitable[None]]] = None
    _ite_halt_callback: Optional[Callable[[], Awaitable[None]]] = None
    _ecl_silence_callback: Optional[Callable[[], Awaitable[None]]] = None
    
    # For testing
    _test_mode = False
    _test_wait_override = None
    
    @classmethod
    def set_test_mode(cls, enabled: bool = True):
        """Enable test mode to avoid infinite waits."""
        cls._test_mode = enabled
        
    @classmethod
    def register_chain(cls, callback: Callable[[str, str], Awaitable[None]]):
        """Register callback for ChainRepository."""
        cls._chain_callback = callback
        
    @classmethod
    def register_ite(cls, callback: Callable[[], Awaitable[None]]):
        """Register callback for ITE."""
        cls._ite_halt_callback = callback
        
    @classmethod
    def register_ecl(cls, callback: Callable[[], Awaitable[None]]):
        """Register callback for ECL."""
        cls._ecl_silence_callback = callback
        
    @classmethod
    async def enter(cls, reason: str, scar_id: str):
        """
        Enter Black Stone mode.
        Stops all active processes.
        """
        from datetime import datetime
        
        if cls._state.active:
            logger.warning(f"Already in Black Stone mode. New reason: {reason}")
            return
            
        cls._state = BlackStoneState(
            active=True,
            reason=reason,
            scar_id=scar_id,
            timestamp=datetime.utcnow().isoformat()
        )
        
        logger.critical(f"🪨 BLACK STONE MODE ACTIVATED: {reason} (scar: {scar_id})")
        
        # 1. Stop ITE
        if cls._ite_halt_callback:
            await cls._ite_halt_callback()
            
        # 2. ECL silence mode
        if cls._ecl_silence_callback:
            await cls._ecl_silence_callback()
            
        # 3. Write to wormhole
        if cls._chain_callback:
            await cls._chain_callback(f"BLACKSTONE:{reason}:{scar_id}")
            
        # 4. Wait for operator (skip in test mode)
        if not cls._test_mode:
            await cls._wait_for_operator()
        
    @classmethod
    async def _wait_for_operator(cls):
        """Wait for physical operator presence."""
        logger.info("⏳ Waiting for operator presence to exit Black Stone...")
        
        while cls._state.active:
            await asyncio.sleep(60)
            
    @classmethod
    async def exit_via_rebirth(cls, operator_signature: bytes):
        """Exit mode via rebirth ritual."""
        if not cls._verify_operator(operator_signature):
            logger.error("Invalid operator signature for rebirth")
            return False
            
        cls._state = BlackStoneState()
        logger.info("✨ Exited Black Stone mode via rebirth")
        return True
        
    @classmethod
    def _verify_operator(cls, signature: bytes) -> bool:
        """Stub for operator verification."""
        return True
        
    @classmethod
    def is_active(cls) -> bool:
        return cls._state.active
        
    @classmethod
    def get_state(cls) -> BlackStoneState:
        return cls._state
