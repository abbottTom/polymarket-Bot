#!/usr/bin/env python3
"""
套利机器人演示版本（使用模拟数据）
"""

import argparse
import asyncio
import logging
import random
from typing import Any, Dict, List, Tuple

from core.metrics import init_metrics
from core.processor import process_depth

# 演示用的模拟数据
MOCK_DEPTH_DATA = {
    "polymarket": {
        "bids": [
            {"price": 0.65, "size": 1000},
            {"price": 0.64, "size": 1500},
            {"price": 0.63, "size": 2000},
            {"price": 0.62, "size": 2500},
            {"price": 0.61, "size": 3000},
        ],
        "asks": [
            {"price": 0.66, "size": 800},
            {"price": 0.67, "size": 1200},
            {"price": 0.68, "size": 1800},
            {"price": 0.69, "size": 2200},
            {"price": 0.70, "size": 2800},
        ],
    },
    "sx": {
        "bids": [
            {"price": 0.655, "size": 900},
            {"price": 0.645, "size": 1400},
            {"price": 0.635, "size": 1900},
            {"price": 0.625, "size": 2400},
            {"price": 0.615, "size": 2900},
        ],
        "asks": [
            {"price": 0.665, "size": 750},
            {"price": 0.675, "size": 1150},
            {"price": 0.685, "size": 1750},
            {"price": 0.695, "size": 2150},
            {"price": 0.705, "size": 2750},
        ],
    },
}


def generate_mock_depth() -> Tuple[Dict, Dict]:
    """生成带有小幅变化的模拟订单簿深度数据"""

    # 向基础数据添加随机变化
    pm_depth: Dict[str, List[Dict[str, Any]]] = {"bids": [], "asks": []}

    sx_depth: Dict[str, List[Dict[str, Any]]] = {"bids": [], "asks": []}

    # 生成 Polymarket 数据
    for bid in MOCK_DEPTH_DATA["polymarket"]["bids"]:
        price_variation = random.uniform(-0.01, 0.01)
        size_variation = random.uniform(0.8, 1.2)

        pm_depth["bids"].append(
            {
                "price": round(bid["price"] + price_variation, 4),
                "size": int(bid["size"] * size_variation),
            }
        )

    for ask in MOCK_DEPTH_DATA["polymarket"]["asks"]:
        price_variation = random.uniform(-0.01, 0.01)
        size_variation = random.uniform(0.8, 1.2)

        pm_depth["asks"].append(
            {
                "price": round(ask["price"] + price_variation, 4),
                "size": int(ask["size"] * size_variation),
            }
        )

    # 生成 SX 数据
    for bid in MOCK_DEPTH_DATA["sx"]["bids"]:
        price_variation = random.uniform(-0.01, 0.01)
        size_variation = random.uniform(0.8, 1.2)

        sx_depth["bids"].append(
            {
                "price": round(bid["price"] + price_variation, 4),
                "size": int(bid["size"] * size_variation),
            }
        )

    for ask in MOCK_DEPTH_DATA["sx"]["asks"]:
        price_variation = random.uniform(-0.01, 0.01)
        size_variation = random.uniform(0.8, 1.2)

        sx_depth["asks"].append(
            {
                "price": round(ask["price"] + price_variation, 4),
                "size": int(ask["size"] * size_variation),
            }
        )

    return pm_depth, sx_depth


def print_depth_analysis(pm_depth: Dict, sx_depth: Dict) -> None:
    """输出订单簿深度分析"""
    print("\n📊 订单簿深度分析")
    print("=" * 50)

    # Polymarket
    print("🔵 Polymarket:")
    print("   最佳买入价格:")
    for i, bid in enumerate(pm_depth["bids"][:3]):
        print(f"     {i+1}. ${bid['price']:.4f} - {bid['size']} 个")

    print("   最佳卖出价格:")
    for i, ask in enumerate(pm_depth["asks"][:3]):
        print(f"     {i+1}. ${ask['price']:.4f} - {ask['size']} 个")

    # SX
    print("\n🟡 SX:")
    print("   最佳买入价格:")
    for i, bid in enumerate(sx_depth["bids"][:3]):
        print(f"     {i+1}. ${bid['price']:.4f} - {bid['size']} 个")

    print("   最佳卖出价格:")
    for i, ask in enumerate(sx_depth["asks"][:3]):
        print(f"     {i+1}. ${ask['price']:.4f} - {ask['size']} 个")

    # 价差
    pm_spread = pm_depth["asks"][0]["price"] - pm_depth["bids"][0]["price"]
    sx_spread = sx_depth["asks"][0]["price"] - sx_depth["bids"][0]["price"]

    print("\n📈 价差:")
    print(f"   Polymarket: {pm_spread:.4f} ({pm_spread*100:.2f}%)")
    print(f"   SX: {sx_spread:.4f} ({sx_spread*100:.2f}%)")


def calculate_total_depth(orderbook: Dict) -> float:
    """计算订单簿总深度"""
    total_bids = sum(order["size"] for order in orderbook.get("bids", []))
    total_asks = sum(order["size"] for order in orderbook.get("asks", []))
    return total_bids + total_asks


async def demo_cycle(cycle_num: int) -> None:
    """执行一个演示周期"""
    print(f"\n🔄 周期 #{cycle_num}")
    print("=" * 30)

    # 生成模拟数据
    pm_depth, sx_depth = generate_mock_depth()

    # 输出分析
    print_depth_analysis(pm_depth, sx_depth)

    # 计算每个交易所的总深度
    pm_total_depth = calculate_total_depth(pm_depth)
    sx_total_depth = calculate_total_depth(sx_depth)

    # 通过机器人主要逻辑处理数据
    print("\n⚙️ 处理数据中...")
    print(f"   Polymarket 总深度: {pm_total_depth:.0f}")
    print(f"   SX 总深度: {sx_total_depth:.0f}")
    await process_depth(pm_total_depth, sx_total_depth)

    print(f"✅ 周期 #{cycle_num} 完成")


async def main() -> None:
    """演示机器人主函数"""
    parser = argparse.ArgumentParser(description="套利机器人演示版本")
    parser.add_argument("--cycles", type=int, default=3, help="周期数量")
    parser.add_argument(
        "--interval", type=int, default=5, help="周期之间的间隔（秒）"
    )
    args = parser.parse_args()

    # 日志配置
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    init_metrics()

    print("🎭 套利机器人演示版本")
    print("=" * 50)
    print("此机器人使用模拟数据演示套利逻辑")
    print(f"周期数量: {args.cycles}")
    print(f"间隔: {args.interval} 秒")
    print()

    try:
        for cycle in range(1, args.cycles + 1):
            await demo_cycle(cycle)

            if cycle < args.cycles:
                print(f"\n⏳ 等待 {args.interval} 秒直到下一个周期...")
                await asyncio.sleep(args.interval)

        print(f"\n🎉 演示完成！已执行 {args.cycles} 个周期。")

    except KeyboardInterrupt:
        print("\n🛑 演示已被用户停止")
    except Exception as exc:
        print(f"\n❌ 演示中出错: {exc}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
