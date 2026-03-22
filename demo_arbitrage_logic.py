#!/usr/bin/env python3
"""
Демонстрация логики работы арбитражного бота:
1. Сопоставление событий (fuzzy matching)
2. Валидация через Perplexity API
3. Расчет входа в сделку на основе глубины стакана
"""

import asyncio
from datetime import datetime
from dataclasses import dataclass

from config import SLIP_BY_DEPTH
from core.matcher import match, _normalize, _extract_teams, score_event_match
from core.processor import process_depth


@dataclass
class MockEvent:
    """Моковое событие 用于 демонстрации"""

    title: str
    t_start: datetime
    platform: str


def print_header(text: str):
    """Красивый заголовок"""
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print(f"{'=' * 70}")


def demonstrate_fuzzy_matching():
    """Демонстрация fuzzy matching 用于 сопоставления событий"""
    print_header("1. СОПОСТАВЛЕНИЕ СОБЫТИЙ (FUZZY MATCHING)")

    # Создаем моковые события
    polymarket_events = [
        MockEvent(
            "Boston Celtics @ LA Lakers",
            datetime(2024, 12, 25),
            "Polymarket",
        ),
        MockEvent(
            "Will Trump win 2024 election?",
            datetime(2024, 11, 5),
            "Polymarket",
        ),
        MockEvent(
            "Bitcoin above $100k by EOY",
            datetime(2024, 12, 31),
            "Polymarket",
        ),
    ]

    sx_events = [
        MockEvent(
            "Boston Celtics at Los Angeles Lakers",  # Slightly different format
            datetime(2024, 12, 25),
            "SX",
        ),
        MockEvent(
            "Trump Presidential Victory 2024",  # Different wording
            datetime(2024, 11, 5),
            "SX",
        ),
        MockEvent(
            "BTC reaches $100,000 in 2024",  # Different wording
            datetime(2024, 12, 31),
            "SX",
        ),
    ]

    print("\n📋 События на Polymarket:")
    for i, event in enumerate(polymarket_events, 1):
        print(f"  {i}. {event.title} ({event.t_start.date()})")

    print("\n📋 События на SX:")
    for i, event in enumerate(sx_events, 1):
        print(f"  {i}. {event.title} ({event.t_start.date()})")

    # Используем matcher 用于 сопоставления
    print("\n🔍 Процесс сопоставления:")
    print("  Минимальный порог сходства: 87%")
    print("  Нормализация: lowercase, 'at' -> '@', убираем '-'")
    print("  Алгоритм: rapidfuzz token_set_ratio")

    pairs = match(polymarket_events, sx_events, min_score=87)

    print(f"\n✅ Найдено пар: {len(pairs)}")
    for pm, sx in pairs:
        print("\n  ➜ Совпадение:")
        print(f"     Polymarket: {pm.title}")
        print(f"     Нормализованно: {_normalize(pm.title)}")
        print(f"     SX: {sx.title}")
        print(f"     Нормализованно: {_normalize(sx.title)}")
        score = score_event_match(pm, sx)
        print(f"     Match confidence: {score.confidence:.2f} ({score.category})")

        # Показываем извлеченные команды 用于 спортивных событий
        if "@" in pm.title or "@" in sx.title:
            pm_teams = _extract_teams(pm.title)
            sx_teams = _extract_teams(sx.title)
            print(f"     Команды PM: {pm_teams}")
            print(f"     Команды SX: {sx_teams}")

    return pairs


async def demonstrate_event_validation():
    """Демонстрация валидации событий через Perplexity API"""
    print_header("2. ВАЛИДАЦИЯ СОБЫТИЙ (PERPLEXITY API SONAR REASONING)")

    print("""
📝 Perplexity Sonar Reasoning API используется 用于 глубокой проверки:
   - Проверяет, относятся ли события к одному реальному событию
   - Анализирует критерии разрешения
   - Chain-of-Thought рассуждение 用于 выявления различий
   - Возвращает уровень уверенности (high/medium/low)
   - Предупреждает о потенциальных неоднозначностях

🔧 Параметры API:
   - Модель: sonar-reasoning
   - reasoning_effort: high (максимальная 深度 анализа)
   - Timeout: 30 секунд

📊 Примеры результатов:
""")

    # Пример 1: Одинаковые события
    print("\n  Пример 1: ОДИНАКОВЫЕ СОБЫТИЯ")
    print("  " + "-" * 60)
    print("  Event 1 (Polymarket):")
    print("    'Will Trump win the 2024 election?'")
    print("    'Resolves YES if Trump wins general election'")
    print("  Event 2 (Kalshi):")
    print("    'Trump 2024 Presidential Victory'")
    print("    'YES if Trump elected president in 2024'")
    print("\n  ✅ 结果:")
    print("    VERDICT: SAME")
    print("    CONFIDENCE: HIGH")
    print("    REASONING: Both refer to 2024 US Presidential Election")
    print("    WARNING: NONE")

    # Пример 2: Разные события
    print("\n  Пример 2: РАЗНЫЕ СОБЫТИЯ")
    print("  " + "-" * 60)
    print("  Event 1 (Polymarket):")
    print("    'Will Trump win the 2024 election?'")
    print("    'Resolves YES if Trump wins general election'")
    print("  Event 2 (Kalshi):")
    print("    'Will Trump win the Republican nomination?'")
    print("    'Resolves YES if Trump wins nomination'")
    print("\n  ❌ 结果:")
    print("    VERDICT: DIFFERENT")
    print("    CONFIDENCE: HIGH")
    print("    REASONING: Different events - election vs nomination")
    print("    WARNING: Resolve at different times and conditions")

    # Пример 3: Средняя уверенность
    print("\n  Пример 3: СРЕДНЯЯ УВЕРЕННОСТЬ")
    print("  " + "-" * 60)
    print("  Event 1 (Polymarket):")
    print("    'Bitcoin above $100k by EOY'")
    print("    'BTC price >= $100,000 on Dec 31'")
    print("  Event 2 (Kalshi):")
    print("    'BTC hits $100k this year'")
    print("    'Bitcoin reaches $100k in 2024'")
    print("\n  ⚠️  结果:")
    print("    VERDICT: SAME")
    print("    CONFIDENCE: MEDIUM")
    print("    REASONING: Same event but wording differs")
    print("    WARNING: Resolution criteria should be verified manually")

    print("""
💡 Когда использовать валидацию:
   - ✅ При автоматическом сопоставлении новых рынков
   - ✅ Когда fuzzy matching дает низкий score (87-92%)
   - ✅ Для критических сделок 使用 большими объемами
   - ❌ Не нужна 用于 идентичных названий (100% match)
""")


async def demonstrate_depth_calculation():
    """Демонстрация расчета входа в сделку на основе глубины стакана"""
    print_header("3. РАСЧЕТ ВХОДА В СДЕЛКУ (DEPTH-BASED SLIPPAGE)")

    print(f"""
📊 Конфигурация проскальзывания (SLIP_BY_DEPTH):
   {SLIP_BY_DEPTH}

🔍 Логика расчета:
   1. Получаем глубину стакана на обеих биржах
   2. Берем МИНИМАЛЬНУЮ глубину (лимитирующий фактор)
   3. На основе глубины определяем максимальное 滑点
   4. Чем больше 深度 → тем меньше 滑点

⚙️  Примеры расчета:
""")

    test_cases = [
        {
            "name": "Высокая ликвидность",
            "pm_depth": 15000.0,
            "sx_depth": 12000.0,
            "description": "Оба рынка имеют хорошую ликвидность",
        },
        {
            "name": "Средняя ликвидность",
            "pm_depth": 8000.0,
            "sx_depth": 600.0,
            "description": "SX имеет низкую ликвидность (лимитирует)",
        },
        {
            "name": "Низкая ликвидность",
            "pm_depth": 300.0,
            "sx_depth": 250.0,
            "description": "Оба рынка имеют низкую ликвидность",
        },
        {
            "name": "Граничный случай",
            "pm_depth": 1000.0,
            "sx_depth": 1001.0,
            "description": "Ровно на пороге 1000 USDC",
        },
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n  Пример {i}: {case['name']}")
        print(f"  {'-' * 60}")
        print(f"  📍 {case['description']}")
        print(f"  📊 深度 Polymarket: ${case['pm_depth']:.2f}")
        print(f"  📊 深度 SX: ${case['sx_depth']:.2f}")

        max_slip = await process_depth(case["pm_depth"], case["sx_depth"])

        limiting_depth = min(case["pm_depth"], case["sx_depth"])
        print(f"  🔒 Лимитирующая 深度: ${limiting_depth:.2f}")
        print(f"  💹 Максимальное 滑点: {max_slip * 100:.2f}%")

        # Объясняем решение
        for threshold, slip in sorted(SLIP_BY_DEPTH.items(), reverse=True):
            if limiting_depth >= threshold:
                print(f"  ✓ 深度 >= ${threshold} → 滑点 {slip * 100:.2f}%")
                break

    print("""
💡 Практическое применение:
   - Если max_slip = 0.1% 和 价差 между биржами 0.5%
     → Можно входить в сделку 使用 прибылью ~0.4%
   - Если max_slip = 0.2% 和 价差 между биржами 0.15%
     → Не входим в сделку (убыток -0.05%)
   - 滑点 учитывает: execution costs, price impact, fees
""")


async def demonstrate_full_workflow():
    """Демонстрация полного рабочего процесса"""
    print_header("4. ПОЛНЫЙ РАБОЧИЙ ПРОЦЕСС")

    print("""
🔄 Этапы работы арбитражного бота:

1️⃣  ОБНАРУЖЕНИЕ СОБЫТИЙ
   - Получаем список активных рынков 使用 Polymarket, SX, Kalshi
   - Фильтруем по объему, ликвидности, времени до разрешения

2️⃣  СОПОСТАВЛЕНИЕ (MATCHING)
   - Нормализуем названия событий
   - Используем fuzzy matching (rapidfuzz)
   - Порог совпадения: 87%
   - Учитываем дату события

3️⃣  ВАЛИДАЦИЯ (опционально)
   - Для новых пар 或 низкого score
   - Perplexity Sonar Reasoning API
   - Chain-of-Thought 分析
   - 检查 критериев разрешения

4️⃣  АНАЛИЗ ГЛУБИНЫ СТАКАНА
   - Получаем orderbook 使用 обеих бирж
   - Рассчитываем общую глубину (сумма bids + asks)
   - Определяем лимитирующий фактор (min depth)

5️⃣  РАСЧЕТ ПРОСКАЛЬЗЫВАНИЯ
   - На основе глубины выбираем max_slip
   - Depth >= 1000: 0.1% slippage
   - Depth >= 500: 0.15% slippage
   - Depth < 500: 0.2% slippage

6️⃣  ПРИНЯТИЕ РЕШЕНИЯ
   - Рассчитываем 价差 между биржами
   - Если 价差 > (max_slip + fees) → ВХОД В СДЕЛКУ
   - Если 价差 < (max_slip + fees) → ПРОПУСК

7️⃣  ИСПОЛНЕНИЕ (不 реализовано в коде)
   - Размещение ордеров на обеих биржах
   - Мониторинг исполнения
   - Управление рисками

8️⃣  МОНИТОРИНГ
   - Prometheus метрики (g_edge, g_trades)
   - Telegram уведомления
   - Логирование всех операций
""")


async def main():
    """Главная 函数"""
    print("\n")
    print("=" * 70)
    print("  🤖 ДЕМОНСТРАЦИЯ ЛОГИКИ АРБИТРАЖНОГО БОТА")
    print("=" * 70)
    print("""
Этот 脚本 демонстрирует ключевые компоненты логики бота:
  • Сопоставление событий (fuzzy matching)
  • Валидация через Perplexity API
  • Расчет входа в сделку на основе глубины стакана
""")

    # 1. Fuzzy matching
    demonstrate_fuzzy_matching()

    # 2. Event validation
    await demonstrate_event_validation()

    # 3. Depth calculation
    await demonstrate_depth_calculation()

    # 4. Full workflow
    await demonstrate_full_workflow()

    print("\n" + "=" * 70)
    print("  ✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 70)
    print("""
📚 Дополнительная информация:
   - core/matcher.py - логика сопоставления событий
   - core/processor.py - расчет проскальзывания
   - core/event_validator.py - валидация через Perplexity API
   - config.py - конфигурация порогов
   - README.md - полная документация
""")


if __name__ == "__main__":
    asyncio.run(main())
