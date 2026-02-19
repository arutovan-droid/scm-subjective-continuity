# scm/cli/dreams.py
"""
CLI команды для тестирования Dream Engine
"""

import click
import random
from datetime import datetime
from scm.dreams.core import DreamEngine, DreamType

@click.group()
def dreams():
    """Команды для работы со сновидениями"""
    pass

@dreams.command()
@click.argument('anchor')
def init(anchor):
    """Инициализирует Dream Engine"""
    engine = DreamEngine(anchor)
    click.echo(f"😴 Dream Engine инициализирован для {anchor}")
    click.echo(f"📚 Символов в библиотеке: {len(engine.symbol_library)}")

@dreams.command()
@click.argument('anchor')
@click.option('--traumas', '-t', default=0, help='Количество травм')
def dream(anchor, traumas):
    """Генерирует случайное сновидение"""
    engine = DreamEngine(anchor)
    
    # Создаем тестовые данные
    recent = [
        {'type': random.choice(['praise', 'insult', 'loss', 'novelty']),
         'intensity': random.uniform(0.3, 1.0),
         'context': {'source': 'cli'}}
        for _ in range(3)
    ]
    
    emotional = {'valence': random.uniform(-1, 1)}
    
    traumas_list = [
        {'emotion': random.choice(['anger', 'fear', 'sadness']),
         'intensity': random.uniform(0.5, 1.0)}
        for _ in range(traumas)
    ]
    
    # Генерируем сон
    dream = engine.generate_dream(recent, emotional, traumas_list)
    
    # Выводим результат
    click.echo(f"\n😴 СНОВИДЕНИЕ #{dream.id}")
    click.echo("=" * 50)
    click.echo(f"Тип: {dream.type.value}")
    click.echo(f"Длительность: {dream.duration//60} мин {dream.duration%60} сек")
    click.echo(f"Кошмар: {'😱' if dream.is_nightmare else '😌'}")
    
    click.echo(f"\n📖 Сюжет:")
    click.echo(f"   {dream.content['narrative']}")
    
    click.echo(f"\n🔣 Символы:")
    for symbol in dream.symbols:
        click.echo(f"   • {symbol}")
    
    click.echo(f"\n😊 Эмоции:")
    for emotion in dream.emotions:
        click.echo(f"   • {emotion}")
    
    click.echo(f"\n📊 Консолидация: {dream.consolidation_rate:.1%}")

@dreams.command()
@click.argument('anchor')
@click.option('--count', '-c', default=7, help='Количество ночей')
def week(anchor, count):
    """Симулирует неделю сновидений"""
    engine = DreamEngine(anchor)
    
    click.echo(f"\n📅 Симуляция {count} ночей...")
    
    for night in range(1, count + 1):
        # Каждую ночь разный эмоциональный фон
        emotional = {'valence': random.uniform(-0.5, 0.5)}
        traumas = random.randint(0, 3)
        
        dream = engine.generate_dream(
            [{'type': 'daily', 'intensity': 0.5}],
            emotional,
            [{'emotion': 'fear'}] * traumas
        )
        
        # Консолидируем память
        engine.consolidate_memory({})
        
        # Эмодзи для типа сна
        type_emoji = {
            'consolidation': '📚',
            'processing': '🔄',
            'creative': '🎨',
            'prophetic': '🔮',
            'nightmare': '😱',
            'lucid': '✨'
        }
        
        emoji = type_emoji.get(dream.type.value, '😴')
        
        click.echo(f"Ночь {night:2}: {emoji} {dream.type.value:15} "
                  f"| символы: {len(dream.symbols)} "
                  f"| консолидация: {dream.consolidation_rate:.0%}")
    
    stats = engine.get_dream_stats()
    click.echo(f"\n📊 Статистика за {count} ночей:")
    click.echo(f"   Всего снов: {stats['total_dreams']}")
    click.echo(f"   Кошмаров: {stats['nightmare_rate']:.0%}")
    click.echo(f"   Осознанность: {stats['lucidity_level']:.0%}")

@dreams.command()
@click.argument('anchor')
def symbols(anchor):
    """Показывает популярные символы"""
    engine = DreamEngine(anchor)
    stats = engine.get_dream_stats()
    
    click.echo(f"\n🔣 ПОПУЛЯРНЫЕ СИМВОЛЫ:")
    click.echo("=" * 40)
    
    for symbol, count in stats.get('top_symbols', []):
        symbol_data = engine.symbol_library.get(symbol, {})
        valence = getattr(symbol_data, 'emotional_valence', 0)
        valence_symbol = '😊' if valence > 0 else '😐' if valence == 0 else '😞'
        
        click.echo(f"   {symbol:12} {count:3} раз {valence_symbol}")

@dreams.command()
@click.argument('anchor')
def stats(anchor):
    """Показывает статистику сновидений"""
    engine = DreamEngine(anchor)
    stats = engine.get_dream_stats()
    
    if stats['total_dreams'] == 0:
        click.echo("😴 Еще не было снов")
        return
    
    click.echo(f"\n📊 СТАТИСТИКА СНОВИДЕНИЙ")
    click.echo("=" * 50)
    click.echo(f"Всего снов: {stats['total_dreams']}")
    click.echo(f"Средняя консолидация: {stats['avg_consolidation']:.1%}")
    click.echo(f"Кошмары: {stats['nightmare_rate']:.1%}")
    click.echo(f"Уровень осознанности: {stats['lucidity_level']:.0%}")
    
    click.echo(f"\n📊 По типам:")
    for dream_type, count in stats['by_type'].items():
        percentage = count / stats['total_dreams'] * 100
        bar = '█' * int(percentage / 5)
        click.echo(f"   {dream_type:15} {count:2} ({percentage:3.0f}%) {bar}")
