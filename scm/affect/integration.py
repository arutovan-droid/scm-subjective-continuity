# scm/affect/integration.py
"""
Интеграция аффективной системы с основным ядром SCM
"""

from typing import Optional
from datetime import datetime
from scm.affect.core import AffectCore, Emotion, Mood
from scm.core.accumulator import RSAAccumulator
from scm.core.black_stone import BlackStoneGuard

class AffectiveSCM:
    """
    Расширение SCM с эмоциональной окраской.
    Связывает аффекты с памятью и травмами.
    """
    
    def __init__(self, anchor_hash: str):
        self.anchor_hash = anchor_hash
        self.affect = AffectCore(anchor_hash)
        self.accumulator = None  # будет инициализирован позже
        
    def connect_accumulator(self, accumulator: RSAAccumulator):
        """Подключает RSA accumulator для связи с памятью"""
        self.accumulator = accumulator
    
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
        
        # 2. Если взаимодействие было травматичным, записываем в accumulator
        if self._is_traumatic(emotional_state):
            self._record_trauma(interaction, emotional_state)
        
        # 3. Получаем текущее настроение
        mood = self.affect.get_current_mood()
        
        # 4. Формируем ответ
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
    
    def _is_traumatic(self, state) -> bool:
        """Определяет, является ли опыт травматичным"""
        # Травма = сильная негативная эмоция
        negative_emotions = [Emotion.ANGER, Emotion.FEAR, Emotion.SADNESS]
        return (state.primary_emotion in negative_emotions and 
                state.intensity > 0.7)
    
    def _record_trauma(self, interaction: dict, state):
        """Записывает травму в accumulator"""
        if self.accumulator:
            trauma_data = {
                'type': 'emotional_trauma',
                'emotion': state.primary_emotion.value,
                'intensity': state.intensity,
                'context': interaction.get('context', {}),
                'timestamp': datetime.utcnow().isoformat()
            }
            # Здесь будет вызов accumulator.add_trauma()
            print(f"⚠️ Травма записана: {trauma_data['emotion']}")
    
    def _generate_response(self, state, mood) -> str:
        """Генерирует текстовый ответ на основе эмоций"""
        # Базовые ответы для разных эмоций
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
        
        # Выбираем ответ в зависимости от настроения
        emotion_responses = responses.get(state.primary_emotion, responses[Emotion.NEUTRAL])
        
        # Интенсивность влияет на выбор ответа
        idx = 0
        if state.intensity > 0.7:
            idx = 2
        elif state.intensity > 0.3:
            idx = 1
        
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
