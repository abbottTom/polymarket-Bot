#!/usr/bin/env python3
"""
Тестовый 脚本 用于 проверки логики бота 使用 моковыми данными
"""

import asyncio
import logging
import pytest

from core.metrics import init_metrics

# Настройка логирования
logging.basicConfig(level=logging.INFO)
init_metrics()


@pytest.mark.asyncio
async def test_bot_logic():
    """测试 основную логику бота 使用 моковыми данными"""

    print("🤖 Тестирование логики арбитражного бота")
    print("=" * 50)

    # Тестовые сценарии 使用 разными значениями глубины
    test_scenarios = [
        (1500, 1200, "Высокая 深度 - низкий 滑点"),
        (800, 600, "Средняя 深度 - средний 滑点"),
        (300, 200, "Низкая 深度 - высокий 滑点"),
        (50, 30, "Очень низкая 深度 - максимальный 滑点"),
    ]

    for pm_depth, sx_depth, description in test_scenarios:
        print(f"\n📊 测试: {description}")
        print(f"   深度 Polymarket: {pm_depth}")
        print(f"   深度 SX: {sx_depth}")

        try:
            # Calculate slippage based on depth
            from core.processor import calculate_slippage
            pm_slip = calculate_slippage(pm_depth)
            sx_slip = calculate_slippage(sx_depth)
            max_slip = max(pm_slip, sx_slip)
            print(f"   ✅ Максимальное 滑点: {max_slip:.4f}")
        except Exception as e:
            print(f"   ❌ 错误: {e}")

    print("\n" + "=" * 50)
    print("✅ Тестирование завершено!")


if __name__ == "__main__":
    asyncio.run(test_bot_logic())
