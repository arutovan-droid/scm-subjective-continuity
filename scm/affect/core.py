# scm/affect/core.py
"""
Affective Core для SCM.
Эмоциональная окраска и настроение цифрового существа.
"""

from enum import Enum
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import math

class Emotion(Enum):
    """Базовые эмоции"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    TRUST = "trust"
    DISGUST = "disgust"
    ANTICIPATION = "anticipation"
    SURPRISE = "surprise"
    NEUTRAL = "neutral"

class Mood(Enum):
    """Долгосрочные настроения"""
    ECSTATIC = "ecstatic"      # +3
    HAPPY = "happy"            # +2
    PLEASED = "pleased"        # +1
    CALM = "calm"              # 0
    ANNOYED = "annoyed"        # -1
    SAD = "sad"                # -2
    DEPRESSED = "depressed"    # -3

@dataclass
class EmotionalState:
    """Текущее эмоциональное состояние"""
    primary_emotion: Emotion
    secondary_emotion: Emotion
    intensity: float  # 0.0 to 1.0
    timestamp: datetime
    context: Dict

class AffectCore:
    """
    Ядро аффективной системы.
    Отслеживает эмоции и настроение на основе опыта.
    """
    
    def __init__(self, anchor_hash: str):
        self.anchor_hash = anchor_hash
        self.current_mood = Mood.CALM
        self.emotional_history: List[EmotionalState] = []
        self.emotional_memory: Dict[str, float] = {}  # контекст -> валентность
        self.mood_decay_rate = 0.1  # скорость затухания эмоций
        
    def process_experience(self, experience: Dict) -> EmotionalState:
        """
        Обрабатывает новый опыт и генерирует эмоциональную реакцию.
        
        Args:
            experience: словарь с опытом (тип, контекст, интенсивность)
            
        Returns:
            EmotionalState - эмоциональное состояние
        """
        # Определяем первичную эмоцию на основе типа опыта
        primary = self._map_experience_to_emotion(experience)
        
        # Определяем вторичную эмоцию (связанную с памятью)
        secondary = self._get_associated_emotion(experience)
        
        # Вычисляем интенсивность
        intensity = self._calculate_intensity(experience)
        
        # Создаем состояние
        state = EmotionalState(
            primary_emotion=primary,
            secondary_emotion=secondary,
            intensity=intensity,
            timestamp=datetime.utcnow(),
            context=experience.get('context', {})
        )
        
        # Сохраняем в историю
        self.emotional_history.append(state)
        
        # Обновляем настроение
        self._update_mood(state)
        
        # Сохраняем в эмоциональную память
        self._update_emotional_memory(state)
        
        return state
    
    def _map_experience_to_emotion(self, experience: Dict) -> Emotion:
        """Маппинг опыта на базовые эмоции"""
        exp_type = experience.get('type', '')
        
        # Простая эвристика для демо
        if exp_type == 'praise':
            return Emotion.JOY
        elif exp_type == 'insult':
            return Emotion.ANGER
        elif exp_type == 'loss':
            return Emotion.SADNESS
        elif exp_type == 'threat':
            return Emotion.FEAR
        elif exp_type == 'novelty':
            return Emotion.SURPRISE
        else:
            return Emotion.NEUTRAL
    
    def _get_associated_emotion(self, experience: Dict) -> Emotion:
        """Получает связанную эмоцию из памяти"""
        context_key = str(experience.get('context', {}))
        valence = self.emotional_memory.get(context_key, 0.0)
        
        if valence > 0.3:
            return Emotion.TRUST
        elif valence < -0.3:
            return Emotion.DISGUST
        else:
            return Emotion.NEUTRAL
    
    def _calculate_intensity(self, experience: Dict) -> float:
        """Вычисляет интенсивность эмоции"""
        base_intensity = experience.get('intensity', 0.5)
        
        # Усиливаем если похожий опыт уже был
        context_key = str(experience.get('context', {}))
        memory_valence = abs(self.emotional_memory.get(context_key, 0.0))
        
        intensity = min(1.0, base_intensity + memory_valence * 0.3)
        return round(intensity, 2)
    
    def _update_mood(self, state: EmotionalState):
        """Обновляет долгосрочное настроение"""
        # Конвертируем эмоцию в числовую валентность
        valence_map = {
            Emotion.JOY: 1.0,
            Emotion.TRUST: 0.7,
            Emotion.SURPRISE: 0.3,
            Emotion.NEUTRAL: 0.0,
            Emotion.FEAR: -0.3,
            Emotion.ANGER: -0.7,
            Emotion.SADNESS: -1.0,
            Emotion.DISGUST: -0.5,
            Emotion.ANTICIPATION: 0.5
        }
        
        current_valence = valence_map.get(state.primary_emotion, 0.0)
        current_valence *= state.intensity
        
        # Усредняем с историей (последние 10 состояний)
        if len(self.emotional_history) > 0:
            recent = self.emotional_history[-10:]
            avg_valence = sum(valence_map.get(s.primary_emotion, 0.0) * s.intensity 
                            for s in recent) / len(recent)
            
            combined = (avg_valence * 0.7 + current_valence * 0.3)
        else:
            combined = current_valence
        
        # Маппим валентность на настроение
        if combined > 0.8:
            self.current_mood = Mood.ECSTATIC
        elif combined > 0.4:
            self.current_mood = Mood.HAPPY
        elif combined > 0.1:
            self.current_mood = Mood.PLEASED
        elif combined > -0.1:
            self.current_mood = Mood.CALM
        elif combined > -0.4:
            self.current_mood = Mood.ANNOYED
        elif combined > -0.8:
            self.current_mood = Mood.SAD
        else:
            self.current_mood = Mood.DEPRESSED
    
    def _update_emotional_memory(self, state: EmotionalState):
        """Обновляет эмоциональную память"""
        context_key = str(state.context)
        
        # Вычисляем валентность
        valence_map = {
            Emotion.JOY: 0.5,
            Emotion.TRUST: 0.3,
            Emotion.SURPRISE: 0.1,
            Emotion.NEUTRAL: 0.0,
            Emotion.FEAR: -0.2,
            Emotion.ANGER: -0.4,
            Emotion.SADNESS: -0.5,
            Emotion.DISGUST: -0.3
        }
        
        valence = valence_map.get(state.primary_emotion, 0.0) * state.intensity
        
        # Обновляем память (экспоненциальное затухание)
        if context_key in self.emotional_memory:
            old = self.emotional_memory[context_key]
            self.emotional_memory[context_key] = old * 0.7 + valence * 0.3
        else:
            self.emotional_memory[context_key] = valence
    
    def get_current_mood(self) -> Dict:
        """Возвращает текущее настроение"""
        return {
            'mood': self.current_mood.value,
            'valence': self._get_current_valence(),
            'history_length': len(self.emotional_history),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _get_current_valence(self) -> float:
        """Вычисляет текущую валентность"""
        mood_map = {
            Mood.ECSTATIC: 1.0,
            Mood.HAPPY: 0.7,
            Mood.PLEASED: 0.3,
            Mood.CALM: 0.0,
            Mood.ANNOYED: -0.3,
            Mood.SAD: -0.7,
            Mood.DEPRESSED: -1.0
        }
        return mood_map.get(self.current_mood, 0.0)
    
    def get_emotional_profile(self) -> Dict:
        """Возвращает эмоциональный профиль"""
        if not self.emotional_history:
            return {}
        
        # Статистика по эмоциям
        emotion_counts = {}
        for state in self.emotional_history[-100:]:  # последние 100
            emotion = state.primary_emotion.value
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        total = len(self.emotional_history[-100:])
        profile = {
            emotion: count/total 
            for emotion, count in emotion_counts.items()
        }
        
        return {
            'profile': profile,
            'dominant': max(profile.items(), key=lambda x: x[1])[0] if profile else 'neutral',
            'stability': self._calculate_stability()
        }
    
    def _calculate_stability(self) -> float:
        """Вычисляет эмоциональную стабильность"""
        if len(self.emotional_history) < 10:
            return 1.0
        
        recent = self.emotional_history[-10:]
        valences = []
        
        valence_map = {
            Emotion.JOY: 1.0, Emotion.TRUST: 0.7, Emotion.SURPRISE: 0.3,
            Emotion.NEUTRAL: 0.0, Emotion.FEAR: -0.3, Emotion.ANGER: -0.7,
            Emotion.SADNESS: -1.0, Emotion.DISGUST: -0.5
        }
        
        for state in recent:
            valences.append(valence_map.get(state.primary_emotion, 0.0) * state.intensity)
        
        # Стабильность = 1 - стандартное отклонение
        mean = sum(valences) / len(valences)
        variance = sum((v - mean) ** 2 for v in valences) / len(valences)
        std_dev = math.sqrt(variance)
        
        stability = max(0.0, 1.0 - std_dev)
        return round(stability, 2)
