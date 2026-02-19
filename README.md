# 🧠 SCM (Subjective Continuity Module)

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-6%2F6-green.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

**SCM** — это ядро онтологической памяти для систем искусственного интеллекта. 
Оно позволяет ИИ **помнить свою историю**, **учиться на ошибках** и **сохранять целостность личности**.

## 🎯 Ключевые возможности

- ✅ **Genesis Anchor** — точка рождения системы (фиксируется 1 раз в TEE)
- ✅ **RSA Accumulator** — O(1) верификация цепочки из тысяч шрамов
- ✅ **Write-Ahead Log** — атомарность и восстановление после сбоев
- ✅ **Black Stone Mode** — режим "смерти" при нарушении целостности
- ✅ **Cognitive Integrator** — влияние шрамов на выбор апостолов
- ✅ **Apostle Trust System** — динамическое доверие к языкам/стилям

## 📊 Результаты тестирования

## 📈 Рейтинг апостолов после обучения
===================================================
✅ АККУМУЛЯТОР (RSA Accumulator)
===================================================
✓ test_add_and_verify - добавление и верификация
✓ test_batch_verify - пакетная верификация
✓ test_incremental_chain - цепочка из 100 шрамов

===================================================
✅ BLACK STONE MODE
===================================================
✓ test_black_stone_activation - активация режима
✓ test_black_stone_exit - выход через rebirth
✓ test_black_stone_no_double_activation - защита от двойной активации

===================================================
✅ ИНТЕГРАЦИЯ (Cognitive Integrator)
===================================================
📊 Chain has 4 scars
✓ Цепочка валидна: True

## 📈 Рейтинг апостолов после обучения
🇩🇪 de: доверие=0.90, шрамов=0
🇦🇲 hy: доверие=0.70, шрамов=0
🇬🇧 en: доверие=0.60, шрамов=0
🇮🇳 sa: доверие=0.50, шрамов=0
🇫🇷 fr: доверие=0.50, шрамов=0
🇪🇸 es: доверие=0.50, шрамов=0
🇮🇹 it: доверие=0.50, шрамов=0
🇷🇺 ru: доверие=0.48, шрамов=1
🇨🇳 zh: доверие=0.40, шрамов=0
🇯🇵 ja: доверие=0.40, шрамов=0

> 💡 **Интересно**: русский язык получил шрам (rejection) и упал с 0.80 до 0.48, а армянский уверенно держится на 2-м месте!

## 🚀 Быстрый старт

### Установка
```bash
git clone https://github.com/arutovan-droid/SCM-Subjective-Continuity-Module-.git
cd SCM-Subjective-Continuity-Module-
pip install -r requirements.txt
Инициализация genesis
python
python scripts/init_genesis.py
Создание первого шрама
python
import asyncio
import uuid
from datetime import datetime
from core.ontological_scar import OntologicalScar
from accumulator.incremental_proof import IncrementalChainProof

async def create_scar():
    chain = IncrementalChainProof(genesis_hash=b"...", wal_path="chain.wal")
    await chain.initialize()
    
    scar = OntologicalScar(
        scar_id=uuid.uuid4(),
        genesis_ref="your_genesis_hash",
        incident_type="rejection",
        cognitive_basis="ru",
        collision_mode=False,
        pre_state_hash="genesis",
        post_state_hash="after_rejection",
        deformation_vector={"reason": "user_rejected"},
        entropy_score=0.8,
        ontological_drift=0.2,
        timestamp=datetime.utcnow(),
        operator_id="user_1"
    )
    
    proof = await chain.add_scar(scar.to_hash())
    print(f"✅ Шрам создан! Chain valid: {chain.verify_chain()}")

asyncio.run(create_scar())
🧪 Демо-API (MVP)
Запусти простой веб-сервер для тестирования:

python
# save as api_demo.py
from flask import Flask, request, jsonify
import asyncio
import hashlib
import uuid
from datetime import datetime
from core.ontological_scar import OntologicalScar
from accumulator.incremental_proof import IncrementalChainProof
from orchestrator.cognitive_integrator import CognitiveIntegrator

app = Flask(__name__)

# Глобальные объекты (в реальности - с базой данных)
chain = None
integrator = None
genesis_hash = None

def init():
    global chain, integrator, genesis_hash
    with open('GENESIS.md', 'r') as f:
        content = f.read()
        genesis_hash = content.split('GENESIS_HASH = ')[1].split('\n')[0].strip()
    
    chain = IncrementalChainProof(
        genesis_hash=hashlib.sha256(genesis_hash.encode()).digest(),
        wal_path="chain.wal"
    )
    asyncio.run(chain.initialize())
    
    integrator = CognitiveIntegrator(chain, genesis_hash)
    asyncio.run(integrator.load_scars_from_chain())

init()

@app.route('/status', methods=['GET'])
def get_status():
    """Получить статус системы и рейтинг апостолов"""
    status = integrator.get_apostle_status()
    return jsonify({
        "chain_valid": chain.verify_chain(),
        "total_scars": chain.accumulator.current_sequence,
        "apostles": status
    })

@app.route('/route', methods=['POST'])
def route_query():
    """Получить решение о маршрутизации для запроса"""
    data = request.json
    query = data.get('query', '')
    user_id = data.get('user_id', 'anonymous')
    
    decision = asyncio.run(integrator.decide_routing(query, user_id))
    
    return jsonify({
        "selected_basis": decision.selected_basis,
        "confidence": decision.confidence,
        "alternatives": decision.alternatives,
        "reasoning": decision.reasoning
    })

@app.route('/scar', methods=['POST'])
def create_scar():
    """Создать новый шрам (отказ/проблему)"""
    data = request.json
    
    scar = OntologicalScar(
        scar_id=uuid.uuid4(),
        genesis_ref=genesis_hash,
        incident_type=data.get('type', 'rejection'),
        cognitive_basis=data.get('basis', 'ru'),
        collision_mode=data.get('collision', False),
        pre_state_hash=data.get('pre_state', 'unknown'),
        post_state_hash=data.get('post_state', 'unknown'),
        deformation_vector=data.get('deformation', {}),
        entropy_score=data.get('entropy', 0.7),
        ontological_drift=data.get('drift', 0.1),
        timestamp=datetime.utcnow(),
        operator_id=data.get('operator', 'api_user')
    )
    
    async def add_scar():
        proof = await chain.add_scar(scar.to_hash())
        from dataclasses import replace
        scar_with_proof = replace(scar, chain_proof=proof, accumulator_value=chain.accumulator_value)
        integrator.apply_scar_to_apostles(scar_with_proof)
        return scar_with_proof
    
    new_scar = asyncio.run(add_scar())
    
    return jsonify({
        "scar_id": str(new_scar.scar_id),
        "basis": new_scar.cognitive_basis,
        "type": new_scar.incident_type,
        "new_trust": integrator.apostles[new_scar.cognitive_basis].current_trust
    })

@app.route('/apostles', methods=['GET'])
def get_apostles():
    """Получить детальный статус всех апостолов"""
    status = integrator.get_apostle_status()
    
    # Сортируем по доверию
    sorted_apostles = sorted(
        [{"basis": k, **v} for k, v in status.items()],
        key=lambda x: x["trust"],
        reverse=True
    )
    
    return jsonify({
        "apostles": sorted_apostles,
        "total_scars": chain.accumulator.current_sequence,
        "chain_valid": chain.verify_chain()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
📦 Установка демо-API
bash
# Установи зависимости
pip install flask

# Запусти сервер
python api_demo.py
Тестирование API
bash
# Получить статус
curl http://localhost:5000/status

# Получить решение для запроса
curl -X POST http://localhost:5000/route \
  -H "Content-Type: application/json" \
  -d '{"query": "Почему это работает?", "user_id": "test"}'

# Создать шрам
curl -X POST http://localhost:5000/scar \
  -H "Content-Type: application/json" \
  -d '{"type": "rejection", "basis": "ru", "entropy": 0.8}'

# Получить рейтинг апостолов
curl http://localhost:5000/apostles
🔬 Примеры запросов
До шрама (русский еще с высоким доверием)
bash
curl -X POST http://localhost:5000/route -H "Content-Type: application/json" -d '{"query": "Почему небо голубое?"}'
# → { "selected_basis": "ru", "confidence": 0.8 }
После шрама
bash
curl -X POST http://localhost:5000/scar -H "Content-Type: application/json" -d '{"type": "rejection", "basis": "ru"}'
curl -X POST http://localhost:5000/route -H "Content-Type: application/json" -d '{"query": "Почему небо голубое?"}'
# → { "selected_basis": "de", "confidence": 0.9 }
🏗 Архитектура
text
┌─────────────────────────────────────────────────────┐
│                    SCM Core                          │
├─────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐                 │
│  │   Genesis   │    │    RSA      │                 │
│  │   Anchor    │◄──►│ Accumulator │                 │
│  └─────────────┘    └─────────────┘                 │
│         │                  │                         │
│         ▼                  ▼                         │
│  ┌─────────────┐    ┌─────────────┐                 │
│  │  Ontological│    │   Write-    │                 │
│  │    Scars    │◄──►│  Ahead Log  │                 │
│  └─────────────┘    └─────────────┘                 │
│         │                  │                         │
│         ▼                  ▼                         │
│  ┌─────────────────────────────────────┐           │
│  │      Cognitive Integrator            │           │
│  │  ┌─────────────────────────────┐    │           │
│  │  │  Apostle Trust System       │    │           │
│  │  │  • de: 0.90  • hy: 0.70    │    │           │
│  │  │  • en: 0.60  • ru: 0.48    │    │           │
│  │  └─────────────────────────────┘    │           │
│  └─────────────────────────────────────┘           │
└─────────────────────────────────────────────────────┘
📄 Лицензия
MIT © 2026 arutovan-droid

🤝 Как помочь проекту
⭐ Поставь звезду на GitHub

🐛 Сообщай о багах

💡 Предлагай идеи

🔧 Делай пул-реквесты

Создано с ❤️ для армянского ИИ 🇦🇲
