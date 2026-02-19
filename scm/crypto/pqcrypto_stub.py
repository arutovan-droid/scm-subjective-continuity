# scm/crypto/pqcrypto_stub.py
"""
Заглушка для pqcrypto-dilithium с правильными размерами ключей
Dilithium5: public_key=1312 bytes, private_key=2528 bytes
"""

import hashlib
import os

class Dilithium5Stub:
    """Заглушка с реальными размерами ключей Dilithium5"""
    
    # Реальные размеры для Dilithium5
    PUBLIC_KEY_SIZE = 1312
    PRIVATE_KEY_SIZE = 2528
    SIGNATURE_SIZE = 2420  # для Dilithium5
    
    @staticmethod
    def keypair():
        """Генерирует ключи правильного размера"""
        seed = os.urandom(32)
        
        # Генерируем публичный ключ (1312 байт)
        public_key = b''
        while len(public_key) < Dilithium5Stub.PUBLIC_KEY_SIZE:
            seed = hashlib.sha256(seed).digest()
            public_key += hashlib.sha512(seed).digest()
        public_key = public_key[:Dilithium5Stub.PUBLIC_KEY_SIZE]
        
        # Генерируем приватный ключ (2528 байт)
        private_key = b''
        while len(private_key) < Dilithium5Stub.PRIVATE_KEY_SIZE:
            seed = hashlib.sha256(seed).digest()
            private_key += hashlib.sha512(seed).digest()
        private_key = private_key[:Dilithium5Stub.PRIVATE_KEY_SIZE]
        
        return public_key, private_key
    
    @staticmethod
    def sign(private_key, message):
        """Создает подпись правильного размера"""
        # Комбинируем ключ и сообщение
        data = private_key[:32] + message
        signature = b''
        
        # Генерируем подпись размером 2420 байт
        while len(signature) < Dilithium5Stub.SIGNATURE_SIZE:
            data = hashlib.sha512(data).digest()
            signature += data
        signature = signature[:Dilithium5Stub.SIGNATURE_SIZE]
        
        return signature
    
    @staticmethod
    def verify(public_key, message, signature):
        """Проверяет подпись (упрощенно)"""
        # Для тестов просто проверяем длину
        if len(signature) != Dilithium5Stub.SIGNATURE_SIZE:
            return False
        
        # Пересоздаем ожидаемую подпись (упрощенно)
        expected = Dilithium5Stub.sign(public_key[:32], message)
        
        # Сравниваем первые 32 байта для скорости
        return signature[:32] == expected[:32]

# Создаем экземпляр для импорта
dilithium5 = Dilithium5Stub()
