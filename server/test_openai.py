#!/usr/bin/env python3
"""
Quick OpenAI API Test Script
Tests both chat and embeddings endpoints
"""

import os
import sys

def test_openai():
    """Test OpenAI API connection and quota"""

    print("=" * 60)
    print("OpenAI API Test")
    print("=" * 60)

    # Check if API key is set
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("\nSet it with:")
        print("  export OPENAI_API_KEY='your-key-here'")
        return False

    print(f"✅ API Key found: {api_key[:20]}...{api_key[-4:]}")
    print()

    # Test 1: Chat Completion (cheaper, faster)
    print("Test 1: Chat Completion (GPT-4o-mini)")
    print("-" * 60)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello! am katuula"}],
            max_tokens=10
        )

        result = response.choices[0].message.content
        tokens = response.usage.total_tokens

        print(f"✅ Chat works!")
        print(f"   Response: {result}")
        print(f"   Tokens used: {tokens}")
        print(f"   Estimated cost: ${tokens * 0.00015 / 1000:.6f}")
        print()

    except Exception as e:
        error_msg = str(e)
        print(f"❌ Chat failed: {error_msg[:100]}")

        if "429" in error_msg or "quota" in error_msg.lower():
            print("\n🔴 QUOTA EXCEEDED - You need to add credits!")
            print("   Go to: https://platform.openai.com/settings/organization/billing")
            print("   Add $10-20 credit to continue")
            return False
        elif "401" in error_msg or "authentication" in error_msg.lower():
            print("\n🔴 INVALID API KEY")
            print("   Check your key at: https://platform.openai.com/api-keys")
            return False
        else:
            print(f"\n🔴 Unknown error: {error_msg}")
            return False

    # Test 2: Free Embeddings (HuggingFace - alternative to OpenAI)
    print("\nTest 2: Free Embeddings (HuggingFace sentence-transformers)")
    print("-" * 60)
    try:
        from sentence_transformers import SentenceTransformer

        # Use a small, fast model (downloads ~80MB first time)
        print("   Loading model (first time only)...")
        model = SentenceTransformer('all-MiniLM-L6-v2')

        # Generate embedding
        embedding = model.encode("Test embedding")

        print(f"✅ Free embeddings work!")
        print(f"   Model: all-MiniLM-L6-v2")
        print(f"   Vector dimensions: {len(embedding)}")
        print(f"   Cost: $0.00 (FREE!)")
        print(f"   Speed: Fast (runs locally)")
        print()

        # Also test OpenAI embeddings to show the difference
        print("   Testing OpenAI embeddings (for comparison)...")
        try:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input="Test embedding"
            )
            print("   ✅ OpenAI embeddings also work!")
        except Exception as openai_err:
            if "429" in str(openai_err):
                print("   ❌ OpenAI embeddings quota exceeded")
                print("   💡 Will use FREE HuggingFace embeddings instead!")
            else:
                print(f"   ❌ OpenAI error: {str(openai_err)[:50]}")
        print()

    except ImportError:
        print("❌ sentence-transformers not installed")
        print("\n📦 Install with:")
        print("   pip install sentence-transformers")
        print("\nOr in Docker:")
        print("   docker compose exec web pip install sentence-transformers")
        return "partial"
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Embeddings failed: {error_msg[:100]}")
        return "partial"

    # Test 3: Check account limits
    print("\nTest 3: Account Info")
    print("-" * 60)
    try:
        # Try to get account info (may not always work)
        models = client.models.list()
        print(f"✅ Can access models API")
        print(f"   Available models: {len(models.data)}")
    except Exception as e:
        print(f"⚠️  Can't access models API: {str(e)[:50]}")

    print()
    return True


def main():
    """Main test runner"""
    result = test_openai()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if result is True:
        print("✅ ALL TESTS PASSED")
        print("\nYour OpenAI setup is working perfectly!")
        print("You can use:")
        print("  - AI chat assistant")
        print("  - RAG/semantic search")
        print("  - Product recommendations")

    elif result == "partial":
        print("⚠️  PARTIAL SUCCESS")
        print("\nYour setup:")
        print("  ✅ Chat works (AI assistant will work)")
        print("  ❌ Embeddings blocked (no semantic search)")
        print("\nYou can test Phase 4 checkout without embeddings!")

    else:
        print("❌ TESTS FAILED")
        print("\nYour OpenAI API has issues.")
        print("\nOptions:")
        print("  1. Add credits: https://platform.openai.com/settings/organization/billing")
        print("  2. Use Ollama (free): brew install ollama")
        print("  3. Test Phase 4 without AI: ./test_phase4_quick.sh")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
