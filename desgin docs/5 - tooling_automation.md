# 5. 🛠️ Tooling and Automation - ZIL to Python 3.14 Port

## Development Environment Setup

### Python 3.14 Environment Configuration

#### Virtual Environment Setup
```bash
# Create dedicated development environment
python3.14 -m venv deadline_port_env
source deadline_port_env/bin/activate  # Linux/Mac
# deadline_port_env\Scripts\activate  # Windows

# Upgrade pip and install build tools
python -m pip install --upgrade pip setuptools wheel
```

#### Requirements Management
```python
# requirements-dev.txt
# Core development dependencies
python>=3.14
black>=23.0.0           # Code formatting
isort>=5.12.0           # Import sorting
mypy>=1.5.0             # Type checking
pytest>=7.4.0           # Testing framework
pytest-cov>=4.1.0       # Coverage reporting
pytest-mock>=3.11.1     # Mocking utilities
hypothesis>=6.82.0       # Property-based testing
flake8>=6.0.0           # Linting
pre-commit>=3.3.0       # Git hooks
sphinx>=7.1.0           # Documentation generation
rich>=13.4.0            # Enhanced console output
typer>=0.9.0            # CLI framework
pydantic>=2.1.0         # Data validation
dataclasses-json>=0.5.9 # JSON serialization

# Game-specific dependencies
prompt-toolkit>=3.0.39  # Enhanced input handling
colorama>=0.4.6         # Cross-platform colors
click>=8.1.6            # Command-line interface
regex>=2023.6.3         # Advanced regex features
```

### Static Analysis and Code Quality Tools

#### Type Checking Configuration
```toml
# pyproject.toml
[tool.mypy]
python_version = "3.14"
warn_return_any = true
warn_unused_configs = true
warn_unreachable = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
strict_equality = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true

[[tool.mypy.overrides]]
module = "deadline.*"
strict = true
```

#### Code Formatting and Linting
```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py314']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 88
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true

[tool.flake8]
max-line-length = 88
extend-ignore = ["E203", "W503"]
exclude = [".git", "__pycache__", "build", "dist"]
```

## ZIL Analysis Tools

### ZIL Parser for Source Analysis
```python
# tools/zil_parser.py
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ZilObject:
    name: str
    properties: Dict[str, str]
    location: Optional[str] = None
    flags: List[str] = None
    
@dataclass  
class ZilRoutine:
    name: str
    parameters: List[str]
    body: str
    type_declarations: Dict[str, str] = None

class ZilSourceAnalyzer:
    """Parse and analyze ZIL source files"""
    
    def __init__(self):
        self.objects: Dict[str, ZilObject] = {}
        self.routines: Dict[str, ZilRoutine] = {}
        self.globals: Dict[str, str] = {}
        self.constants: Dict[str, str] = {}
        self.syntax_rules: List[str] = []
        
    def analyze_file(self, file_path: Path) -> Dict[str, any]:
        """Analyze a single ZIL file"""
        content = file_path.read_text(encoding='utf-8')
        
        # Extract different constructs
        objects = self._extract_objects(content)
        routines = self._extract_routines(content)
        globals_vars = self._extract_globals(content)
        constants = self._extract_constants(content)
        syntax = self._extract_syntax(content)
        
        return {
            'objects': objects,
            'routines': routines,
            'globals': globals_vars,
            'constants': constants,
            'syntax': syntax,
            'dependencies': self._analyze_dependencies(content)
        }
    
    def _extract_objects(self, content: str) -> List[ZilObject]:
        """Extract OBJECT definitions from ZIL code"""
        pattern = r'<OBJECT\s+([A-Z-]+).*?(?=<OBJECT|<ROUTINE|$)'
        matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)
        
        objects = []
        for match in matches:
            obj_def = match.group(0)
            obj_name = match.group(1)
            
            # Parse properties
            properties = self._parse_object_properties(obj_def)
            
            objects.append(ZilObject(
                name=obj_name,
                properties=properties,
                location=properties.get('IN'),
                flags=properties.get('FLAGS', '').split()
            ))
            
        return objects
    
    def _extract_routines(self, content: str) -> List[ZilRoutine]:
        """Extract ROUTINE definitions from ZIL code"""
        pattern = r'<ROUTINE\s+([A-Z-]+)\s*\((.*?)\).*?(?=<ROUTINE|<OBJECT|$)'
        matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)
        
        routines = []
        for match in matches:
            routine_name = match.group(1)
            params_str = match.group(2)
            routine_body = match.group(0)
            
            # Parse parameters
            parameters = self._parse_routine_parameters(params_str)
            
            routines.append(ZilRoutine(
                name=routine_name,
                parameters=parameters,
                body=routine_body
            ))
            
        return routines
    
    def generate_dependency_graph(self, source_dir: Path) -> Dict[str, List[str]]:
        """Generate dependency graph between ZIL files"""
        dependencies = {}
        
        for zil_file in source_dir.glob("*.zil"):
            file_deps = self.analyze_file(zil_file)['dependencies']
            dependencies[zil_file.stem] = file_deps
            
        return dependencies

# Usage
analyzer = ZilSourceAnalyzer()
analysis = analyzer.analyze_file(Path("deadline.zil"))
dependency_graph = analyzer.generate_dependency_graph(Path("zil_source/"))
```

### Automated Translation Tool
```python
# tools/zil_translator.py
from typing import Dict, List
import re
from pathlib import Path

class ZilToPythonTranslator:
    """Automated ZIL to Python code translation"""
    
    def __init__(self):
        self.translation_rules = self._load_translation_rules()
        self.python_templates = self._load_python_templates()
        
    def translate_file(self, zil_file: Path, output_dir: Path):
        """Translate a ZIL file to Python"""
        content = zil_file.read_text()
        analyzer = ZilSourceAnalyzer()
        analysis = analyzer.analyze_file(zil_file)
        
        # Generate Python module
        python_code = self._generate_python_module(analysis, zil_file.stem)
        
        # Write output
        output_file = output_dir / f"{zil_file.stem.lower()}.py"
        output_file.write_text(python_code)
        
        return output_file
    
    def _generate_python_module(self, analysis: Dict, module_name: str) -> str:
        """Generate Python module from ZIL analysis"""
        lines = []
        
        # Module header
        lines.extend(self._generate_module_header(module_name))
        
        # Import statements
        lines.extend(self._generate_imports(analysis))
        
        # Constants
        lines.extend(self._generate_constants(analysis['constants']))
        
        # Object classes
        lines.extend(self._generate_object_classes(analysis['objects']))
        
        # Function definitions
        lines.extend(self._generate_functions(analysis['routines']))
        
        return '\n'.join(lines)
    
    def _generate_object_classes(self, objects: List[ZilObject]) -> List[str]:
        """Generate Python classes from ZIL objects"""
        lines = []
        
        for obj in objects:
            class_name = self._zil_name_to_python_class(obj.name)
            
            lines.append(f"\nclass {class_name}(GameObject):")
            lines.append('    """Auto-generated from ZIL object"""')
            lines.append("    def __init__(self):")
            lines.append("        super().__init__(")
            
            # Add properties
            for prop, value in obj.properties.items():
                py_value = self._translate_zil_value(value)
                lines.append(f'            {prop.lower()}={py_value},')
            
            lines.append("        )")
            lines.append("")
            
        return lines
    
    def _translate_zil_value(self, zil_value: str) -> str:
        """Translate ZIL values to Python equivalents"""
        translations = {
            'T': 'True',
            '<>': 'None', 
            'RFALSE': 'return False',
            'RTRUE': 'return True',
        }
        
        # Handle string literals
        if zil_value.startswith('"') and zil_value.endswith('"'):
            return zil_value
            
        # Handle numbers
        if zil_value.isdigit():
            return zil_value
            
        return translations.get(zil_value, f'"{zil_value}"')

# Batch translation script
def translate_deadline_project():
    translator = ZilToPythonTranslator()
    source_dir = Path("zil_source")
    output_dir = Path("python_output")
    
    output_dir.mkdir(exist_ok=True)
    
    for zil_file in source_dir.glob("*.zil"):
        print(f"Translating {zil_file.name}...")
        output_file = translator.translate_file(zil_file, output_dir)
        print(f"Generated {output_file}")
```

## Build and Deployment Automation

### Build System Configuration
```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="deadline-if",
    version="1.0.0",
    description="Deadline Interactive Fiction - Python Port",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Port Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.14",
    install_requires=[
        "prompt-toolkit>=3.0.39",
        "colorama>=0.4.6",
        "typer>=0.9.0",
        "rich>=13.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "mypy>=1.5.0",
            "flake8>=6.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "deadline=deadline.main:main",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment",
        "Programming Language :: Python :: 3.14",
    ],
)
```

### Automated Testing Pipeline
```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.14"]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
        pip install -e .
    
    - name: Lint with flake8
      run: |
        flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 src tests --count --exit-zero --max-complexity=10 --statistics
    
    - name: Check types with mypy
      run: mypy src/deadline
    
    - name: Format check with black
      run: black --check src tests
    
    - name: Import sort check
      run: isort --check-only src tests
    
    - name: Test with pytest
      run: |
        pytest tests/ -v --cov=deadline --cov-report=xml --cov-report=html
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Pre-commit Hooks Configuration
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3.14

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

## Development Utilities

### Debug and Testing Tools
```python
# tools/debug_tools.py
import pdb
import traceback
import logging
from typing import Any, Dict
from functools import wraps

class GameDebugger:
    """Enhanced debugging utilities for game development"""
    
    def __init__(self):
        self.debug_mode = False
        self.command_history = []
        self.game_state_snapshots = []
        
    def enable_debug_mode(self):
        """Enable comprehensive debugging"""
        self.debug_mode = True
        logging.basicConfig(level=logging.DEBUG)
        
    def debug_command(self, func):
        """Decorator to debug command execution"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.debug_mode:
                print(f"DEBUG: Executing {func.__name__} with args={args}, kwargs={kwargs}")
                
            try:
                result = func(*args, **kwargs)
                if self.debug_mode:
                    print(f"DEBUG: {func.__name__} returned: {result}")
                return result
            except Exception as e:
                if self.debug_mode:
                    print(f"DEBUG: {func.__name__} failed with: {e}")
                    traceback.print_exc()
                raise
                
        return wrapper
    
    def snapshot_game_state(self, label: str = None):
        """Capture current game state for debugging"""
        from deadline.game import GameState
        
        snapshot = {
            'timestamp': time.time(),
            'label': label or f"snapshot_{len(self.game_state_snapshots)}",
            'state': GameState.get_instance().serialize(),
            'command_count': len(self.command_history)
        }
        
        self.game_state_snapshots.append(snapshot)
        
    def compare_snapshots(self, snapshot1_idx: int, snapshot2_idx: int):
        """Compare two game state snapshots"""
        snap1 = self.game_state_snapshots[snapshot1_idx]
        snap2 = self.game_state_snapshots[snapshot2_idx]
        
        # Deep comparison logic here
        differences = self._compare_dicts(snap1['state'], snap2['state'])
        
        print(f"Comparison: {snap1['label']} -> {snap2['label']}")
        for path, (old_val, new_val) in differences.items():
            print(f"  {path}: {old_val} -> {new_val}")
    
    def _compare_dicts(self, dict1: Dict, dict2: Dict, path: str = "") -> Dict[str, tuple]:
        """Recursively compare dictionaries"""
        differences = {}
        
        all_keys = set(dict1.keys()) | set(dict2.keys())
        for key in all_keys:
            current_path = f"{path}.{key}" if path else key
            
            if key not in dict1:
                differences[current_path] = (None, dict2[key])
            elif key not in dict2:
                differences[current_path] = (dict1[key], None)
            elif isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                sub_diffs = self._compare_dicts(dict1[key], dict2[key], current_path)
                differences.update(sub_diffs)
            elif dict1[key] != dict2[key]:
                differences[current_path] = (dict1[key], dict2[key])
        
        return differences

# Game testing utilities
class GameTester:
    """Automated game testing utilities"""
    
    def __init__(self, game_instance):
        self.game = game_instance
        self.test_scenarios = []
        
    def load_test_scenario(self, scenario_file: str):
        """Load test scenario from file"""
        import json
        with open(scenario_file, 'r') as f:
            scenario = json.load(f)
        self.test_scenarios.append(scenario)
        
    def run_scenario(self, scenario_name: str) -> bool:
        """Execute a test scenario"""
        scenario = next((s for s in self.test_scenarios if s['name'] == scenario_name), None)
        if not scenario:
            raise ValueError(f"Scenario '{scenario_name}' not found")
        
        # Reset game to initial state
        self.game.reset()
        
        # Execute commands
        for step in scenario['steps']:
            command = step['command']
            expected_output = step.get('expected_output')
            expected_state = step.get('expected_state')
            
            result = self.game.execute_command(command)
            
            if expected_output and expected_output not in result.message:
                print(f"FAIL: Expected '{expected_output}' in output, got '{result.message}'")
                return False
                
            if expected_state:
                current_state = self.game.get_state_dict()
                if not self._validate_state(current_state, expected_state):
                    print(f"FAIL: Game state validation failed after command '{command}'")
                    return False
        
        print(f"SUCCESS: Scenario '{scenario_name}' completed successfully")
        return True
    
    def _validate_state(self, current_state: Dict, expected_state: Dict) -> bool:
        """Validate game state matches expected values"""
        for key, expected_value in expected_state.items():
            if key not in current_state:
                return False
            if current_state[key] != expected_value:
                return False
        return True
```

### Performance Profiling Tools
```python
# tools/profiling.py
import cProfile
import pstats
import time
from functools import wraps
from typing import Dict, List
import psutil
import os

class GameProfiler:
    """Performance profiling utilities for the game"""
    
    def __init__(self):
        self.profiler = cProfile.Profile()
        self.performance_log = []
        self.memory_snapshots = []
        
    def profile_function(self, func):
        """Decorator to profile individual functions"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            start_memory = psutil.Process(os.getpid()).memory_info().rss
            
            self.profiler.enable()
            try:
                result = func(*args, **kwargs)
            finally:
                self.profiler.disable()
            
            end_time = time.perf_counter()
            end_memory = psutil.Process(os.getpid()).memory_info().rss
            
            self.performance_log.append({
                'function': func.__name__,
                'duration': end_time - start_time,
                'memory_delta': end_memory - start_memory,
                'timestamp': time.time()
            })
            
            return result
        return wrapper
    
    def profile_command_processing(self):
        """Profile the main game command processing loop"""
        stats = pstats.Stats(self.profiler)
        stats.sort_stats('cumulative')
        
        # Print top 20 time-consuming functions
        print("Top 20 functions by cumulative time:")
        stats.print_stats(20)
        
        # Focus on game-specific modules
        print("\nGame-specific module performance:")
        stats.print_stats('deadline.*')
        
    def generate_performance_report(self, output_file: str = "performance_report.txt"):
        """Generate comprehensive performance report"""
        with open(output_file, 'w') as f:
            f.write("DEADLINE GAME PERFORMANCE REPORT\n")
            f.write("=" * 40 + "\n\n")
            
            # Function call statistics
            f.write("Function Performance Summary:\n")
            f.write("-" * 30 + "\n")
            
            function_stats = {}
            for entry in self.performance_log:
                func_name = entry['function']
                if func_name not in function_stats:
                    function_stats[func_name] = {
                        'calls': 0,
                        'total_time': 0,
                        'total_memory': 0,
                        'max_time': 0,
                        'max_memory': 0
                    }
                
                stats = function_stats[func_name]
                stats['calls'] += 1
                stats['total_time'] += entry['duration']
                stats['total_memory'] += entry['memory_delta']
                stats['max_time'] = max(stats['max_time'], entry['duration'])
                stats['max_memory'] = max(stats['max_memory'], entry['memory_delta'])
            
            for func_name, stats in sorted(function_stats.items(), 
                                         key=lambda x: x[1]['total_time'], reverse=True):
                avg_time = stats['total_time'] / stats['calls']
                avg_memory = stats['total_memory'] / stats['calls']
                
                f.write(f"{func_name}:\n")
                f.write(f"  Calls: {stats['calls']}\n")
                f.write(f"  Total Time: {stats['total_time']:.4f}s\n")
                f.write(f"  Average Time: {avg_time:.4f}s\n")
                f.write(f"  Max Time: {stats['max_time']:.4f}s\n")
                f.write(f"  Average Memory: {avg_memory/1024:.2f} KB\n")
                f.write(f"  Max Memory: {stats['max_memory']/1024:.2f} KB\n\n")

# Memory leak detection
class MemoryTracker:
    """Track memory usage over time to detect leaks"""
    
    def __init__(self):
        self.snapshots = []
        self.baseline = None
        
    def take_snapshot(self, label: str = None):
        """Take a memory usage snapshot"""
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        snapshot = {
            'timestamp': time.time(),
            'label': label or f"snapshot_{len(self.snapshots)}",
            'rss': memory_info.rss,
            'vms': memory_info.vms,
            'percent': process.memory_percent()
        }
        
        if self.baseline is None:
            self.baseline = snapshot
            
        self.snapshots.append(snapshot)
        
    def detect_leaks(self, threshold_mb: int = 10) -> List[Dict]:
        """Detect potential memory leaks"""
        if len(self.snapshots) < 2:
            return []
        
        leaks = []
        baseline_rss = self.baseline['rss']
        
        for snapshot in self.snapshots[1:]:
            growth = (snapshot['rss'] - baseline_rss) / (1024 * 1024)  # MB
            
            if growth > threshold_mb:
                leaks.append({
                    'label': snapshot['label'],
                    'growth_mb': growth,
                    'timestamp': snapshot['timestamp'],
                    'total_mb': snapshot['rss'] / (1024 * 1024)
                })
                
        return leaks
```

### Documentation Generation Tools
```python
# tools/doc_generator.py
import ast
import inspect
from pathlib import Path
from typing import Dict, List, Optional
import re

class DocumentationGenerator:
    """Generate documentation from ZIL comments and Python code"""
    
    def __init__(self):
        self.api_docs = {}
        self.zil_comments = {}
        
    def extract_zil_comments(self, zil_file: Path) -> Dict[str, str]:
        """Extract comments and documentation from ZIL files"""
        content = zil_file.read_text()
        
        # Extract routine documentation
        routine_docs = {}
        pattern = r';.*?\n<ROUTINE\s+([A-Z-]+)'
        
        matches = re.finditer(pattern, content, re.MULTILINE)
        for match in matches:
            comment = match.group(0).split('\n')[0][1:].strip()  # Remove ;
            routine_name = match.group(1)
            routine_docs[routine_name] = comment
            
        return routine_docs
    
    def generate_api_documentation(self, python_module_path: Path) -> str:
        """Generate API documentation from Python modules"""
        docs = []
        docs.append("# API Documentation\n")
        
        for py_file in python_module_path.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
                
            module_docs = self._document_python_module(py_file)
            if module_docs:
                docs.append(module_docs)
        
        return "\n".join(docs)
    
    def _document_python_module(self, py_file: Path) -> str:
        """Document a single Python module"""
        try:
            with open(py_file, 'r') as f:
                tree = ast.parse(f.read())
        except:
            return ""
        
        docs = [f"\n## Module: {py_file.stem}\n"]
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                docs.append(self._document_class(node))
            elif isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                docs.append(self._document_function(node))
        
        return "\n".join(docs) if len(docs) > 1 else ""
    
    def _document_class(self, class_node: ast.ClassDef) -> str:
        """Document a Python class"""
        docs = [f"\n### Class: {class_node.name}\n"]
        
        if ast.get_docstring(class_node):
            docs.append(ast.get_docstring(class_node) + "\n")
        
        # Document methods
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                docs.append(f"#### {node.name}\n")
                if ast.get_docstring(node):
                    docs.append(ast.get_docstring(node) + "\n")
        
        return "\n".join(docs)
    
    def _document_function(self, func_node: ast.FunctionDef) -> str:
        """Document a Python function"""
        docs = [f"\n### Function: {func_node.name}\n"]
        
        if ast.get_docstring(func_node):
            docs.append(ast.get_docstring(func_node) + "\n")
        
        return "\n".join(docs)

# Game walkthrough generator
class WalkthroughGenerator:
    """Generate game walkthroughs and hint systems"""
    
    def __init__(self, game_instance):
        self.game = game_instance
        self.solution_paths = []
        
    def generate_optimal_walkthrough(self) -> List[str]:
        """Generate the optimal solution path"""
        # This would use game state analysis to find the shortest solution
        optimal_commands = [
            "examine body",
            "take note from body", 
            "read note",
            "north",
            "question mrs. robner about alibi",
            "examine desk",
            "open drawer",
            "take key from drawer",
            "south",
            "west", 
            "unlock door with key",
            "north",
            "examine safe",
            "examine painting",
            "move painting",
            "open safe",
            "take papers from safe",
            "read papers",
            "south",
            "east",
            "north",
            "accuse george robner of murder"
        ]
        
        return optimal_commands
    
    def generate_hint_system(self) -> Dict[str, List[str]]:
        """Generate contextual hints for players"""
        hints = {
            "starting_room": [
                "Look around carefully.",
                "Examine everything in detail.",
                "Don't forget to look at the victim.",
                "Check if there's anything on the body."
            ],
            "investigation": [
                "Talk to all the suspects.",
                "Ask about their whereabouts.",
                "Look for physical evidence.",
                "Check all rooms thoroughly."
            ],
            "evidence": [
                "Read any documents you find.",
                "Some evidence might be hidden.",
                "Check desks and furniture.",
                "Look behind paintings."
            ],
            "finale": [
                "Review all the evidence.",
                "Consider means, motive, and opportunity.",
                "Make sure you have proof.",
                "Confront the murderer directly."
            ]
        }
        
        return hints
```

### Deployment and Distribution Tools
```bash
#!/bin/bash
# scripts/build_release.sh

set -e  # Exit on any error

echo "Building Deadline Interactive Fiction Release..."

# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Ensure we're in a clean state
git status --porcelain | grep -q . && {
    echo "Working directory is not clean. Commit or stash changes first."
    exit 1
}

# Run tests
echo "Running test suite..."
pytest tests/ -v --cov=deadline --cov-fail-under=80

# Type checking
echo "Running type checking..."
mypy src/deadline

# Code quality checks
echo "Running code quality checks..."
black --check src tests
isort --check-only src tests
flake8 src tests

# Build distribution
echo "Building Python package..."
python setup.py sdist bdist_wheel

# Create standalone executable
echo "Creating standalone executable..."
pip install pyinstaller
pyinstaller --onefile --name deadline src/deadline/main.py

# Package game data
echo "Packaging game data files..."
mkdir -p dist/deadline-standalone/
cp dist/deadline dist/deadline-standalone/
cp -r data/ dist/deadline-standalone/
cp README.md LICENSE dist/deadline-standalone/

# Create release archive
echo "Creating release archive..."
cd dist/
tar -czf deadline-if-$(python -c "import deadline; print(deadline.__version__)").tar.gz deadline-standalone/
cd ..

echo "Build complete! Release files are in dist/"
```

### Continuous Integration Configuration
```dockerfile
# Dockerfile for testing environment
FROM python:3.14-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy source code
COPY . .

# Install package in development mode
RUN pip install -e .

# Default command runs tests
CMD ["pytest", "tests/", "-v", "--cov=deadline"]
```

### Makefile for Common Tasks
```makefile
# Makefile
.PHONY: help install test lint format type-check docs clean build

help:		## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $1, $2}'

install:	## Install development dependencies
	pip install -r requirements-dev.txt
	pip install -e .
	pre-commit install

test:		## Run test suite
	pytest tests/ -v --cov=deadline --cov-report=html

lint:		## Run linting checks
	flake8 src tests
	black --check src tests
	isort --check-only src tests

format:		## Format code
	black src tests
	isort src tests

type-check:	## Run type checking
	mypy src/deadline

docs:		## Generate documentation
	python tools/doc_generator.py
	sphinx-build -b html docs/ docs/_build/

clean:		## Clean build artifacts
	rm -rf build/ dist/ *.egg-info/ .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:		## Build distribution packages
	python setup.py sdist bdist_wheel

translate:	## Run ZIL to Python translation
	python tools/zil_translator.py --input zil_source/ --output src/deadline/

profile:	## Run performance profiling
	python tools/profiling.py --profile-game

release:	## Build release packages
	./scripts/build_release.sh
```

This comprehensive tooling and automation setup provides the foundation for efficient development, testing, and deployment of the Deadline port from ZIL to Python 3.14. The tools cover static analysis, automated translation, performance profiling, testing utilities, and deployment automation.
        