# scm/cli/affect.py
"""
CLI команды для тестирования аффективной системы
"""

import click
import random
from scm.affect.core import AffectCore
from scm.affect.integration import AffectiveSCM

@click.group()
def affect():
    """Команды для работы с эмоциональной системой"""
    pass

@affect.command()
@click.argument('anchor')
def init(anchor):
    """Инициализирует аффективную систему для якоря"""
    scm = AffectiveSCM(anchor)
    click.echo(f"🎭 Эмоциональная система инициализирована для {anchor}")
    click.echo(f"Текущее настроение: {scm.affect.current_mood.value}")

@affect.command()
@click.argument('anchor')
@click.option('--type', '-t', default='neutral', 
              help='Тип опыта (praise/insult/loss/threat/novelty)')
@click.option('--intensity', '-i', default=0.5, type=float,
              help='Интенсивность (0.0-1.0)')
def experience(anchor, type, intensity):
    """Добавляет опыт и показывает эмоциональную реакцию"""
    scm = AffectiveSCM(anchor)
    
    interaction = {
        'type': type,
        'intensity': intensity,
        'context': {'source': 'cli', 'timestamp': 'now'}
    }
    
    response = scm.process_interaction(interaction)
    
    click.echo(f"\n📝 Опыт: {type} (интенсивность: {intensity})")
    click.echo(f"🎭 Эмоция: {response['emotional_state']['primary']} + {response['emotional_state']['secondary']}")
    click.echo(f"💪 Интенсивность: {response['emotional_state']['intensity']}")
    click.echo(f"😊 Настроение: {response['mood']}")
    click.echo(f"💬 Ответ: {response['response']}")

@affect.command()
@click.argument('anchor')
def status(anchor):
    """Показывает текущий эмоциональный статус"""
    scm = AffectiveSCM(anchor)
    status = scm.get_emotional_status()
    
    click.echo(f"\n📊 ЭМОЦИОНАЛЬНЫЙ СТАТУС для {anchor}")
    click.echo("=" * 50)
    click.echo(f"😊 Текущее настроение: {status['current_mood']['mood']}")
    click.echo(f"📈 Валентность: {status['current_mood']['valence']}")
    click.echo(f"📊 Стабильность: {status['emotional_profile'].get('stability', 'N/A')}")
    click.echo(f"🎭 Доминирующая эмоция: {status['emotional_profile'].get('dominant', 'neutral')}")
    click.echo(f"📚 В истории: {status['history_length']} событий")
    click.echo(f"🧠 В памяти: {status['memory_size']} контекстов")

@affect.command()
@click.argument('anchor')
@click.option('--count', '-c', default=10, help='Количество случайных опытов')
def simulate(anchor, count):
    """Симулирует серию случайных опытов"""
    scm = AffectiveSCM(anchor)
    
    types = ['praise', 'insult', 'loss', 'threat', 'novelty', 'neutral']
    
    click.echo(f"\n🎲 Симуляция {count} случайных опытов...")
    
    for i in range(count):
        exp_type = random.choice(types)
        intensity = random.uniform(0.2, 1.0)
        
        scm.process_interaction({
            'type': exp_type,
            'intensity': intensity,
            'context': {'simulation': i}
        })
        
        if (i + 1) % 10 == 0:
            click.echo(f"   Обработано {i + 1} опытов...")
    
    status = scm.get_emotional_status()
    click.echo(f"\n✅ Симуляция завершена!")
    click.echo(f"😊 Финальное настроение: {status['current_mood']['mood']}")
    click.echo(f"🎭 Доминирующая эмоция: {status['emotional_profile'].get('dominant', 'neutral')}")
    click.echo(f"📊 Стабильность: {status['emotional_profile'].get('stability', 'N/A')}")
