"""
Test script for the new RAG/LLM system.
Run this to verify the setup works correctly.

Usage:
    docker compose exec web python -m apps.ai_assistant.test_rag_system
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


def test_document_loaders():
    """Test that document loaders can read from database"""
    print("\n" + "="*60)
    print("TEST 1: Document Loaders")
    print("="*60)

    from apps.ai_assistant.services.document_loaders import MasterDocumentLoader

    try:
        documents = MasterDocumentLoader.load_all()
        print(f"✓ Successfully loaded {len(documents)} documents from database")

        # Show sample documents
        if documents:
            print(f"\nSample document:")
            print(f"Type: {documents[0].metadata.get('type')}")
            print(f"Text preview: {documents[0].text[:200]}...")

        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_index_service():
    """Test that index service can build and query"""
    print("\n" + "="*60)
    print("TEST 2: Index Service")
    print("="*60)

    from apps.ai_assistant.services.index_service import IndexService

    try:
        index_service = IndexService()
        print("Building index (this may take a minute)...")

        index_service.build_index()
        print("✓ Index built successfully")

        # Test query
        results = index_service.query("mountain bike", top_k=3)
        print(f"✓ Query returned {len(results['documents'])} results")

        if results['documents']:
            print(f"\nTop result:")
            print(f"Score: {results['documents'][0]['score']:.3f}")
            print(f"Text: {results['documents'][0]['text'][:150]}...")

        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_langchain_tools():
    """Test that LangChain tools work"""
    print("\n" + "="*60)
    print("TEST 3: LangChain Tools")
    print("="*60)

    from apps.ai_assistant.services.langchain_tools import get_all_tools

    try:
        tools = get_all_tools()
        print(f"✓ Loaded {len(tools)} LangChain tools")

        for tool in tools:
            print(f"  - {tool.name}: {tool.description[:80]}...")

        # Test a tool
        search_tool = tools[0]  # SearchProductsTool
        print(f"\nTesting {search_tool.name}...")
        result = search_tool._run("bike", None)
        print(f"✓ Tool executed successfully")
        print(f"Result preview: {result[:200]}...")

        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_service():
    """Test that agent service can generate responses"""
    print("\n" + "="*60)
    print("TEST 4: Agent Service")
    print("="*60)

    from apps.ai_assistant.services.agent_service import AgentService

    try:
        agent = AgentService()
        print("✓ Agent initialized successfully")

        # Test simple query
        print("\nTesting agent with query: 'What categories do you have?'")
        response = agent.generate_response("What categories do you have?")

        print(f"✓ Agent responded")
        print(f"Content: {response['content'][:300]}...")
        print(f"Tools used: {response['metadata'].get('tools_used', [])}")

        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_rag_service():
    """Test the RAG service"""
    print("\n" + "="*60)
    print("TEST 5: RAG Service")
    print("="*60)

    from apps.ai_assistant.services.rag_service_new import RAGService

    try:
        rag = RAGService()
        print("✓ RAG service initialized")

        # Test context retrieval
        context = rag.retrieve_context_for_query("I need a mountain bike")
        print(f"✓ Retrieved context for query")
        print(f"Intent: {context['intent']}")
        print(f"Products found: {len(context['products'])}")
        print(f"Summary: {context['context_summary']}")

        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("RAG/LLM SYSTEM TEST SUITE")
    print("="*60)

    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  WARNING: OPENAI_API_KEY not set!")
        print("Set it in your environment to test LLM features")

    tests = [
        ("Document Loaders", test_document_loaders),
        ("Index Service", test_index_service),
        ("LangChain Tools", test_langchain_tools),
        ("Agent Service", test_agent_service),
        ("RAG Service", test_rag_service),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n✗ {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n🎉 All tests passed! System is ready to use.")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")


if __name__ == "__main__":
    main()
