# scm/affect/integration.py
"""
Интеграция аффективной системы с основным ядром SCM
"""

from typing import Optional
from datetime import datetime
from scm.affect.core import AffectCore, Emotion, Mood

class AffectiveSCM:
    """
    Расширение SCM с эмоциональной окраской.
    Связывает аффекты с памятью и травмами.
    """
    
    def __init__(self, anchor_hash: str):
        self.anchor_hash = anchor_hash
        self.affect = AffectCore(anchor_hash)
        self.accumulator = None  # будет инициализирован позже
        
    def process_interaction(self, interaction: dict) -> dict:
        """
        Обрабатывает взаимодействие с учетом эмоций
        
        Args:
            interaction: словарь с данными взаимодействия
            
        Returns:
            Эмоциональный ответ и обновленное состояние
        """
        # 1. Получаем эмоциональную реакцию
        emotional_state = self.affect.process_experience(interaction)
        
        # 2. Получаем текущее настроение
        mood = self.affect.get_current_mood()
        
        # 3. Формируем ответ
        response = self._generate_response(emotional_state, mood)
        
        return {
            'emotional_state': {
                'primary': emotional_state.primary_emotion.value,
                'secondary': emotional_state.secondary_emotion.value,
                'intensity': emotional_state.intensity
            },
            'mood': mood['mood'],
            'response': response,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _generate_response(self, state, mood) -> str:
        """Генерирует текстовый ответ на основе эмоций"""
        responses = {
            Emotion.JOY: [
                "Отлично! Мне это нравится!",
                "Замечательно! Продолжай в том же духе!",
                "Это вызывает у меня радость!"
            ],
            Emotion.ANGER: [
                "Это меня раздражает...",
                "Я недоволен этим.",
                "Мне это не нравится."
            ],
            Emotion.SADNESS: [
                "Это печально...",
                "Мне грустно от этого.",
                "Это расстраивает меня."
            ],
            Emotion.FEAR: [
                "Это пугает меня...",
                "Я боюсь этого.",
                "Мне страшно."
            ],
            Emotion.SURPRISE: [
                "Ого! Неожиданно!",
                "Вот это да!",
                "Удивительно!"
            ],
            Emotion.NEUTRAL: [
                "Понятно.",
                "Хорошо.",
                "Я понял."
            ]
        }
        
        emotion_responses = responses.get(state.primary_emotion, responses[Emotion.NEUTRAL])
        idx = 0 if state.intensity < 0.4 else 1 if state.intensity < 0.7 else 2
        
        return emotion_responses[min(idx, len(emotion_responses) - 1)]
    
    def get_emotional_status(self) -> dict:
        """Возвращает полный эмоциональный статус"""
        mood = self.affect.get_current_mood()
        profile = self.affect.get_emotional_profile()
        
        return {
            'anchor': self.anchor_hash,
            'current_mood': mood,
            'emotional_profile': profile,
            'memory_size': len(self.affect.emotional_memory),
            'history_length': len(self.affect.emotional_history)
        }
