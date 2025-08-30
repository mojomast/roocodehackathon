"""
Parser Module

This module provides the Parser class that handles code parsing and analysis
for documentation generation.
"""

import logging
import os
import ast
import re
from typing import Dict, List, Optional

# WK-011: Import for AST analysis


class Parser:
    """
    Parses and analyzes source code for documentation generation.

    This class provides functionality to parse various programming languages,
    extract key information, and prepare data for documentation generation.
    """

    def __init__(self):
        """Initialize the Parser with supported file extensions."""
        self.logger = logging.getLogger(__name__)
        self.supported_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust'
        }

    def parse_code(self, clone_path: str) -> Dict:
        """
        Parse the code in a repository and extract relevant information.

        This method scans the repository, identifies supported files,
        and extracts structural information about the codebase.

        Args:
            clone_path (str): Path to the cloned repository

        Returns:
            Dict: Parsed code information including files, functions, classes, etc.
        """
        try:
            self.logger.info(f"Parsing code in repository at {clone_path}")

            if not os.path.exists(clone_path):
                raise FileNotFoundError(f"Repository path does not exist: {clone_path}")

            parsed_data = {
                'files': [],
                'functions': [],
                'classes': [],
                'modules': [],
                'imports': {
                    'direct': [],
                    'from': [],
                    'relative': [],
                    'stdlib': [],
                    'third_party': []
                }
            }

            # Walk through all directories and files
            for root, dirs, files in os.walk(clone_path):
                # Skip common non-code directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'dist', 'build']]

                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, clone_path)

                    # Check if file extension is supported
                    _, ext = os.path.splitext(file)
                    if ext in self.supported_extensions:
                        file_info = self._parse_file(file_path, rel_path, ext)
                        if file_info:
                            parsed_data['files'].append(file_info)

            self.logger.info(f"Successfully parsed {len(parsed_data['files'])} files")
            return parsed_data

        except Exception as e:
            self.logger.error(f"Error parsing code: {e}")
            return {}

    def _parse_file(self, file_path: str, rel_path: str, extension: str) -> Optional[Dict]:
        """
        WK-011: Parse an individual file and extract its structure using AST parsing.

        Performs comprehensive analysis of source files using appropriate parsing methods:
        - Python: Full AST analysis with detailed metadata
        - JavaScript/TypeScript: Regex-based parsing for functions and structures
        - Other languages: Pattern-based extraction

        Args:
            file_path (str): Absolute path to the file
            rel_path (str): Relative path from repository root
            extension (str): File extension

        Returns:
            Optional[Dict]: File information with extracted functions, classes, imports, etc.
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            file_info = {
                'path': rel_path,
                'type': self.supported_extensions.get(extension, 'unknown'),
                'size': len(content),
                'lines': content.count('\n') + 1,
                'functions': [],
                'classes': [],
                'imports': {},
                'language': self.supported_extensions.get(extension, 'unknown')
            }

            # Extract functions using AST or regex parsing
            file_info['functions'] = self.extract_functions(file_path)

            # Extract classes (for Python primarily)
            file_info['classes'] = self.extract_classes(file_path)

            # Extract imports
            file_info['imports'] = self.extract_imports(file_path)

            self.logger.debug(f"WK-011: Successfully parsed {rel_path} - {len(file_info['functions'])} functions, {len(file_info['classes'])} classes")

            return file_info

        except Exception as e:
            self.logger.warning(f"WK-011: Failed to parse file {rel_path}: {e}")
            return None

    # WK-010: Additional stub implementations to prevent AttributeError
    def extract_functions(self, file_path: str) -> list:
        """
        WK-011: Extract function definitions from a file using AST parsing.

        Extracts function definitions using appropriate parsing method
        for each supported programming language.

        Args:
            file_path (str): Path to the source file

        Returns:
            list: List of extracted function definitions with metadata
        """
        try:
            _, ext = os.path.splitext(file_path)
            language = self.supported_extensions.get(ext)

            if not language:
                self.logger.warning(f"WK-011: Unsupported file type: {ext}")
                return []

            if language == 'python':
                return self._extract_python_functions(file_path)
            elif language in ['javascript', 'typescript']:
                return self._extract_js_functions(file_path)
            else:
                return self._extract_other_functions(file_path, language)

        except Exception as e:
            self.logger.warning(f"WK-011: Error extracting functions from {file_path}: {e}")
            return []

    def extract_classes(self, file_path: str) -> list:
        """
        WK-011: Extract class definitions from a file using AST or pattern matching.

        Extracts class information including methods, attributes, and inheritance.
        Currently implements Python AST parsing and regex patterns for other languages.

        Args:
            file_path (str): Path to the source file

        Returns:
            list: List of extracted class definitions with metadata
        """
        try:
            _, ext = os.path.splitext(file_path)
            language = self.supported_extensions.get(ext)

            if language == 'python':
                return self._extract_python_classes(file_path)
            elif language in ['javascript', 'typescript']:
                return self._extract_js_classes(file_path)
            else:
                return self._extract_other_classes(file_path, language)

        except Exception as e:
            self.logger.warning(f"WK-011: Error extracting classes from {file_path}: {e}")
            return []

    def extract_imports(self, file_path: str) -> Dict[str, list]:
        """
        WK-011: Extract import statements from a file with comprehensive dependency analysis.

        Analyzes import statements to understand external dependencies and module relationships.
        Supports multiple programming languages with appropriate parsing methods.

        Args:
            file_path (str): Path to the source file

        Returns:
            Dict[str, list]: Import information categorized by type and containing detailed metadata
        """
        try:
            _, ext = os.path.splitext(file_path)
            language = self.supported_extensions.get(ext, 'unknown')

            if language == 'python':
                return self._extract_python_imports(file_path)
            elif language in ['javascript', 'typescript']:
                return self._extract_js_imports(file_path)
            else:
                return self._extract_other_imports(file_path, language)

        except Exception as e:
            self.logger.warning(f"WK-011: Error extracting imports from {file_path}: {e}")
            return {
                'direct': [],
                'from': [],
                'relative': [],
                'stdlib': [],
                'third_party': []
            }

    def _extract_python_imports(self, file_path: str) -> Dict[str, list]:
        """
        WK-011: Extract Python import statements using AST parsing.
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                source = f.read()

            if not source.strip():
                return {
                    'direct': [],
                    'from': [],
                    'relative': [],
                    'stdlib': [],
                    'third_party': []
                }

            tree = ast.parse(source, filename=file_path)
            imports = {
                'direct': [],
                'from': [],
                'relative': [],
                'stdlib': [],
                'third_party': []
            }

            stdlib_modules = {
                'os', 'sys', 'json', 'urllib', 'http', 'time', 'datetime',
                'collections', 'itertools', 'functools', 're', 'math',
                'random', 'pathlib', 'subprocess', 'threading', 'multiprocessing',
                'logging', 'configparser', 'argparse', 'unittest', 'typing'
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        import_info = {
                            'module': alias.name,
                            'alias': alias.asname,
                            'line': node.lineno,
                            'type': 'direct'
                        }
                        imports['direct'].append(import_info)

                        # Categorize
                        root_module = alias.name.split('.')[0]
                        if '.' in alias.name:
                            imports['third_party'].append(import_info)
                        elif root_module in stdlib_modules:
                            imports['stdlib'].append(import_info)
                        else:
                            imports['third_party'].append(import_info)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        import_info = {
                            'module': node.module,
                            'names': [alias.name for alias in node.names],
                            'aliases': [alias.asname for alias in node.names],
                            'line': node.lineno,
                            'type': 'from'
                        }
                        imports['from'].append(import_info)

                        # Check for relative imports
                        if node.level > 0:
                            imports['relative'].append(import_info)

                        # Categorize
                        root_module = node.module.split('.')[0]
                        if root_module in stdlib_modules:
                            imports['stdlib'].append(import_info)
                        else:
                            imports['third_party'].append(import_info)
                    else:
                        # from . import or from .. import
                        import_info = {
                            'module': '.' * node.level,
                            'names': [alias.name for alias in node.names],
                            'aliases': [alias.asname for alias in node.names],
                            'line': node.lineno,
                            'type': 'relative'
                        }
                        imports['relative'].append(import_info)

            return imports

        except SyntaxError:
            self.logger.warning(f"WK-011: Syntax error in Python import parsing {file_path}")
            return {
                'direct': [],
                'from': [],
                'relative': [],
                'stdlib': [],
                'third_party': []
            }

    def _extract_js_imports(self, file_path: str) -> Dict[str, list]:
        """
        WK-011: Extract JavaScript/TypeScript import statements.
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            imports = {
                'direct': [],
                'from': [],
                'relative': [],
                'stdlib': [],  # Node.js built-ins
                'third_party': []
            }

            # Node.js stdlib modules
            nodejs_stdlib = {
                'fs', 'path', 'http', 'https', 'url', 'querystring',
                'events', 'util', 'crypto', 'stream', 'buffer', 'os'
            }

            # ES6 import statements: import { name } from 'module'
            import_pattern = r"import\s+(?:\{([^}]+)\}|(\w+)|(\*\s+as\s+\w+))\s+from\s+['\"]([^'\"]+)['\"];?"
            matches = re.finditer(import_pattern, content, re.MULTILINE)

            for match in matches:
                imported_items = match.group(1) or match.group(2) or match.group(3)
                module = match.group(4)

                import_info = {
                    'module': module,
                    'items': imported_items if imported_items else [],
                    'line': content[:match.start()].count('\n') + 1,
                    'type': 'from'
                }

                if module.startswith('./') or module.startswith('../'):
                    imports['relative'].append(import_info)
                elif module.split('/')[0] in nodejs_stdlib:
                    imports['stdlib'].append(import_info)
                else:
                    imports['third_party'].append(import_info)

            # CommonJS require statements: const name = require('module')
            require_pattern = r"(?:const|let|var)\s+\{?(\w+)\}?\s*=\s*require\s*\(\s*['\"]([^'\"]+)['\"]\s*\);?"
            matches = re.finditer(require_pattern, content, re.MULTILINE)

            for match in matches:
                var_name = match.group(1)
                module = match.group(2)

                import_info = {
                    'module': module,
                    'variable': var_name,
                    'line': content[:match.start()].count('\n') + 1,
                    'type': 'direct'
                }

                if module.startswith('./') or module.startswith('../'):
                    imports['relative'].append(import_info)
                elif module in nodejs_stdlib:
                    imports['stdlib'].append(import_info)
                else:
                    imports['third_party'].append(import_info)

            return imports

        except Exception as e:
            self.logger.warning(f"WK-011: Error parsing JS imports {file_path}: {e}")
            return {
                'direct': [],
                'from': [],
                'relative': [],
                'stdlib': [],
                'third_party': []
            }

    def _extract_other_imports(self, file_path: str, language: str) -> Dict[str, list]:
        """
        WK-011: Extract import statements from other languages using basic patterns.
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            imports = {
                'direct': [],
                'from': [],
                'relative': [],
                'stdlib': [],
                'third_party': []
            }

            # Basic patterns for different languages
            patterns = {
                'java': [
                    r'import\s+(?:static\s+)?([\w.]+);',  # import java.util.List;
                ],
                'cpp': [
                    r'#include\s*<([^>]+)>',      # #include <iostream>
                    r'#include\s*"([^"]+)"',      # #include "local.h"
                ],
                'c': [
                    r'#include\s*<([^>]+)>',      # #include <stdio.h>
                    r'#include\s*"([^"]+)"',      # #include "local.h"
                ],
                'go': [
                    r'import\s+(?:\([^)]+\)|"([^"]+)")',  # import "fmt"
                ],
                'rust': [
                    r'use\s+([^;]+);',  # use std::collections::HashMap;
                ]
            }

            language_patterns = patterns.get(language, [])
            if not language_patterns:
                return imports

            for pattern in language_patterns:
                matches = re.finditer(pattern, content, re.MULTILINE)
                for match in matches:
                    module = match.group(1)

                    import_info = {
                        'module': module,
                        'line': content[:match.start()].count('\n') + 1,
                        'type': 'direct',
                        'language': language
                    }

                    # Determine if relative or standard library
                    if language in ['cpp', 'c'] and '"' in pattern and module.startswith('./'):
                        imports['relative'].append(import_info)
                    elif language in ['cpp', 'c'] and '<' in pattern:
                        imports['stdlib'].append(import_info)
                    else:
                        imports['direct'].append(import_info)

            return imports

        except Exception as e:
            self.logger.warning(f"WK-011: Error parsing {language} imports {file_path}: {e}")
            return {
                'direct': [],
                'from': [],
                'relative': [],
                'stdlib': [],
                'third_party': []
            }

    def get_language_parser(self, language: str) -> Optional[object]:
        """
        WK-010: Get language-specific parser instance.

        Stub implementation for language-specific parsing strategies.

        Args:
            language (str): Programming language name

        Returns:
            Optional[object]: Parser instance for the language or None
        """
        try:
            parsers = {
                'python': self._get_python_parser(),
                'javascript': self._get_javascript_parser(),
                'typescript': self._get_typescript_parser(),
                'java': self._get_java_parser(),
                'cpp': self._get_cpp_parser(),
            }
            return parsers.get(language.lower())
        except Exception as e:
            self.logger.warning(f"WK-010: Error getting parser for {language}: {e}")
            return None

    def _get_python_parser(self) -> object:
        """WK-011: Get Python AST parser."""
        # Return the Python AST module for parsing
        return ast

    def _extract_python_functions(self, file_path: str) -> list:
        """
        WK-011: Extract function definitions from Python file using AST.

        Parses Python source code using the abstract syntax tree (AST)
        to extract function definitions with detailed metadata.

        Args:
            file_path (str): Path to the Python source file

        Returns:
            list: List of function dictionaries with name, args, docstring, etc.
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                source = f.read()

            if not source.strip():
                return []

            tree = ast.parse(source, filename=file_path)
            functions = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        'name': node.name,
                        'type': 'function',
                        'args': self._extract_function_args(node.args),
                        'line_start': node.lineno,
                        'line_end': getattr(node, 'end_lineno', node.lineno),
                        'docstring': ast.get_docstring(node),
                        'returns': self._get_return_annotation(node),
                        'decorators': [self._get_decorator_name(d) for d in node.decorator_list],
                        'is_async': isinstance(node, ast.AsyncFunctionDef),
                        'file_path': file_path
                    }
                    functions.append(func_info)

                elif isinstance(node, ast.ClassDef):
                    # Extract methods from class
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            func_info = {
                                'name': item.name,
                                'type': 'method',
                                'class_name': node.name,
                                'args': self._extract_function_args(item.args),
                                'line_start': item.lineno,
                                'line_end': getattr(item, 'end_lineno', item.lineno),
                                'docstring': ast.get_docstring(item),
                                'returns': self._get_return_annotation(item),
                                'decorators': [self._get_decorator_name(d) for d in item.decorator_list],
                                'is_async': isinstance(item, ast.AsyncFunctionDef),
                                'file_path': file_path
                            }
                            functions.append(func_info)

            return functions

        except SyntaxError as e:
            self.logger.warning(f"WK-011: Syntax error in Python file {file_path}: {e}")
            return []
        except Exception as e:
            self.logger.warning(f"WK-011: Error parsing Python file {file_path}: {e}")
            return []

    def _extract_function_args(self, args_node) -> list:
        """WK-011: Extract function arguments from AST args node."""
        args = []

        # Positional arguments
        for arg in args_node.args:
            arg_info = {
                'name': arg.arg,
                'type': self._get_annotation_name(arg.annotation) if arg.annotation else None,
                'default': None  # Would need more complex AST analysis
            }
            args.append(arg_info)

        # Keyword-only arguments
        for arg in args_node.kwonlyargs:
            arg_info = {
                'name': arg.arg,
                'type': self._get_annotation_name(arg.annotation) if arg.annotation else None,
                'default': None
            }
            args.append(arg_info)

        # Varargs (*args)
        if args_node.vararg:
            arg_info = {
                'name': f"*{args_node.vararg.arg}",
                'type': self._get_annotation_name(args_node.vararg.annotation) if args_node.vararg.annotation else None,
                'default': None
            }
            args.append(arg_info)

        # Keyword arguments (**kwargs)
        if args_node.kwarg:
            arg_info = {
                'name': f"**{args_node.kwarg.arg}",
                'type': self._get_annotation_name(args_node.kwarg.annotation) if args_node.kwarg.annotation else None,
                'default': None
            }
            args.append(arg_info)

        return args

    def _get_annotation_name(self, annotation_node) -> str:
        """WK-011: Extract type annotation name from AST."""
        if isinstance(annotation_node, ast.Name):
            return annotation_node.id
        elif isinstance(annotation_node, ast.Str):
            return annotation_node.s  # For forward references in older Python
        elif isinstance(annotation_node, ast.Attribute):
            return f"{annotation_node.value.id}.{annotation_node.attr}"
        # Handle more complex annotations like Union, Optional, etc.
        return self._simplify_annotation(annotation_node)

    def _simplify_annotation(self, annotation_node) -> str:
        """WK-011: Simplify complex type annotations."""
        try:
            # Handle subscript annotations like List[str], Dict[str, int]
            if isinstance(annotation_node, ast.Subscript):
                if isinstance(annotation_node.value, ast.Name):
                    base = annotation_node.value.id
                    if isinstance(annotation_node.slice, ast.Tuple):
                        args = [self._simplify_annotation(arg) for arg in annotation_node.slice.elts]
                        return f"{base}[{', '.join(args)}]"
                    else:
                        arg = self._simplify_annotation(annotation_node.slice)
                        return f"{base}[{arg}]"
            return str(annotation_node)
        except:
            return str(annotation_node)

    def _get_return_annotation(self, node) -> str:
        """WK-011: Get return type annotation."""
        if node.returns:
            return self._get_annotation_name(node.returns)
        return None

    def _get_decorator_name(self, decorator_node) -> str:
        """WK-011: Extract decorator name from AST."""
        if isinstance(decorator_node, ast.Name):
            return decorator_node.id
        elif isinstance(decorator_node, ast.Attribute):
            return f"{self._get_annotation_name(decorator_node.value)}.{decorator_node.attr}"
        elif isinstance(decorator_node, ast.Call):
            return self._get_decorator_name(decorator_node.func)
        return str(decorator_node)

    def _get_javascript_parser(self) -> object:
        """WK-011: Stub for JavaScript-specific parsing."""
        # Note: Real JS parsing would require external libraries like esprima or babel
        # For now, return a simple regex-based parser
        return None

    def _extract_js_functions(self, file_path: str) -> list:
        """
        WK-011: Extract function definitions from JavaScript/TypeScript file.

        Uses regex-based parsing since full AST parsing requires external libraries.
        Supports both function declarations and arrow functions.

        Args:
            file_path (str): Path to the JS/TS source file

        Returns:
            list: List of function dictionaries with metadata
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            functions = []

            # Match traditional function declarations: function name(params) {
            func_pattern = r'(?:(export\s+)?(?:async\s+)?)function\s+(\w+)\s*\(([^)]*)\)\s*\{'
            matches = re.finditer(func_pattern, content, re.MULTILINE)

            for match in matches:
                exported, is_async, name, params = match.groups()
                is_async = is_async is not None

                func_info = {
                    'name': name,
                    'type': 'function',
                    'language': 'javascript',
                    'args': self._parse_js_params(params),
                    'is_async': is_async,
                    'exported': exported is not None,
                    'file_path': file_path,
                    'line_start': content[:match.start()].count('\n') + 1,
                    'docstring': None  # JS doesn't have standard docstrings
                }
                functions.append(func_info)

            # Match arrow functions: const name = (params) => {
            arrow_pattern = r'(?:const|let|var)\s+(\w+)\s*[:=]\s*(?:\(([^)]*)\)\s*=>)?\s*\{'
            matches = re.finditer(arrow_pattern, content, re.MULTILINE)

            for match in matches:
                name = match.group(1)
                params = match.group(2) if match.groups()[1] else ""

                func_info = {
                    'name': name,
                    'type': 'arrow_function',
                    'language': 'javascript',
                    'args': self._parse_js_params(params),
                    'is_async': False,  # Would need more complex parsing for async arrows
                    'exported': False,
                    'file_path': file_path,
                    'line_start': content[:match.start()].count('\n') + 1,
                    'docstring': None
                }
                functions.append(func_info)

            return functions

        except Exception as e:
            self.logger.warning(f"WK-011: Error parsing JS file {file_path}: {e}")
            return []

    def _parse_js_params(self, params_str: str) -> list:
        """WK-011: Parse JavaScript/TypeScript function parameters."""
        if not params_str or not params_str.strip():
            return []

        args = []
        for param in params_str.split(','):
            param = param.strip()
            if param:
                # Handle destructuring, default values, etc.
                param_name = param.split(':')[0].split('=')[0].strip()
                # Remove destructuring braces/brackets
                param_name = re.sub(r'[\{\[\]\}\(\)]', '', param_name)
                if param_name:
                    args.append({
                        'name': param_name,
                        'type': None,  # TS would have types, but extracting is complex
                        'default': '=' in param
                    })

        return args

    def _get_typescript_parser(self) -> object:
        """WK-010: Stub for TypeScript-specific parsing."""
        return object()

    def _get_java_parser(self) -> object:
        """WK-011: Stub for Java-specific parsing."""
        # Note: Real Java parsing would require external libraries like javaparser
        return None

    def _extract_other_functions(self, file_path: str, language: str) -> list:
        """
        WK-011: Extract function definitions from other languages using regex patterns.

        Provides basic function extraction for languages without built-in AST support.
        Uses language-specific regex patterns for common function declaration formats.

        Args:
            file_path (str): Path to the source file
            language (str): Programming language

        Returns:
            list: List of function dictionaries with basic metadata
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            patterns = {
                'java': [
                    r'(?:public|private|protected|static|final)?\s*\w+\s+(\w+)\s*\(([^)]*)\)\s*\{',  # method declarations
                    r'\w+\s+(\w+)\s*\(([^)]*)\)\s*\{'  # basic functions
                ],
                'cpp': [
                    r'(?:\w+\s+)*(?:\w+|~?\w+)\s*\([^)]*\)\s*\{',  # functions and methods
                    r'(?:static\s+)?\w+\s+\w+\s*\([^)]*\)\s*\{'  # C++ style
                ],
                'c': [
                    r'(?:\w+\s+)+\w+\s*\([^)]*\)\s*\{',  # C functions
                ],
                'go': [
                    r'func\s+(\w+)\s*\(([^)]*)\)\s*(?:\([^)]*\))?\s*\{',  # Go functions
                ],
                'rust': [
                    r'(?:pub\s+)?(?:fn\s+(\w+)|impl.*?\w+\s*\{.*?fn\s+(\w+))\s*\(([^)]*)\)\s*(?:->\s*\w+\s*)?\{',  # Rust functions
                ]
            }

            functions = []
            lang_patterns = patterns.get(language, [])

            if not lang_patterns:
                self.logger.info(f"WK-011: No patterns defined for {language}, using generic function detection")
                # Generic fallback: look for patterns that might indicate functions
                generic_pattern = r'(\w+)\s*\([^)]*\)\s*\{'
                patterns = [generic_pattern]
            else:
                patterns = lang_patterns

            for pattern in patterns:
                matches = re.finditer(pattern, content, re.MULTILINE)
                for match in matches:
                    func_name = match.group(1) if len(match.groups()) > 0 else "unknown"
                    params = match.group(2) if len(match.groups()) > 1 else ""

                    func_info = {
                        'name': func_name,
                        'type': 'function',
                        'language': language,
                        'args': [{'name': 'params', 'type': None}] if params.strip() else [],
                        'file_path': file_path,
                        'line_start': content[:match.start()].count('\n') + 1,
                        'docstring': None
                    }
                    functions.append(func_info)

            return functions

        except Exception as e:
            self.logger.warning(f"WK-011: Error parsing {language} file {file_path}: {e}")
            return []

    def _extract_python_classes(self, file_path: str) -> list:
        """
        WK-011: Extract class definitions from Python file using AST.
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                source = f.read()

            if not source.strip():
                return []

            tree = ast.parse(source, filename=file_path)
            classes = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'bases': [self._get_annotation_name(base) for base in node.bases],
                        'methods': [],
                        'attributes': [],
                        'line_start': node.lineno,
                        'line_end': getattr(node, 'end_lineno', node.lineno),
                        'docstring': ast.get_docstring(node),
                        'decorators': [self._get_decorator_name(d) for d in node.decorator_list],
                        'file_path': file_path
                    }

                    # Extract methods and attributes
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_info = {
                                'name': item.name,
                                'args': self._extract_function_args(item.args),
                                'is_static': any(d.id == 'staticmethod' for d in item.decorator_list if isinstance(d, ast.Name)),
                                'is_classmethod': any(d.id == 'classmethod' for d in item.decorator_list if isinstance(d, ast.Name))
                            }
                            class_info['methods'].append(method_info)
                        elif isinstance(item, ast.AnnAssign):
                            # Type-annotated attribute
                            attr_info = {
                                'name': item.target.id if isinstance(item.target, ast.Name) else str(item.target),
                                'type': self._get_annotation_name(item.annotation),
                                'default': None
                            }
                            class_info['attributes'].append(attr_info)

                    classes.append(class_info)

            return classes

        except SyntaxError as e:
            self.logger.warning(f"WK-011: Syntax error in Python class parsing {file_path}: {e}")
            return []

    def _extract_js_classes(self, file_path: str) -> list:
        """
        WK-011: Extract class definitions from JavaScript/TypeScript file using regex.
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            classes = []

            # Match class declarations: class Name extends Parent {
            class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{'
            matches = re.finditer(class_pattern, content, re.MULTILINE)

            for match in matches:
                class_name, parent = match.groups()

                class_info = {
                    'name': class_name,
                    'bases': [parent] if parent else [],
                    'methods': [],  # Would need more complex parsing
                    'attributes': [],
                    'language': 'javascript',
                    'file_path': file_path,
                    'line_start': content[:match.start()].count('\n') + 1,
                    'docstring': None
                }
                classes.append(class_info)

            return classes

        except Exception as e:
            self.logger.warning(f"WK-011: Error parsing JS classes {file_path}: {e}")
            return []

    def _extract_other_classes(self, file_path: str, language: str) -> list:
        """
        WK-011: Extract class definitions from other languages using regex patterns.
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            patterns = {
                'java': r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{',
                'cpp': r'class\s+(\w+)(?::\s*(?:public|private|protected)\s+(\w+))?\s*\{',
                'c': r'struct\s+(\w+)\s*\{',  # C uses structs instead of classes
                'rust': r'struct\s+(\w+)\s*\{',
                'go': r'type\s+(\w+)\s+struct\s*\{'
            }

            language_specific_pattern = patterns.get(language)
            if not language_specific_pattern:
                return []  # No pattern defined for this language

            classes = []
            matches = re.finditer(language_specific_pattern, content, re.MULTILINE)

            for match in matches:
                class_name = match.group(1)
                parent = match.group(2) if len(match.groups()) > 1 else None

                class_info = {
                    'name': class_name,
                    'bases': [parent] if parent else [],
                    'language': language,
                    'file_path': file_path,
                    'line_start': content[:match.start()].count('\n') + 1,
                    'methods': [],
                    'attributes': [],
                    'docstring': None
                }
                classes.append(class_info)

            return classes

        except Exception as e:
            self.logger.warning(f"WK-011: Error parsing {language} classes {file_path}: {e}")
            return []

    def _get_cpp_parser(self) -> object:
        """WK-010: Stub for C/C++ specific parsing."""
        return object()

    def get_parsing_stats(self) -> dict:
        """
        WK-010: Get parsing statistics and performance metrics.

        Stub implementation for parsing analytics.

        Returns:
            dict: Statistics about parsing operations
        """
        try:
            stats = {
                'total_files_processed': 0,
                'parsing_errors': 0,
                'supported_languages': list(self.supported_extensions.keys()),
                'avg_processing_time': 0.0
            }
            return stats
        except Exception as e:
            self.logger.warning(f"WK-010: Error getting parsing stats: {e}")
            return {}

    def validate_parsed_data(self, parsed_data: dict) -> bool:
        """
        WK-010: Validate parsed data structure and completeness.

        Stub implementation for data validation.

        Args:
            parsed_data (dict): Parsed data to validate

        Returns:
            bool: True if data is valid, False otherwise
        """
        try:
            if not isinstance(parsed_data, dict):
                self.logger.warning("WK-010: Parsed data is not a dictionary")
                return False

            if 'files' not in parsed_data:
                self.logger.warning("WK-010: Missing 'files' key in parsed data")
                return False

            self.logger.info("WK-010: Parsed data validation passed")
            return True
        except Exception as e:
            self.logger.warning(f"WK-010: Error validating parsed data: {e}")
            return False