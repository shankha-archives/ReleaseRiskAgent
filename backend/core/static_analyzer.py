"""Static code analysis module"""
import ast
import re
from typing import List, Dict, Any
from backend.models import StaticAnalysisResult
from radon.complexity import cc_visit
from radon.metrics import mi_visit
import subprocess
import tempfile
import os

class StaticAnalyzer:
    """Perform static code analysis"""
    
    def __init__(self):
        self.supported_languages = ['python', 'javascript', 'typescript']
    
    def analyze_file(self, file_path: str, content: str, file_type: str) -> Dict[str, Any]:
        """Analyze a single file"""
        if file_type == 'python':
            return self._analyze_python(file_path, content)
        elif file_type in ['javascript', 'typescript']:
            return self._analyze_javascript(file_path, content)
        else:
            return self._generic_analysis(file_path, content)
    
    def _analyze_python(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze Python code"""
        issues = []
        complexity_score = 0
        maintainability_index = 100
        loc = len([line for line in content.split('\n') if line.strip()])
        
        try:
            # Parse AST
            tree = ast.parse(content)
            
            # Complexity analysis using radon
            complexity_results = cc_visit(content)
            if complexity_results:
                avg_complexity = sum(r.complexity for r in complexity_results) / len(complexity_results)
                complexity_score = min(avg_complexity / 10, 1.0)  # Normalize to 0-1
                
                # Flag high complexity
                for result in complexity_results:
                    if result.complexity > 10:
                        issues.append({
                            'type': 'high_complexity',
                            'severity': 'warning',
                            'message': f"{result.name} has complexity {result.complexity}",
                            'line': result.lineno
                        })
            
            # Maintainability index
            mi_results = mi_visit(content, multi=True)
            if mi_results:
                maintainability_index = mi_results
                if maintainability_index < 20:
                    issues.append({
                        'type': 'low_maintainability',
                        'severity': 'error',
                        'message': f"Low maintainability index: {maintainability_index:.1f}",
                        'line': 1
                    })
            
            # Check for common anti-patterns
            issues.extend(self._check_python_antipatterns(content))
            
        except SyntaxError as e:
            issues.append({
                'type': 'syntax_error',
                'severity': 'error',
                'message': str(e),
                'line': e.lineno if hasattr(e, 'lineno') else 0
            })
        except Exception as e:
            issues.append({
                'type': 'analysis_error',
                'severity': 'info',
                'message': f"Could not fully analyze: {str(e)}",
                'line': 0
            })
        
        return {
            'file_path': file_path,
            'issues': issues,
            'complexity_score': round(complexity_score, 2),
            'maintainability_index': round(maintainability_index, 1) if isinstance(maintainability_index, float) else maintainability_index,
            'loc': loc
        }
    
    def _check_python_antipatterns(self, content: str) -> List[Dict[str, Any]]:
        """Check for Python anti-patterns"""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Bare except
            if re.search(r'except\s*:', line):
                issues.append({
                    'type': 'bare_except',
                    'severity': 'warning',
                    'message': 'Bare except clause found',
                    'line': i
                })
            
            # TODO/FIXME comments
            if re.search(r'#.*\b(TODO|FIXME|XXX)\b', line, re.IGNORECASE):
                issues.append({
                    'type': 'todo_comment',
                    'severity': 'info',
                    'message': 'TODO/FIXME comment found',
                    'line': i
                })
            
            # Hardcoded credentials patterns
            if re.search(r'(password|api_key|secret|token)\s*=\s*["\'][^"\']+["\']', line, re.IGNORECASE):
                issues.append({
                    'type': 'hardcoded_secret',
                    'severity': 'error',
                    'message': 'Potential hardcoded secret detected',
                    'line': i
                })
        
        return issues
    
    def _analyze_javascript(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript code"""
        issues = []
        loc = len([line for line in content.split('\n') if line.strip()])
        
        # Basic pattern matching for common issues
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Console.log
            if 'console.log' in line and 'eslint-disable' not in line:
                issues.append({
                    'type': 'console_log',
                    'severity': 'warning',
                    'message': 'console.log statement found',
                    'line': i
                })
            
            # TODO comments
            if re.search(r'//.*\b(TODO|FIXME|XXX)\b', line, re.IGNORECASE):
                issues.append({
                    'type': 'todo_comment',
                    'severity': 'info',
                    'message': 'TODO/FIXME comment found',
                    'line': i
                })
            
            # Hardcoded API keys
            if re.search(r'(apiKey|api_key|token|secret)\s*[=:]\s*["\'][^"\']+["\']', line, re.IGNORECASE):
                issues.append({
                    'type': 'hardcoded_secret',
                    'severity': 'error',
                    'message': 'Potential hardcoded secret detected',
                    'line': i
                })
        
        # Estimate complexity (simple heuristic)
        complexity_score = min(len(re.findall(r'\bif\b|\bfor\b|\bwhile\b|\bswitch\b', content)) / 20, 1.0)
        
        return {
            'file_path': file_path,
            'issues': issues,
            'complexity_score': round(complexity_score, 2),
            'maintainability_index': 65.0,  # Default for JS
            'loc': loc
        }
    
    def _generic_analysis(self, file_path: str, content: str) -> Dict[str, Any]:
        """Generic analysis for unsupported file types"""
        loc = len([line for line in content.split('\n') if line.strip()])
        
        return {
            'file_path': file_path,
            'issues': [],
            'complexity_score': 0.0,
            'maintainability_index': 100.0,
            'loc': loc
        }
    
    def analyze_pr(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze all files in a PR"""
        results = []
        
        for file_info in files:
            file_path = file_info.get('file_path', '')
            content = file_info.get('content', file_info.get('changes', ''))
            
            # Determine file type
            file_type = self._get_file_type(file_path)
            
            if file_type:
                analysis = self.analyze_file(file_path, content, file_type)
                results.append(analysis)
        
        return results
    
    def _get_file_type(self, file_path: str) -> str:
        """Determine file type from path"""
        if file_path.endswith('.py'):
            return 'python'
        elif file_path.endswith(('.js', '.jsx')):
            return 'javascript'
        elif file_path.endswith(('.ts', '.tsx')):
            return 'typescript'
        else:
            return 'unknown'
