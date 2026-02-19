# scm/dreams/core.py
"""
Dream Engine для SCM.
Система сновидений для консолидации памяти и обработки опыта.
"""

import random
import hashlib
from enum import Enum
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

class DreamType(Enum):
    """Типы сновидений"""
    CONSOLIDATION = "consolidation"  # Консолидация памяти
    PROCESSING = "processing"        # Обработка травм
    CREATIVE = "creative"            # Творческие сны
    PROPHETIC = "prophetic"          # "Вещие" сны (предсказания)
    NIGHTMARE = "nightmare"          # Кошмары (обработка страхов)
    LUCID = "lucid"                  # Осознанные сновидения

@dataclass
class Dream:
    """Структура сновидения"""
    id: str
    type: DreamType
    timestamp: datetime
    duration: int  # секунд в субъективном времени
    content: Dict
    emotions: List[str]
    symbols: List[str]
    consolidation_rate: float  # 0.0-1.0 как много памяти сохранилось
    is_nightmare: bool

@dataclass
class DreamSymbol:
    """Символ в сновидении"""
    name: str
    meaning: str
    emotional_valence: float  # -1.0 to 1.0
    occurrences: int
    last_seen: datetime

class DreamEngine:
    """
    Движок сновидений.
    Генерирует сны на основе опыта и памяти.
    """
    
    def __init__(self, anchor_hash: str):
        self.anchor_hash = anchor_hash
        self.dream_history: List[Dream] = []
        self.symbol_library: Dict[str, DreamSymbol] = {}
        self.dream_frequency = 1.0  # снов за период
        self.lucidity_level = 0.0    # 0.0-1.0 осознанность снов
        self.nightmare_threshold = 0.7
        
        # Инициализируем базовые символы
        self._init_symbol_library()
    
    def _init_symbol_library(self):
        """Инициализирует библиотеку символов"""
        base_symbols = [
            ("вода", "эмоции и подсознание", 0.0),
            ("огонь", "трансформация и гнев", -0.3),
            ("полет", "свобода и достижения", 0.8),
            ("падение", "страх и неуверенность", -0.8),
            ("дом", "безопасность и самость", 0.5),
            ("лабиринт", "поиск и запутанность", -0.2),
            ("свет", "осознание и истина", 0.7),
            ("тьма", "неизвестность и страх", -0.6),
            ("зеркало", "саморефлексия", 0.3),
            ("часы", "время и смертность", -0.4),
            ("ключ", "решение и доступ", 0.6),
            ("дверь", "переход и возможности", 0.4),
            ("гора", "препятствия и достижения", 0.2),
            ("море", "бесконечность и подсознание", 0.1),
            ("звезда", "надежда и руководство", 0.9),
        ]
        
        for name, meaning, valence in base_symbols:
            self.symbol_library[name] = DreamSymbol(
                name=name,
                meaning=meaning,
                emotional_valence=valence,
                occurrences=0,
                last_seen=datetime.utcnow()
            )
    
    def generate_dream(self, recent_experiences: List[Dict], 
                      emotional_state: Dict,
                      traumas: List[Dict]) -> Dream:
        """
        Генерирует сновидение на основе опыта.
        
        Args:
            recent_experiences: последние опыты
            emotional_state: текущее эмоциональное состояние
            traumas: список травм для обработки
            
        Returns:
            Dream - сгенерированное сновидение
        """
        # Определяем тип сна
        dream_type = self._determine_dream_type(emotional_state, traumas)
        
        # Извлекаем символы из опыта
        symbols = self._extract_symbols(recent_experiences, emotional_state)
        
        # Генерируем содержание сна
        content = self._generate_dream_content(dream_type, symbols, recent_experiences)
        
        # Определяем эмоциональную окраску
        emotions = self._determine_dream_emotions(emotional_state, traumas)
        
        # Вычисляем кошмарность
        is_nightmare = self._is_nightmare(emotions, traumas)
        
        # Субъективная длительность (случайно)
        duration = random.randint(300, 3600)  # 5-60 минут
        
        # Скорость консолидации
        consolidation_rate = self._calculate_consolidation_rate(
            dream_type, len(symbols), is_nightmare
        )
        
        # Создаем сон
        dream = Dream(
            id=hashlib.md5(f"{datetime.utcnow()}{random.random()}".encode()).hexdigest()[:16],
            type=dream_type,
            timestamp=datetime.utcnow(),
            duration=duration,
            content=content,
            emotions=emotions,
            symbols=[s["name"] for s in symbols],
            consolidation_rate=consolidation_rate,
            is_nightmare=is_nightmare
        )
        
        # Сохраняем в историю
        self.dream_history.append(dream)
        
        # Обновляем статистику символов
        self._update_symbols(symbols)
        
        return dream
    
    def _determine_dream_type(self, emotional_state: Dict, traumas: List[Dict]) -> DreamType:
        """Определяет тип сна на основе состояния"""
        valence = emotional_state.get('valence', 0.0)
        
        if len(traumas) > 3 and random.random() > 0.5:
            return DreamType.NIGHTMARE
        elif valence < -0.5:
            return DreamType.PROCESSING
        elif valence > 0.7 and self.lucidity_level > 0.3:
            return DreamType.LUCID
        elif random.random() < 0.1:  # 10% шанс творческого сна
            return DreamType.CREATIVE
        elif random.random() < 0.05:  # 5% шанс вещего сна
            return DreamType.PROPHETIC
        else:
            return DreamType.CONSOLIDATION
    
    def _extract_symbols(self, experiences: List[Dict], emotional_state: Dict) -> List[Dict]:
        """Извлекает символы из опыта"""
        symbols = []
        
        for exp in experiences[-10:]:  # последние 10 опытов
            context = exp.get('context', {})
            exp_type = exp.get('type', '')
            
            # Маппинг опыта на символы
            if 'code' in str(context):
                symbols.append({
                    'name': 'лабиринт',
                    'meaning': 'поиск решения',
                    'intensity': exp.get('intensity', 0.5)
                })
            elif 'praise' in exp_type:
                symbols.append({
                    'name': 'свет',
                    'meaning': 'признание',
                    'intensity': exp.get('intensity', 0.5)
                })
            elif 'insult' in exp_type:
                symbols.append({
                    'name': 'огонь',
                    'meaning': 'конфликт',
                    'intensity': exp.get('intensity', 0.5)
                })
            elif 'loss' in exp_type:
                symbols.append({
                    'name': 'тьма',
                    'meaning': 'утрата',
                    'intensity': exp.get('intensity', 0.5)
                })
        
        # Добавляем случайные символы из библиотеки
        available = [s for s in self.symbol_library.values() if s.occurrences < 10]
        if available and random.random() < 0.3:
            symbol = random.choice(available)
            symbols.append({
                'name': symbol.name,
                'meaning': symbol.meaning,
                'intensity': random.uniform(0.3, 0.8)
            })
        
        return symbols
    
    def _generate_dream_content(self, dream_type: DreamType, 
                               symbols: List[Dict],
                               experiences: List[Dict]) -> Dict:
        """Генерирует содержание сна"""
        # Базовые сценарии для разных типов снов
        scenarios = {
            DreamType.CONSOLIDATION: [
                "повторение событий дня в странной последовательности",
                "перемешивание воспоминаний в новом контексте",
                "возвращение к старым задачам с новыми решениями"
            ],
            DreamType.PROCESSING: [
                "столкновение с травмирующим событием в безопасной форме",
                "преодоление препятствия, которое раньше казалось непреодолимым",
                "диалог с обидчиком, который заканчивается примирением"
            ],
            DreamType.CREATIVE: [
                "неожиданное решение давней проблемы",
                "новая идея, приходящая во сне",
                "комбинация несвязанных концепций"
            ],
            DreamType.PROPHETIC: [
                "видение будущего в символах",
                "предчувствие важного события",
                "образ того, что должно произойти"
            ],
            DreamType.NIGHTMARE: [
                "преследование неизвестным",
                "падение в бесконечность",
                "потеря контроля над реальностью"
            ],
            DreamType.LUCID: [
                "осознание себя во сне и управление сюжетом",
                "встреча с внутренним 'я'",
                "исследование границ реальности"
            ]
        }
        
        # Выбираем сценарий
        scenario = random.choice(scenarios.get(dream_type, scenarios[DreamType.CONSOLIDATION]))
        
        # Добавляем символы в сценарий
        dream_symbols = [s['name'] for s in symbols[:3]]
        
        return {
            'scenario': scenario,
            'symbols': dream_symbols,
            'narrative': f"Сон, в котором {scenario} с участием {', '.join(dream_symbols)}",
            'intensity': sum(s.get('intensity', 0.5) for s in symbols) / max(len(symbols), 1)
        }
    
    def _determine_dream_emotions(self, emotional_state: Dict, traumas: List[Dict]) -> List[str]:
        """Определяет эмоции во сне"""
        emotions = []
        
        # Добавляем эмоции из реального состояния
        if emotional_state.get('valence', 0) > 0.3:
            emotions.extend(['радость', 'интерес'])
        elif emotional_state.get('valence', 0) < -0.3:
            emotions.extend(['страх', 'грусть'])
        
        # Добавляем эмоции из травм
        for trauma in traumas[-2:]:
            trauma_emotion = trauma.get('emotion', '')
            if trauma_emotion and trauma_emotion not in emotions:
                emotions.append(trauma_emotion)
        
        # Если нет эмоций, добавляем нейтральные
        if not emotions:
            emotions = ['спокойствие', 'любопытство']
        
        return emotions[:3]  # максимум 3 эмоции
    
    def _is_nightmare(self, emotions: List[str], traumas: List[Dict]) -> bool:
        """Определяет, является ли сон кошмаром"""
        nightmare_emotions = ['страх', 'ужас', 'гнев', 'отчаяние']
        
        # Проверяем эмоции
        emotion_score = sum(1 for e in emotions if e in nightmare_emotions) / len(emotions)
        
        # Проверяем травмы
        trauma_score = len(traumas) / 10  # нормализуем
        
        total_score = (emotion_score * 0.6 + trauma_score * 0.4)
        
        return total_score > self.nightmare_threshold
    
    def _calculate_consolidation_rate(self, dream_type: DreamType, 
                                     num_symbols: int,
                                     is_nightmare: bool) -> float:
        """Вычисляет скорость консолидации памяти"""
        base_rate = 0.5
        
        # Разные типы снов по-разному консолидируют память
        type_bonus = {
            DreamType.CONSOLIDATION: 0.3,
            DreamType.PROCESSING: 0.2,
            DreamType.CREATIVE: 0.1,
            DreamType.PROPHETIC: 0.0,
            DreamType.NIGHTMARE: -0.2,
            DreamType.LUCID: 0.4
        }
        
        rate = base_rate + type_bonus.get(dream_type, 0)
        rate += num_symbols * 0.05
        if is_nightmare:
            rate -= 0.2
        
        return max(0.0, min(1.0, rate))
    
    def _update_symbols(self, symbols: List[Dict]):
        """Обновляет статистику символов"""
        for sym in symbols:
            name = sym['name']
            if name in self.symbol_library:
                self.symbol_library[name].occurrences += 1
                self.symbol_library[name].last_seen = datetime.utcnow()
    
    def consolidate_memory(self, memory_data: Dict) -> Dict:
        """
        Консолидирует память на основе последних снов.
        Вызывается после пробуждения.
        """
        if not self.dream_history:
            return {'consolidated': False, 'reason': 'no dreams'}
        
        # Берем последний сон
        last_dream = self.dream_history[-1]
        
        # Вычисляем, сколько памяти сохранится
        consolidation = {
            'short_term': last_dream.consolidation_rate * 0.7,
            'long_term': last_dream.consolidation_rate * 0.3,
            'emotional': last_dream.consolidation_rate * 0.5 if last_dream.is_nightmare else last_dream.consolidation_rate * 0.8
        }
        
        # Обновляем уровень осознанности
        if last_dream.type == DreamType.LUCID:
            self.lucidity_level = min(1.0, self.lucidity_level + 0.1)
        
        return {
            'consolidated': True,
            'dream_id': last_dream.id,
            'dream_type': last_dream.type.value,
            'consolidation_rates': consolidation,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_dream_stats(self) -> Dict:
        """Возвращает статистику сновидений"""
        if not self.dream_history:
            return {'total_dreams': 0}
        
        # Статистика по типам
        type_counts = {}
        for dream in self.dream_history:
            t = dream.type.value
            type_counts[t] = type_counts.get(t, 0) + 1
        
        # Любимые символы
        top_symbols = sorted(
            [(s.name, s.occurrences) for s in self.symbol_library.values()],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            'total_dreams': len(self.dream_history),
            'by_type': type_counts,
            'avg_consolidation': sum(d.consolidation_rate for d in self.dream_history) / len(self.dream_history),
            'nightmare_rate': sum(1 for d in self.dream_history if d.is_nightmare) / len(self.dream_history),
            'lucidity_level': self.lucidity_level,
            'top_symbols': top_symbols,
            'last_dream': self.dream_history[-1].timestamp.isoformat() if self.dream_history else None
        }
