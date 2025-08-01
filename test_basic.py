#!/usr/bin/env python3
"""
Basic test script to verify the project setup
"""

def test_imports():
    """Test that all modules can be imported"""
    try:
        from config import LLMConfig, DialogueConfig, DEFAULT_LLMS
        from llm_providers import BaseLLMProvider, OpenAIProvider, AnthropicProvider, GroqProvider, create_llm_provider
        from dialogue_manager import DialogueManager
        return True
    except ImportError as e:
        print(f"Import error: {e}")
        return False

def test_config():
    """Test configuration functionality"""
    try:
        from config import LLMConfig, DialogueConfig
        config = LLMConfig(
            name="Test Model",
            model="test-model",
            api_key="test-key"
        )
        assert config.name == "Test Model"
        dconfig = DialogueConfig(rounds=5)
        assert dconfig.rounds == 5
        return True
    except Exception as e:
        print(f"Config test error: {e}")
        return False

def test_available_llms():
    """Test that default LLMs are configured"""
    try:
        from config import DEFAULT_LLMS
        expected_models = ["kimi-k2", "llama-3.3-70b", "qwen3-32b", "gpt-4o", "claude-3.5-sonnet"]
        for model in expected_models:
            assert model in DEFAULT_LLMS, f"Missing model: {model}"
        return True
    except Exception as e:
        print(f"LLM configuration test error: {e}")
        return False

def main():
    """Run all tests"""
    print("Running basic tests...")
    print("=" * 40)
    tests = [
        test_imports,
        test_config,
        test_available_llms
    ]
    passed = 0
    total = len(tests)
    for test in tests:
        if test():
            passed += 1
    print("=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    if passed == total:
        print("All tests passed! The project is ready to use.")
        print("Next steps:")
        print("1. Set up your API keys (see README.md)")
        print("2. Run: python main.py start --interactive")
    else:
        print("Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main() 