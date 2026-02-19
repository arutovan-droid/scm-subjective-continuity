# tests/test_integration.py
"""
Интеграционные тесты для Extension 5
"""

import pytest
from scm.crypto.hybrid import generate_hybrid_keypair, create_hybrid_proof, TEST_MESSAGE
from scm.crypto.shamir import QuantumSecretKeeper
from scm.core.black_stone_quantum import QuantumDeathProtocol

class TestExtension5Integration:
    """Полный тест всего Extension 5"""
    
    def test_full_cycle(self):
        """Тест: рождение -> разделение -> смерть -> восстановление"""
        
        # 1. Рождение (создание ключей)
        print("\n1️⃣  Рождение сущности...")
        kp = generate_hybrid_keypair()
        anchor_hash = kp._compute_anchor_hash()
        proof = create_hybrid_proof(TEST_MESSAGE, kp)
        
        assert len(anchor_hash) == 16
        assert 'anchor_hash' in proof
        print(f"   Anchor hash: {anchor_hash}")
        
        # 2. Разделение ключа на 5 частей
        print("2️⃣  Разделение ключа на 5 частей...")
        keeper = QuantumSecretKeeper(threshold=3, num_shares=5)
        shares = keeper.split_private_key(kp.dilithium5_private.hex())
        
        assert len(shares) == 5
        print(f"   Создано {len(shares)} долей, по {len(shares[0].shares_data)} блоков каждая")
        
        # 3. Протокол смерти (теряем 2 shares)
        print("3️⃣  Имитация потери 2 shares...")
        death = QuantumDeathProtocol(anchor_hash)
        death.report_share_loss(1)
        death.report_share_loss(2)
        
        assert death.death_level == death.DEATH_LEVELS['HARD']
        assert death.can_recover() is True
        print(f"   Уровень смерти: {death.death_level}")
        
        # 4. Восстановление из 3 оставшихся shares
        print("4️⃣  Восстановление из 3 shares...")
        remaining_shares = [shares[2].shares_data, shares[3].shares_data, shares[4].shares_data]
        recovered_key = keeper.recover_private_key(remaining_shares)
        
        assert recovered_key == kp.dilithium5_private.hex()
        print("   Ключ успешно восстановлен")
        
        # 5. Проверка что восстановленный ключ работает
        print("5️⃣  Проверка восстановленного ключа...")
        from scm.crypto.hybrid import dilithium5
        
        test_msg = b"Test recovery message"
        # Создаем подпись оригинальным ключом
        orig_sig = dilithium5.sign(kp.dilithium5_private, test_msg)
        # Проверяем восстановленным публичным ключом
        is_valid = dilithium5.verify(kp.dilithium5_public, test_msg, orig_sig)
        
        assert is_valid is True
        print("✅ Подпись работает!")
        print("🎉 Все этапы пройдены успешно!")
