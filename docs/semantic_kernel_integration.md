# Semantic Kernel Integration Guide

This document provides detailed information on how the Emotion Agent application integrates with Semantic Kernel to provide advanced language model capabilities.

## Overview

Semantic Kernel serves as the AI orchestration layer in our application, connecting the various components with language model capabilities. The integration follows a service-oriented architecture with clean separation of concerns.

## Core Components

### 1. KernelService

The `KernelService` class is the primary interface to Semantic Kernel functionality:

```python
class KernelService:
    def __init__(self):
        self.kernel = sk.Kernel()
        self._setup_kernel()
        
    def register_semantic_function(self, plugin_name, function_name, prompt_template):
        # Registers a prompt template as a semantic function
        
    def register_native_function(self, plugin_name, function):
        # Registers a Python function as a native plugin
        
    async def execute_function(self, plugin_name, function_name, variables=None):
        # Executes a registered function with provided variables
```

### 2. AIConfig

The `AIConfig` class manages AI service settings and API keys:

```python
class AIConfig:
    def __init__(self):
        # Load environment variables
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.openai_max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1024"))
        self.openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
```

### 3. PromptService

The `PromptService` handles loading and formatting prompt templates:

```python
class PromptService:
    def __init__(self, prompts_dir=None):
        # Initialize and load prompts
        
    def get_formatted_prompt(self, name):
        # Gets a prompt and formats it for Semantic Kernel
```

## Configuration

### Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```
# AI service configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o
OPENAI_MAX_TOKENS=1024
OPENAI_TEMPERATURE=0.7

# Server configuration
PORT=8000
HOST=0.0.0.0
DEBUG=True
```

### Prompt Templates

Prompts are stored in `backend/prompts/` directory with either `.txt` or `.prompt` extensions. The system automatically converts Jinja2-style templates to Semantic Kernel format:

From:
```
You are an empathetic AI assistant helping someone who is feeling {{ emotion }}.
```

To:
```
You are an empathetic AI assistant helping someone who is feeling {{$emotion}}.
```

## Integration with Agent Kernel

The `AgentKernel` class orchestrates the entire AI processing pipeline:

1. Registers tools with Semantic Kernel
2. Registers semantic functions from prompt templates
3. Processes user input through the analysis pipeline
4. Uses Semantic Kernel to generate personalized responses
5. Integrates with Memory System for contextual awareness

## Usage Examples

### Simple Prompt Execution

```python
# Create services
kernel_service = KernelService()
prompt_service = PromptService()

# Register a semantic function
prompt = prompt_service.get_formatted_prompt("empathy_prompt")
kernel_service.register_semantic_function("agent", "generate_response", prompt)

# Execute the function
response = await kernel_service.execute_function(
    "agent", 
    "generate_response",
    {"emotion": "happy", "user_text": "I got a promotion today!"}
)
```

### Tool Integration

```python
# Register a tool function
@sk_function
async def analyze_emotion(text: str) -> Dict[str, Any]:
    # Analyze emotion in text
    return {"emotion": "happy", "confidence": 0.9}

# Register with the kernel
kernel_service.register_native_function("tools", analyze_emotion)
```

## Adding New Capabilities

### Creating a New Tool

1. Create a new function in the `backend/tools/` directory
2. Register it in the `ToolRegistry` class
3. The `AgentKernel` will automatically register it with Semantic Kernel

### Adding a New Prompt Template

1. Create a new file in `backend/prompts/` directory (e.g., `new_prompt.txt`)
2. Use Jinja2-style syntax for variables (e.g., `{{ variable_name }}`)
3. Load and register it:

```python
prompt = prompt_service.get_formatted_prompt("new_prompt")
kernel_service.register_semantic_function("agent", "new_function", prompt)
```

## Error Handling

The system includes robust error handling:

1. Configuration validation at startup
2. Fallback prompt templates when loading fails
3. Exception handling during function execution
4. Graceful degradation for missing services

## Logging

The integration includes comprehensive logging:

```python
logger = logging.getLogger(__name__)
logger.info("Semantic Kernel initialized with model: %s", config["ai_model_id"])
```

## Performance Considerations

- API calls are the main performance bottleneck
- Cache frequently used results when possible
- Use appropriate token limits to reduce costs
- Consider batching requests where appropriate

## Testing Framework

The Emotion Agent includes a robust testing framework to ensure the Semantic Kernel integration functions correctly across different operating systems.

### Windows Testing

For Windows users, a batch file script (`backend/memory/run_tests.bat`) is provided to simplify running tests:

```batch
@echo off
echo Starting Memory System tests...

REM Check if Python is installed
python --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in the PATH.
    echo Please install Python and try again.
    exit /b 1
)

REM Check if the necessary files exist
if not exist context_store.py (
    echo Error: context_store.py not found in the current directory.
    echo Please run this script from the backend/memory directory.
    exit /b 1
)

if not exist test_context_store.py (
    echo Error: test_context_store.py not found in the current directory.
    echo Please run this script from the backend/memory directory.
    exit /b 1
)

REM Run the test script
echo Running tests...
python test_context_store.py

REM Check if the test was successful
if %ERRORLEVEL% EQU 0 (
    echo All tests completed successfully!
    
    REM Check if test_results.json exists and report its size
    if exist test_results.json (
        for %%A in (test_results.json) do set size=%%~zA
        echo Test results saved to test_results.json (Size: !size! bytes)
    )
) else (
    echo Tests failed with exit code %ERRORLEVEL%
    echo Please check the output above for error details.
    exit /b %ERRORLEVEL%
)

exit /b 0
```

The script performs the following tasks:
1. Checks for Python installation
2. Verifies the existence of necessary files (`context_store.py` and `test_context_store.py`)
3. Runs the test script
4. Reports test results and generates a `test_results.json` file with test outcomes
5. Handles error cases with informative messages

### Cross-Platform Testing

Tests should be run on all target platforms (Windows, macOS, Linux) to ensure compatibility. The testing framework validates:

1. Proper initialization of the Semantic Kernel
2. Memory system integration
3. Prompt template loading and formatting
4. Tool registration and execution
5. Error handling and recovery

Run tests regularly when making changes to the Semantic Kernel integration to ensure backward compatibility and prevent regressions.

## Future Enhancements

- Implement memory integration with Semantic Kernel's built-in memory system
- Add knowledge graph capabilities for more contextual awareness
- Integrate with vector databases for semantic search
- Implement more sophisticated planning and reasoning capabilities 