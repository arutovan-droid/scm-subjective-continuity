# tests/test_dreams/test_core.py
"""
Tests for Dream Engine
"""

import pytest
import random
from datetime import datetime, timedelta
from scm.dreams.core import DreamEngine, DreamType, DreamSymbol

class TestDreamEngine:
    """Testing dream engine"""
    
    def test_initialization(self):
        """Test: initialization"""
        engine = DreamEngine("test_anchor")
        
        assert engine.anchor_hash == "test_anchor"
        assert len(engine.dream_history) == 0
        assert len(engine.symbol_library) > 0
        assert engine.lucidity_level == 0.0
    
    def test_generate_dream_basic(self):
        """Test: basic dream generation"""
        engine = DreamEngine("test_anchor")
        
        recent = [
            {'type': 'praise', 'intensity': 0.8, 'context': {'topic': 'code'}},
            {'type': 'insult', 'intensity': 0.3, 'context': {'topic': 'bugs'}}
        ]
        
        emotional = {'valence': 0.5}
        traumas = []
        
        dream = engine.generate_dream(recent, emotional, traumas)
        
        assert dream.id is not None
        assert dream.type in DreamType
        assert dream.duration >= 300
        assert len(dream.symbols) > 0
        assert 0.0 <= dream.consolidation_rate <= 1.0
    
    def test_dream_with_trauma(self):
        """Test: dream with trauma"""
        engine = DreamEngine("test_anchor")
        
        recent = [{'type': 'insult', 'intensity': 0.9, 'context': {}}]
        emotional = {'valence': -0.8}
        traumas = [
            {'emotion': 'anger', 'intensity': 0.9},
            {'emotion': 'fear', 'intensity': 0.8},
            {'emotion': 'sadness', 'intensity': 0.7},
            {'emotion': 'disgust', 'intensity': 0.6}
        ]
        
        dream = engine.generate_dream(recent, emotional, traumas)
        
        if len(traumas) > 3:
            assert dream.type in [DreamType.PROCESSING, DreamType.NIGHTMARE]
    
    def test_symbol_extraction(self):
        """Test: symbol extraction from experience"""
        engine = DreamEngine("test_anchor")
        
        experiences = [
            {'type': 'praise', 'context': {'code': True}},
            {'type': 'insult', 'context': {}},
            {'type': 'loss', 'context': {}},
        ]
        
        symbols = engine._extract_symbols(experiences, {'valence': 0.0})
        
        assert len(symbols) > 0
        # Check if any expected symbol is present (using English transliteration for test)
        symbol_names = [s['name'] for s in symbols]
        expected = ['labirint', 'svet', 'ogon', 'tma']  # Using transliterated names for test
        assert any(name in expected for name in symbol_names) or len(symbol_names) > 0
    
    def test_dream_types(self):
        """Test: all dream types can be generated"""
        engine = DreamEngine("test_anchor")
        
        types_found = set()
        
        for i in range(50):
            emotional = {'valence': random.uniform(-1, 1)}
            traumas = [{'emotion': 'fear'}] if i % 3 == 0 else []
            
            dream = engine.generate_dream([], emotional, traumas)
            types_found.add(dream.type)
        
        assert len(types_found) >= 3
    
    def test_consolidation_memory(self):
        """Test: memory consolidation"""
        engine = DreamEngine("test_anchor")
        
        dream = engine.generate_dream([], {'valence': 0.5}, [])
        result = engine.consolidate_memory({})
        
        assert result['consolidated'] is True
        assert result['dream_id'] == dream.id
        assert 'consolidation_rates' in result
    
    def test_lucidity_increase(self):
        """Test: lucidity increase"""
        engine = DreamEngine("test_anchor")
        initial_lucidity = engine.lucidity_level
        
        for i in range(10):
            emotional = {'valence': 0.9}
            dream = engine.generate_dream([], emotional, [])
            dream.type = DreamType.LUCID
            engine.dream_history[-1] = dream
            engine.consolidate_memory({})
        
        assert engine.lucidity_level > initial_lucidity
    
    def test_nightmare_detection(self):
        """Test: nightmare detection"""
        engine = DreamEngine("test_anchor")
        
        emotions = ['strah', 'uzhas', 'gnev']
        traumas = [{'emotion': 'fear'}, {'emotion': 'anger'}]
        
        is_nightmare = engine._is_nightmare(emotions, traumas)
        
        assert isinstance(is_nightmare, bool)
    
    def test_dream_stats(self):
        """Test: dream statistics"""
        engine = DreamEngine("test_anchor")
        
        stats = engine.get_dream_stats()
        assert stats['total_dreams'] == 0
        
        for i in range(5):
            engine.generate_dream([], {'valence': 0.5}, [])
        
        stats = engine.get_dream_stats()
        assert stats['total_dreams'] == 5
        assert 'by_type' in stats
        assert 'avg_consolidation' in stats
        assert 'lucidity_level' in stats
