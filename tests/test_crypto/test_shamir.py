# tests/test_crypto/test_shamir.py
"""
Тесты для ультра-простой версии Shamir
"""

import pytest
from scm.crypto.shamir import QuantumSecretKeeper
from scm.crypto.hybrid import generate_hybrid_keypair

class TestShamir:
    """Тестируем разделение и восстановление ключей"""
    
    def test_split_and_recover(self):
        """Тест: разделили ключ на 5 частей, восстановили из 3"""
        kp = generate_hybrid_keypair()
        private_key = kp.dilithium5_private.hex()
        
        keeper = QuantumSecretKeeper(threshold=3, num_shares=5)
        shares = keeper.split_private_key(private_key)
        
        assert len(shares) == 5
        
        # Берем первые 3 shares для восстановления
        share_data = [s.share_data for s in shares[:3]]
        recovered = keeper.recover_private_key(share_data)
        
        assert recovered == private_key, "Ключ не восстановился правильно"
    
    def test_threshold_requirement(self):
        """Тест: 2 shares недостаточно для восстановления"""
        kp = generate_hybrid_keypair()
        private_key = kp.dilithium5_private.hex()
        
        keeper = QuantumSecretKeeper(threshold=3, num_shares=5)
        shares = keeper.split_private_key(private_key)
        
        # Пытаемся восстановить из 2 shares
        share_data = [s.share_data for s in shares[:2]]
        
        with pytest.raises(ValueError, match="Need at least 3 shares"):
            keeper.recover_private_key(share_data)
    
    def test_different_shares_dont_work(self):
        """Тест: разные доли не работают вместе"""
        kp1 = generate_hybrid_keypair()
        kp2 = generate_hybrid_keypair()
        
        keeper = QuantumSecretKeeper()
        
        shares1 = keeper.split_private_key(kp1.dilithium5_private.hex())
        shares2 = keeper.split_private_key(kp2.dilithium5_private.hex())
        
        # Смешиваем доли от разных ключей
        mixed = [shares1[0].share_data, shares1[1].share_data, shares2[2].share_data]
        
        recovered = keeper.recover_private_key(mixed)
        
        # Должен вернуть ключ который встречается чаще (kp1)
        assert recovered == kp1.dilithium5_private.hex()
    
    def test_all_combinations_recover(self):
        """Тест: любые 3 из 5 долей должны восстановить ключ"""
        kp = generate_hybrid_keypair()
        private_key = kp.dilithium5_private.hex()
        
        keeper = QuantumSecretKeeper(threshold=3, num_shares=5)
        shares = keeper.split_private_key(private_key)
        
        from itertools import combinations
        
        for combo in combinations(range(5), 3):
            share_data = [shares[i].share_data for i in combo]
            recovered = keeper.recover_private_key(share_data)
            assert recovered == private_key, f"Комбинация {combo} не сработала"
    
    def test_different_order_recover(self):
        """Тест: порядок долей не важен"""
        kp = generate_hybrid_keypair()
        private_key = kp.dilithium5_private.hex()
        
        keeper = QuantumSecretKeeper(threshold=3, num_shares=5)
        shares = keeper.split_private_key(private_key)
        
        # Берем доли в разном порядке
        share_data1 = [shares[0].share_data, shares[1].share_data, shares[2].share_data]
        share_data2 = [shares[2].share_data, shares[0].share_data, shares[1].share_data]
        
        recovered1 = keeper.recover_private_key(share_data1)
        recovered2 = keeper.recover_private_key(share_data2)
        
        assert recovered1 == private_key
        assert recovered2 == private_key
