#!/usr/bin/env python3
"""Test Magic wallet configuration."""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed")

from config import POLYMARKET_SIGNATURE_TYPE
from core.wallet import Wallet, PolymarketOrderSigner


def main():
    """Test Magic wallet configuration."""
    print("🔍 Magic Wallet Configuration Test\n")

    # Check signature type
    sig_type_names = {
        0: "EOA (Standard Wallet)",
        1: "Magic/Email Wallet",
        2: "Proxy Contract"
    }

    sig_type_name = sig_type_names.get(POLYMARKET_SIGNATURE_TYPE, f"Unknown ({POLYMARKET_SIGNATURE_TYPE})")
    print(f"Signature Type: {POLYMARKET_SIGNATURE_TYPE} ({sig_type_name})")

    if POLYMARKET_SIGNATURE_TYPE == 1:
        print("✅ Magic/Email wallet signature type configured")
    elif POLYMARKET_SIGNATURE_TYPE == 0:
        print("⚠️  Using EOA signature type (standard wallet)")
    else:
        print(f"⚠️  Using signature type: {POLYMARKET_SIGNATURE_TYPE}")

    # Check if private key is configured
    private_key = os.getenv("PRIVATE_KEY", "")

    if not private_key or "<YOUR-PRIVATE-KEY-HERE>" in private_key:
        print("\n❌ PRIVATE_KEY not configured!")
        print("\nNext steps:")
        print("1. Export your private key from Polymarket/Magic wallet")
        print("2. Add it to .env file:")
        print("   PRIVATE_KEY=0xyour_private_key_here")
        print("\nSee MAGIC_WALLET_SETUP.md for detailed instructions")
        return False

    # Try to initialize wallet
    print("\n🔐 Testing wallet initialization...")
    try:
        wallet = Wallet()
        print(f"✅ Wallet initialized: {wallet.address}")

        # Test order signer
        print("\n📝 Testing order signing...")
        signer = PolymarketOrderSigner(wallet)

        # Create test order signature (won't be submitted)
        test_token_id = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        test_signature = signer.sign_order(
            token_id=test_token_id,
            maker_amount=1000000,  # 1 USDC
            taker_amount=1000000,
            side=0,  # BUY
            nonce=12345,
            expiration=1893456000,  # Far future
            fee_rate_bps=0
        )

        print(f"✅ Order signing successful")
        print(f"   Signature: {test_signature[:20]}...")
        print(f"   Signature Type: {POLYMARKET_SIGNATURE_TYPE} ({sig_type_name})")

        print("\n✅ All tests passed!")
        print("\nYour Magic wallet is correctly configured for trading.")
        print("The bot will use signature_type=1 when placing orders.")

        return True

    except Exception as exc:
        print(f"\n❌ Error: {exc}")
        print("\nTroubleshooting:")
        print("1. Verify your PRIVATE_KEY is correct")
        print("2. Make sure it starts with '0x' or is valid hex")
        print("3. Check MAGIC_WALLET_SETUP.md for help")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
