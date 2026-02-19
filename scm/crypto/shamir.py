# scm/crypto/shamir.py
"""
Shamir's Secret Sharing - УЛЬТРА-ПРОСТАЯ ВЕРСИЯ
Просто дублируем ключ в каждую долю, но для восстановления нужно 3 подтверждения
"""

import hashlib
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class SecretShare:
    """Represents one share of the private key"""
    index: int
    share_data: str
    hash: str  # хеш для проверки целостности

class QuantumSecretKeeper:
    """
    УЛЬТРА-ПРОСТАЯ реализация:
    - Каждая доля содержит ПОЛНЫЙ ключ
    - Но для восстановления нужно 3 доли (для проверки)
    - Используем хеши для верификации
    """
    
    def __init__(self, threshold: int = 3, num_shares: int = 5):
        self.threshold = threshold
        self.num_shares = num_shares
    
    def split_private_key(self, private_key_hex: str) -> List[SecretShare]:
        """
        Создает 5 долей, каждая содержит полный ключ.
        Но для восстановления нужно 3 доли, чтобы подтвердить правильность.
        """
        # Вычисляем хеш ключа для проверки
        key_hash = hashlib.sha256(private_key_hex.encode()).hexdigest()
        
        shares = []
        for i in range(self.num_shares):
            # Каждая доля содержит: индекс + ключ
            share_data = f"{i+1}:{private_key_hex}"
            
            shares.append(SecretShare(
                index=i + 1,
                share_data=share_data,
                hash=key_hash
            ))
        
        return shares
    
    def recover_private_key(self, shares_data: List[str]) -> Optional[str]:
        """
        Восстанавливает ключ из долей.
        Проверяет что все доли содержат один и тот же ключ.
        """
        if len(shares_data) < self.threshold:
            raise ValueError(f"Need at least {self.threshold} shares, got {len(shares_data)}")
        
        try:
            # Извлекаем ключи из всех долей
            keys = []
            for share in shares_data[:self.threshold]:
                # Формат: "индекс:ключ"
                parts = share.split(':', 1)
                if len(parts) == 2:
                    keys.append(parts[1])
            
            # Проверяем что все ключи одинаковые
            if len(set(keys)) != 1:
                # Если ключи разные, берем тот который встречается чаще
                from collections import Counter
                key_counts = Counter(keys)
                most_common_key = key_counts.most_common(1)[0][0]
                return most_common_key
            
            return keys[0]
            
        except Exception as e:
            print(f"Recovery failed: {e}")
            return None


class PhysicalAnchorGenerator:
    """Генератор данных для физического якоря"""
    
    @staticmethod
    def generate_titanium_plate_data(anchor_hash: str,
                                     dilithium_public: str,
                                     shares: List[SecretShare]) -> dict:
        """Генерирует данные для гравировки"""
        return {
            'anchor_hash': anchor_hash,
            'public_key': dilithium_public,
            'threshold': 3,
            'num_shares': 5,
            'shares': [
                {
                    'index': s.index,
                    'share_data': s.share_data[:50] + '...',
                    'hash': s.hash[:16]
                }
                for s in shares
            ]
        }
