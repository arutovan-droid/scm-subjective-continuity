# tests/test_hybrid_crypto.py
"""
Unit tests for quantum-safe hybrid cryptography.
"""

import pytest
from scm.crypto.hybrid import (
    generate_hybrid_keypair,
    hybrid_sign,
    hybrid_verify,
    create_hybrid_proof,
    TEST_MESSAGE
)

class TestHybridCrypto:
    """Test suite for hybrid Ed25519 + Dilithium5"""
    
    def test_keypair_generation(self):
        """Test that both keypairs are generated correctly"""
        kp = generate_hybrid_keypair()
        
        assert len(kp.ed25519_private) == 32
        assert len(kp.ed25519_public) == 32
        assert len(kp.dilithium5_private) > 2000
        assert len(kp.dilithium5_public) > 1000
        assert len(kp._compute_anchor_hash()) == 16
        
    def test_hybrid_sign_verify(self):
        """Test signing and verification with both algorithms"""
        kp = generate_hybrid_keypair()
        message = b"Test message for SCM quantum genesis"
        
        ed_sig, dil_sig = hybrid_sign(message, kp)
        
        public_kp = type(kp)(
            ed25519_private=None,
            ed25519_public=kp.ed25519_public,
            dilithium5_private=None,
            dilithium5_public=kp.dilithium5_public
        )
        
        assert hybrid_verify(message, ed_sig, dil_sig, public_kp) is True
        
    def test_hybrid_verify_fails_on_tampered_message(self):
        """Test that verification fails if message is altered"""
        kp = generate_hybrid_keypair()
        message = b"Original message"
        tampered = b"Tampered message"
        
        ed_sig, dil_sig = hybrid_sign(message, kp)
        
        public_kp = type(kp)(
            ed25519_private=None,
            ed25519_public=kp.ed25519_public,
            dilithium5_private=None,
            dilithium5_public=kp.dilithium5_public
        )
        
        assert hybrid_verify(tampered, ed_sig, dil_sig, public_kp) is False
        
    def test_create_hybrid_proof(self):
        """Test creation of complete hybrid proof"""
        kp = generate_hybrid_keypair()
        proof = create_hybrid_proof(TEST_MESSAGE, kp)
        
        assert 'message' in proof
        assert 'ed25519_signature' in proof
        assert 'dilithium5_signature' in proof
        assert 'ed25519_public' in proof
        assert 'dilithium5_public' in proof
        assert 'anchor_hash' in proof
