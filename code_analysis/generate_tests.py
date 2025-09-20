import pytest
import os
from analysis import Analysis

class GenerateTests:
    def __init__(self, directory: str, output_dir: str = "tests", exclude_dirs: list = None, exclude_files: list = None):
        """
        Initialize test generator.
        :param directory: Directory to analyze (passed to Analysis)
        :param output_dir: Where to save generated tests
        :param exclude_dirs: List of directories to exclude (e.g., ['tests'])
        :param exclude_files: List of files to exclude (e.g., ['main.py'])
        """
        self.directory = directory
        self.output_dir = output_dir
        self.exclude_dirs = exclude_dirs or ["tests"]
        self.exclude_files = exclude_files or ["main.py"]
        self.analysis = Analysis(directory, ".py")
        self.analysis_results = self.analysis.analysis()

    def _should_process_file(self, file_path: str) -> bool:
        """
        Check if file should be processed (exclude dirs/files).
        """
        if any(exclude_dir in file_path for exclude_dir in self.exclude_dirs):
            return False
        if os.path.basename(file_path) in self.exclude_files:
            return False
        return True

    def generate_tests(self):
        """
        Generate test files for each analyzed file.
        """
        os.makedirs(self.output_dir, exist_ok=True)

        for file_path, data in self.analysis_results.items():
            if not self._should_process_file(file_path):
                continue

            if "error" in data:
                print(f"Skipping {file_path} due to error: {data['error']}")
                continue

            module_name = os.path.basename(file_path).replace(".py", "")
            test_file = os.path.join(self.output_dir, f"test_{module_name}.py")
            test_code = f"import pytest\nimport {module_name}\n\n"

            for func_name, args in data["functions"].items():
                test_code += f"def test_{func_name}():\n"
                inputs = ", ".join(["1" if i % 2 == 0 else "'test'" for i in range(len(args))])
                test_code += f"    result = {module_name}.{func_name}({inputs})\n"
                test_code += f"    assert result is not None  # Basic check\n\n"

            for class_name, methods in data["classes"].items():
                test_code += f"class Test{class_name}:\n"
                test_code += f"    def setup_method(self):\n"
                test_code += f"        self.obj = {module_name}.{class_name}()\n\n"
                for method in methods:
                    if method != "__init__":
                        test_code += f"    def test_{method}(self):\n"
                        test_code += f"        result = self.obj.{method}()\n"
                        test_code += f"        assert result is not None  # Basic check\n\n"

            with open(test_file, "w", encoding="utf-8") as file:
                file.write(test_code)
            print(f"Generated test file: {test_file}")

# Usage example
if __name__ == "__main__":
    generator = GenerateTests(
        directory=".",
        exclude_dirs=["tests", ".git", "__pycache__"],
        exclude_files=["main.py", "analysis.py", "generate_tests.py", "__init__.py"]
    )
    generator.generate_tests()
