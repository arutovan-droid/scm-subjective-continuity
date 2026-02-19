# tests/test_affect/test_core.py
"""
Тесты для аффективного ядра
"""

import pytest
from datetime import datetime, timedelta
from scm.affect.core import AffectCore, Emotion, Mood, EmotionalState

class TestAffectCore:
    """Тестируем эмоциональную систему"""
    
    def test_initial_state(self):
        """Тест: начальное состояние"""
        affect = AffectCore("test_anchor_123")
        
        assert affect.anchor_hash == "test_anchor_123"
        assert affect.current_mood == Mood.CALM
        assert len(affect.emotional_history) == 0
        assert len(affect.emotional_memory) == 0
    
    def test_process_positive_experience(self):
        """Тест: обработка позитивного опыта"""
        affect = AffectCore("test_anchor")
        
        experience = {
            'type': 'praise',
            'intensity': 0.8,
            'context': {'source': 'user', 'topic': 'performance'}
        }
        
        state = affect.process_experience(experience)
        
        assert state.primary_emotion == Emotion.JOY
        assert state.intensity == 0.8
        assert affect.current_mood in [Mood.HAPPY, Mood.PLEASED]
    
    def test_process_negative_experience(self):
        """Тест: обработка негативного опыта"""
        affect = AffectCore("test_anchor")
        
        experience = {
            'type': 'insult',
            'intensity': 0.6,
            'context': {'source': 'user', 'topic': 'appearance'}
        }
        
        state = affect.process_experience(experience)
        
        assert state.primary_emotion == Emotion.ANGER
        assert state.intensity == 0.6
        assert affect.current_mood in [Mood.ANNOYED, Mood.SAD]
    
    def test_emotional_memory(self):
        """Тест: эмоциональная память работает"""
        affect = AffectCore("test_anchor")
        
        # Первый опыт
        exp1 = {
            'type': 'praise',
            'intensity': 0.5,
            'context': {'topic': 'code'}
        }
        affect.process_experience(exp1)
        
        # Похожий опыт должен вызвать более сильную реакцию
        exp2 = {
            'type': 'praise',
            'intensity': 0.5,
            'context': {'topic': 'code'}
        }
        
        state2 = affect.process_experience(exp2)
        
        # Интенсивность должна быть выше из-за памяти
        assert state2.intensity > 0.5
    
    def test_mood_decay(self):
        """Тест: настроение меняется со временем"""
        affect = AffectCore("test_anchor")
        
        # Вызываем сильную позитивную эмоцию
        affect.process_experience({
            'type': 'praise',
            'intensity': 1.0,
            'context': {}
        })
        
        assert affect.current_mood == Mood.ECSTATIC
        
        # Добавляем нейтральные события
        for i in range(10):
            affect.process_experience({
                'type': 'neutral',
                'intensity': 0.1,
                'context': {'i': i}
            })
        
        # Настроение должно стать более спокойным
        assert affect.current_mood != Mood.ECSTATIC
    
    def test_emotional_profile(self):
        """Тест: эмоциональный профиль"""
        affect = AffectCore("test_anchor")
        
        # Серия разных эмоций
        experiences = [
            {'type': 'praise', 'intensity': 0.8},
            {'type': 'praise', 'intensity': 0.6},
            {'type': 'insult', 'intensity': 0.4},
            {'type': 'loss', 'intensity': 0.7},
            {'type': 'novelty', 'intensity': 0.5},
        ]
        
        for exp in experiences:
            affect.process_experience(exp)
        
        profile = affect.get_emotional_profile()
        
        assert 'profile' in profile
        assert 'dominant' in profile
        assert 'stability' in profile
        assert 0 <= profile['stability'] <= 1
    
    def test_emotional_history(self):
        """Тест: история эмоций сохраняется"""
        affect = AffectCore("test_anchor")
        
        for i in range(5):
            affect.process_experience({
                'type': 'praise',
                'intensity': 0.5,
                'context': {'i': i}
            })
        
        assert len(affect.emotional_history) == 5
        
        # Проверяем временные метки
        timestamps = [e.timestamp for e in affect.emotional_history]
        assert all(isinstance(t, datetime) for t in timestamps)
