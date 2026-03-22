#!/usr/bin/env python3
"""Test script for Lark webhook notifications."""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed")

from core.alert_manager import get_alert_manager


async def test_lark_alerts():
    """Test Lark alert functionality."""
    print("Testing Lark webhook alerts...")

    alert_manager = get_alert_manager()

    if not alert_manager.lark_enabled:
        print("❌ Lark webhook not configured!")
        print("Please set LARK_WEBHOOK_URL in your .env file")
        return False

    print(f"✅ Lark webhook configured")

    # Test info alert
    print("\n📤 Sending INFO alert...")
    await alert_manager.send_info_alert(
        title="Test Info Alert",
        message="This is a test info message from the arbitrage bot",
        details={"timestamp": "2026-03-23", "status": "testing"}
    )

    # Test warning alert
    print("📤 Sending WARNING alert...")
    await alert_manager.send_warning_alert(
        title="Test Warning Alert",
        message="This is a test warning message",
        details={"reason": "testing", "severity": "medium"}
    )

    # Test critical alert
    print("📤 Sending CRITICAL alert...")
    await alert_manager.send_critical_alert(
        title="Test Critical Alert",
        message="This is a test critical message",
        details={"action": "testing", "impact": "none"}
    )

    print("\n✅ All test alerts sent!")
    print("Check your Lark channel to verify they were received.")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_lark_alerts())
    sys.exit(0 if success else 1)
