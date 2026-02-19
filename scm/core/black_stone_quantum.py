# scm/core/black_stone_quantum.py
"""
Quantum-safe extensions for Black Stone Mode.
Исправленная версия с правильными уровнями смерти.
"""

from datetime import datetime
from typing import Dict

class QuantumDeathProtocol:
    """Handles death scenarios with quantum-safe recovery"""
    
    DEATH_LEVELS = {
        'SOFT': 1,      # 5-4 shares available
        'HARD': 2,       # 3 shares available (минимальный порог)
        'CRITICAL': 3,   # 2 shares available (ниже порога)
        'IRREVERSIBLE': 4 # 0-1 shares available
    }
    
    def __init__(self, anchor_hash: str):
        self.anchor_hash = anchor_hash
        self.share_status = {i: True for i in range(1, 6)}  # 1-5, True = available
        self.death_level = 1  # SOFT по умолчанию (все shares есть)
        self._update_death_level()
    
    def report_share_loss(self, share_index: int):
        """Report that a share has been lost"""
        if 1 <= share_index <= 5:
            self.share_status[share_index] = False
            self._update_death_level()
    
    def report_share_recovered(self, share_index: int):
        """Report that a share has been recovered"""
        if 1 <= share_index <= 5:
            self.share_status[share_index] = True
            self._update_death_level()
    
    def _update_death_level(self):
        """Update death level based on available shares"""
        available = sum(1 for v in self.share_status.values() if v)
        
        if available >= 4:
            self.death_level = self.DEATH_LEVELS['SOFT']      # 4-5 shares: SOFT
        elif available == 3:
            self.death_level = self.DEATH_LEVELS['HARD']      # 3 shares: HARD
        elif available == 2:
            self.death_level = self.DEATH_LEVELS['CRITICAL']  # 2 shares: CRITICAL
        else:
            self.death_level = self.DEATH_LEVELS['IRREVERSIBLE'] # 0-1 shares: IRREVERSIBLE
        
        self._log_death_event()
    
    def _log_death_event(self):
        """Log death event"""
        available = sum(1 for v in self.share_status.values() if v)
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'anchor': self.anchor_hash,
            'death_level': self.death_level,
            'available_shares': available,
            'threshold': 3
        }
        
        with open('BLACKSTONE.md', 'a') as f:
            f.write(f"\n## Quantum Death Event: {event['timestamp']}\n")
            f.write(f"- Anchor: {event['anchor']}\n")
            f.write(f"- Level: {event['death_level']}\n")
            f.write(f"- Available shares: {event['available_shares']}/5\n")
            f.write(f"- Threshold: {event['threshold']}\n")
    
    def can_recover(self) -> bool:
        """Check if entity can still be recovered"""
        available = sum(1 for v in self.share_status.values() if v)
        return available >= 3  # Можно восстановить если есть минимум 3 shares
    
    def get_status(self) -> Dict:
        """Get current status"""
        available = sum(1 for v in self.share_status.values() if v)
        return {
            'anchor': self.anchor_hash,
            'death_level': self.death_level,
            'available_shares': available,
            'threshold': 3,
            'can_recover': available >= 3,
            'shares': self.share_status.copy()
        }
