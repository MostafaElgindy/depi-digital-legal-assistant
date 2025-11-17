#!/usr/bin/env python3
"""
Startup script to verify configuration and dependencies
"""

import os
import sys
from dotenv import load_dotenv

# Load .env from config directory
config_path = os.path.join(os.path.dirname(__file__), 'config', '.env')
load_dotenv(config_path)
def check_environment():
    """Check if environment variables are set correctly"""
    print("🔍 Configuration Check")
    print("=" * 60)
    
    # Check Google API Key
    google_key = os.getenv("GOOGLE_API_KEY", "")
    if google_key:
        print("✅ GOOGLE_API_KEY is set")
    else:
        print("❌ GOOGLE_API_KEY is NOT set")
        print("   Please set it in .env file")
        return False
    
    # Check dependencies
    print("\n" * 1 + "=" * 60)
    print("📦 Checking Dependencies")
    print("=" * 60)
    
    dependencies = [
        ("llama-index", "llama_index"),
        ("chromadb", "chromadb"),
        ("fastapi", "fastapi"),
        ("streamlit", "streamlit"),
        ("transformers", "transformers"),
        ("torch", "torch"),
    ]
    
    all_ok = True
    for package_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - NOT INSTALLED")
            all_ok = False
    
    return all_ok

if __name__ == "__main__":
    if check_environment():
        print("\n" + "=" * 60)
        print("✅ All checks passed! You can now run the application.")
        print("=" * 60)
        print("\nRun the following commands in separate terminals:")
        print("  1. uvicorn endpoint:app --reload")
        print("  2. streamlit run ui.py")
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ Some checks failed. Please fix them first.")
        print("=" * 60)
        sys.exit(1)
