"""Test generation using LLM"""
import os
from typing import List, Dict, Any
from openai import AzureOpenAI
import json
import uuid

class TestGenerator:
    """Generate unit tests using Azure OpenAI"""
    
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.environ.get('AZURE_OPENAI_API_KEY'),
            api_version=os.environ.get('AZURE_OPENAI_API_VERSION'),
            azure_endpoint=os.environ.get('AZURE_OPENAI_ENDPOINT')
        )
        self.deployment = os.environ.get('AZURE_OPENAI_DEPLOYMENT_NAME')
    
    def generate_tests_for_file(self, file_path: str, code_content: str, 
                               file_type: str) -> List[Dict[str, Any]]:
        """Generate test cases for a single file"""
        if file_type == 'python':
            return self._generate_python_tests(file_path, code_content)
        elif file_type in ['javascript', 'typescript']:
            return self._generate_javascript_tests(file_path, code_content)
        else:
            return []
    
    def _generate_python_tests(self, file_path: str, code_content: str) -> List[Dict[str, Any]]:
        """Generate Python unit tests"""
        prompt = f"""You are an expert Python test engineer. Generate comprehensive unit tests for the following Python code.

Code:
```python
{code_content}
```

Generate pytest test cases that:
1. Test all public functions and methods
2. Include edge cases and error conditions
3. Use appropriate fixtures and mocks
4. Follow pytest best practices
5. Achieve high code coverage

Return the tests as a JSON array with this format:
[
  {{
    "test_name": "test_function_name",
    "test_code": "def test_function_name():\n    # test code here",
    "description": "What this test validates"
  }}
]

Only return the JSON array, no other text."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": "You are an expert test engineer. Generate high-quality unit tests."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from markdown code blocks if present
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            tests_data = json.loads(content)
            
            # Convert to our format
            test_cases = []
            for test in tests_data:
                test_cases.append({
                    'id': str(uuid.uuid4()),
                    'file_path': file_path,
                    'test_code': test['test_code'],
                    'test_type': 'unit',
                    'description': test['description']
                })
            
            return test_cases
            
        except Exception as e:
            print(f"Error generating tests: {e}")
            return []
    
    def _generate_javascript_tests(self, file_path: str, code_content: str) -> List[Dict[str, Any]]:
        """Generate JavaScript/TypeScript tests"""
        prompt = f"""You are an expert JavaScript test engineer. Generate comprehensive unit tests for the following code.

Code:
```javascript
{code_content}
```

Generate Jest test cases that:
1. Test all exported functions and components
2. Include edge cases and error conditions
3. Use appropriate mocks and spies
4. Follow Jest best practices
5. Achieve high code coverage

Return the tests as a JSON array with this format:
[
  {{
    "test_name": "should test something",
    "test_code": "test('should test something', () => {{ ... }})",
    "description": "What this test validates"
  }}
]

Only return the JSON array, no other text."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": "You are an expert test engineer. Generate high-quality unit tests."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from markdown code blocks if present
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            tests_data = json.loads(content)
            
            # Convert to our format
            test_cases = []
            for test in tests_data:
                test_cases.append({
                    'id': str(uuid.uuid4()),
                    'file_path': file_path,
                    'test_code': test['test_code'],
                    'test_type': 'unit',
                    'description': test['description']
                })
            
            return test_cases
            
        except Exception as e:
            print(f"Error generating tests: {e}")
            return []
    
    def generate_tests_for_pr(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate tests for all files in PR"""
        all_tests = []
        
        for file_info in files:
            file_path = file_info.get('file_path', '')
            content = file_info.get('content', file_info.get('changes', ''))
            file_type = self._get_file_type(file_path)
            
            # Skip test files and non-code files
            if 'test' in file_path.lower() or file_type == 'unknown':
                continue
            
            tests = self.generate_tests_for_file(file_path, content, file_type)
            all_tests.extend(tests)
        
        return all_tests
    
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
