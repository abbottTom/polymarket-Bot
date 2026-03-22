#!/usr/bin/env python3
"""
查找交易所活跃市场的脚本。

此脚本帮助找到可用于机器人的真实 market IDs：
1. 从每个交易所获取热门市场列表
2. 检查它们的流动性
3. 输出流动性最高的前 N 个市场

用法：
    python scripts/find_markets.py [--limit 10]
"""

import asyncio
import logging
import os
import sys
import argparse
from pathlib import Path
from aiohttp import ClientSession
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Ensure aiohttp works with aiodns on Windows
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from core.logging_config import setup_logging


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


async def find_polymarket_markets(session: ClientSession, limit: int = 10) -> List[Dict]:
    """
    查找 Polymarket 上的热门市场。

    API Documentation: https://docs.polymarket.com/
    """
    print(f"\n{Colors.BOLD}Searching Polymarket markets...{Colors.END}")

    try:
        # Polymarket API 端点用于获取热门市场
        url = "https://gamma-api.polymarket.com/markets"
        params = {
            'limit': limit * 2,  # Get more, filter later
            'active': 'true',
            'closed': 'false',
        }

        async with session.get(url, params=params, timeout=30) as resp:
            if resp.status != 200:
                print(f"  {Colors.RED}✗ Error: HTTP {resp.status}{Colors.END}")
                return []

            data = await resp.json()

            markets = []
            def _normalize_outcome(value):
                if value is None:
                    return None
                normalized = str(value).strip().lower()
                return normalized if normalized in {"yes", "no"} else None

            for market in data[:limit]:
                token_ids = {}
                clob_token_ids = market.get("clobTokenIds") or []
                outcomes = market.get("outcomes") or []

                if isinstance(clob_token_ids, str):
                    try:
                        import json

                        clob_token_ids = json.loads(clob_token_ids)
                    except json.JSONDecodeError:
                        clob_token_ids = []

                if clob_token_ids and outcomes and len(clob_token_ids) == len(outcomes):
                    for i, outcome in enumerate(outcomes):
                        key = _normalize_outcome(outcome)
                        if key:
                            token_ids[key] = clob_token_ids[i]

                tokens = market.get("tokens") or []
                for token in tokens:
                    key = _normalize_outcome(token.get("outcome", ""))
                    if not key:
                        continue
                    token_id = token.get("token_id") or token.get("id")
                    if token_id:
                        token_ids.setdefault(key, token_id)

                yes_token_id = token_ids.get("yes")
                no_token_id = token_ids.get("no")

                # Extract relevant info
                market_info = {
                    'id': market.get('condition_id') or market.get('id'),
                    'yes_token_id': yes_token_id,
                    'no_token_id': no_token_id,
                    'question': market.get('question', 'Unknown'),
                    'volume': float(market.get('volume', 0)),
                    'liquidity': float(market.get('liquidity', 0)),
                    'end_date': market.get('end_date_iso'),
                }
                markets.append(market_info)

            # Sort by liquidity
            markets.sort(key=lambda x: x['liquidity'], reverse=True)

            print(f"  {Colors.GREEN}✓ Found {len(markets)} active markets{Colors.END}\n")

            # Display top markets
            print(f"{Colors.BOLD}Top Polymarket markets by liquidity:{Colors.END}")
            for i, m in enumerate(markets[:limit], 1):
                print(f"\n  {i}. {Colors.YELLOW}{m['question'][:70]}...{Colors.END}")
                print(f"     Condition ID: {Colors.BLUE}{m['id']}{Colors.END}")
                yes_label = m.get("yes_token_id") or "N/A"
                no_label = m.get("no_token_id") or "N/A"
                print(f"     Token ID (YES): {Colors.BLUE}{yes_label}{Colors.END}")
                print(f"     Token ID (NO):  {Colors.BLUE}{no_label}{Colors.END}")
                print(f"     Liquidity: ${m['liquidity']:,.2f}")
                print(f"     Volume: ${m['volume']:,.2f}")
                if m['end_date']:
                    print(f"     End: {m['end_date']}")

            return markets

    except Exception as exc:
        print(f"  {Colors.RED}✗ Error: {exc}{Colors.END}")
        logging.error("Failed to fetch Polymarket markets", exc_info=True)
        return []


async def find_sx_markets(session: ClientSession, limit: int = 10) -> List[Dict]:
    """
    查找 SX 上的热门市场。

    ⚠️ 警告：SX 市场发现功能有限/实验性。
    下面的 API 解析是占位符，可能无法正常工作。

    推荐：在 https://sx.bet 手动查找 SX market IDs
    然后验证：python scripts/check_sx_connector.py <market_id>
    """
    print(f"\n{Colors.BOLD}Searching SX markets...{Colors.END}")
    print(f"{Colors.YELLOW}⚠ WARNING: SX integration is experimental{Colors.END}")
    print(f"{Colors.YELLOW}  Recommended to find market IDs manually at https://sx.bet{Colors.END}")

    try:
        # SX API - 需要检查实际端点
        # 这是示例，可能需要调整
        url = "https://api.sx.bet/markets"
        params = {
            'limit': limit,
            'status': 'active',
        }

        async with session.get(url, params=params, timeout=30) as resp:
            if resp.status != 200:
                print(f"  {Colors.YELLOW}⚠ SX API returned {resp.status}{Colors.END}")
                print(f"  {Colors.YELLOW}Note: You may need to find SX markets manually{Colors.END}")
                print(f"  {Colors.YELLOW}Visit: https://sx.bet to browse active markets{Colors.END}")
                return []

            data = await resp.json()

            markets = []
            # Parse SX market data (format may vary)
            # This is a placeholder - adjust based on actual API response

            return markets

    except Exception as exc:
        print(f"  {Colors.YELLOW}⚠ Could not fetch SX markets: {exc}{Colors.END}")
        print(f"  {Colors.YELLOW}Visit https://sx.bet to find markets manually{Colors.END}")
        return []


async def find_kalshi_markets(session: ClientSession, limit: int = 10) -> List[Dict]:
    """
    查找 Kalshi 上的热门市场。

    API Documentation: https://trading-api.readme.io/reference/getmarkets
    """
    print(f"\n{Colors.BOLD}Searching Kalshi markets...{Colors.END}")

    try:
        url = "https://trading-api.kalshi.com/trade-api/v2/markets"
        params = {
            'limit': limit,
            'status': 'open',
        }
        headers = {}
        kalshi_key = os.getenv("KALSHI_API_KEY")
        if kalshi_key:
            headers["Authorization"] = f"Bearer {kalshi_key}"

        async with session.get(url, params=params, headers=headers, timeout=30) as resp:
            if resp.status != 200:
                print(f"  {Colors.YELLOW}⚠ Kalshi API returned {resp.status}{Colors.END}")
                if resp.status == 401:
                    print(
                        f"  {Colors.YELLOW}Set KALSHI_API_KEY to access market listings{Colors.END}"
                    )
                print(f"  {Colors.YELLOW}Visit: https://kalshi.com to browse active markets{Colors.END}")
                return []

            data = await resp.json()
            markets_data = data.get('markets', [])

            markets = []
            for market in markets_data[:limit]:
                market_info = {
                    'ticker': market.get('ticker'),
                    'title': market.get('title', 'Unknown'),
                    'volume': float(market.get('volume', 0)),
                    'open_interest': float(market.get('open_interest', 0)),
                }
                markets.append(market_info)

            # Sort by volume
            markets.sort(key=lambda x: x['volume'], reverse=True)

            print(f"  {Colors.GREEN}✓ Found {len(markets)} active markets{Colors.END}\n")

            # Display top markets
            print(f"{Colors.BOLD}Top Kalshi markets by volume:{Colors.END}")
            for i, m in enumerate(markets[:limit], 1):
                print(f"\n  {i}. {Colors.YELLOW}{m['title'][:70]}...{Colors.END}")
                print(f"     Ticker: {Colors.BLUE}{m['ticker']}{Colors.END}")
                print(f"     Volume: ${m['volume']:,.2f}")
                print(f"     Open Interest: ${m['open_interest']:,.2f}")

            return markets

    except Exception as exc:
        print(f"  {Colors.YELLOW}⚠ Could not fetch Kalshi markets: {exc}{Colors.END}")
        print(f"  {Colors.YELLOW}Visit https://kalshi.com to find markets manually{Colors.END}")
        return []


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Find active markets on exchanges')
    parser.add_argument(
        '--limit',
        type=int,
        default=5,
        help='Number of markets to display per exchange (default: 5)'
    )
    args = parser.parse_args()

    setup_logging(level=logging.WARNING)  # Less verbose

    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║                                                                      ║")
    print("║                  🔍 MARKET DISCOVERY TOOL                           ║")
    print("║                                                                      ║")
    print("║          Find active markets with high liquidity                    ║")
    print("║                                                                      ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")

    async with ClientSession() as session:
        # Find markets on each exchange
        polymarket_markets = await find_polymarket_markets(session, args.limit)
        sx_markets = await find_sx_markets(session, args.limit)
        kalshi_markets = await find_kalshi_markets(session, args.limit)

        # Summary
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.END}")
        print(f"{Colors.BOLD}SUMMARY{Colors.END}\n")

        print(f"Markets found:")
        print(f"  Polymarket: {Colors.GREEN}{len(polymarket_markets)}{Colors.END}")
        print(f"  SX:         {Colors.YELLOW}{len(sx_markets) if sx_markets else 'Manual lookup needed'}{Colors.END}")
        print(f"  Kalshi:     {Colors.GREEN}{len(kalshi_markets)}{Colors.END}")

        print(f"\n{Colors.BOLD}NEXT STEPS:{Colors.END}\n")
        print(f"1. Pick Polymarket token IDs and SX/Kalshi market IDs from above")
        print(f"2. Test each connector:")
        print(f"   {Colors.BLUE}python scripts/check_polymarket_connector.py <token_id>{Colors.END}")
        print(f"   {Colors.BLUE}python scripts/check_sx_connector.py <market_id>{Colors.END}")
        print(f"   {Colors.BLUE}python scripts/check_kalshi_connector.py <ticker>{Colors.END}")
        print(f"3. Update main.py with working market IDs")
        print(f"4. Run test: {Colors.BLUE}python scripts/test_run.py{Colors.END}\n")


if __name__ == '__main__':
    asyncio.run(main())
