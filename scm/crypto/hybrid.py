# scm/crypto/hybrid.py
"""
Hybrid Cryptography Module for SCM Extension 5.
Combines Ed25519 (classical) with CRYSTALS-Dilithium5 (post-quantum).
"""

import hashlib
import os
from typing import Tuple, Dict, Any

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

# Post-quantum crypto - используем заглушку
try:
    import pqcrypto.sign.dilithium5 as dilithium5
except ImportError:
    from scm.crypto.pqcrypto_stub import dilithium5

class HybridKeyPair:
    """Container for hybrid key pair (Ed25519 + Dilithium5)"""
    
    def __init__(self, ed25519_private: bytes, ed25519_public: bytes,
                 dilithium5_private: bytes, dilithium5_public: bytes):
        self.ed25519_private = ed25519_private
        self.ed25519_public = ed25519_public
        self.dilithium5_private = dilithium5_private
        self.dilithium5_public = dilithium5_public
        
    def to_dict(self) -> Dict[str, Any]:
        """Export public keys as dict for storage"""
        return {
            'ed25519_public': self.ed25519_public.hex(),
            'dilithium5_public': self.dilithium5_public.hex(),
            'anchor_hash': self._compute_anchor_hash()
        }
    
    def _compute_anchor_hash(self) -> str:
        """Compute genesis anchor hash from both public keys"""
        combined = self.ed25519_public + self.dilithium5_public
        return hashlib.sha256(combined).hexdigest()[:16]
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HybridKeyPair':
        """Recreate from dict (public keys only)"""
        return cls(
            ed25519_private=None,
            ed25519_public=bytes.fromhex(data['ed25519_public']),
            dilithium5_private=None,
            dilithium5_public=bytes.fromhex(data['dilithium5_public'])
        )


def generate_hybrid_keypair() -> HybridKeyPair:
    """
    Generate both Ed25519 and Dilithium5 key pairs.
    Returns HybridKeyPair with all keys.
    """
    # Ed25519
    ed25519_private = ed25519.Ed25519PrivateKey.generate()
    ed25519_public = ed25519_private.public_key()
    
    # Serialize Ed25519 keys
    ed_private_bytes = ed25519_private.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    ed_public_bytes = ed25519_public.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    
    # Dilithium5
    dilithium5_public, dilithium5_private = dilithium5.keypair()
    
    return HybridKeyPair(
        ed25519_private=ed_private_bytes,
        ed25519_public=ed_public_bytes,
        dilithium5_private=dilithium5_private,
        dilithium5_public=dilithium5_public
    )


def hybrid_sign(message: bytes, hybrid_keypair: HybridKeyPair) -> Tuple[bytes, bytes]:
    """Sign message with both algorithms"""
    # Ed25519 sign
    ed_private = ed25519.Ed25519PrivateKey.from_private_bytes(
        hybrid_keypair.ed25519_private
    )
    ed_sig = ed_private.sign(message)
    
    # Dilithium5 sign
    dil_sig = dilithium5.sign(hybrid_keypair.dilithium5_private, message)
    
    return ed_sig, dil_sig


def hybrid_verify(message: bytes, 
                  ed_sig: bytes, 
                  dil_sig: bytes,
                  hybrid_public: HybridKeyPair) -> bool:
    """Verify both signatures"""
    # Verify Ed25519
    try:
        ed_public = ed25519.Ed25519PublicKey.from_public_bytes(
            hybrid_public.ed25519_public
        )
        ed_public.verify(ed_sig, message)
    except InvalidSignature:
        return False
    
    # Verify Dilithium5
    try:
        dilithium5.verify(hybrid_public.dilithium5_public, message, dil_sig)
        return True
    except Exception:
        return False


def create_hybrid_proof(message: bytes, hybrid_keypair: HybridKeyPair) -> Dict[str, str]:
    """Create a hybrid proof for the genesis anchor"""
    ed_sig, dil_sig = hybrid_sign(message, hybrid_keypair)
    
    return {
        'message': message.hex(),
        'ed25519_signature': ed_sig.hex(),
        'dilithium5_signature': dil_sig.hex(),
        'ed25519_public': hybrid_keypair.ed25519_public.hex(),
        'dilithium5_public': hybrid_keypair.dilithium5_public.hex(),
        'anchor_hash': hybrid_keypair._compute_anchor_hash()
    }


TEST_MESSAGE = b"SCM Genesis Anchor - Quantum Safe Birth - 2026-02-19"
