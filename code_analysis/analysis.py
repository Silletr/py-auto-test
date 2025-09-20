import ast
import os
import argparse
from rich.console import Console
from rich.table import Table

class VariableVisitor(ast.NodeVisitor):
    def __init__(self):
        self.variables = []

    def visit_Assign(self, node):
        self.variables.extend([ast.unparse(t) for t in node.targets])
        self.generic_visit(node)

class Analysis:
    def __init__(self, folder: str, file_extensions: str = ".py"):
        if not os.path.isdir(folder):
            raise ValueError(f"Directory '{folder}' does not exist or is not a directory")
        self.folder = folder
        self.file_extensions = file_extensions.split(",")

    def detect_files(self):
        result = []
        for root, dirs, files in os.walk(self.folder):
            for file in files:
                if any(file.lower().endswith(ext.lower()) for ext in self.file_extensions):
                    result.append(os.path.join(root, file))
        return result

    def _analyze_imports(self, node):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return ast.unparse(node).replace("import ", "", 1)
        return None

    def _analyze_classes(self, node):
        if isinstance(node, ast.ClassDef):
            return node.name, [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
        return None

    def _analyze_functions(self, node):
        if isinstance(node, ast.FunctionDef):
            return node.name, [arg.arg for arg in node.args.args]
        return None

    def _analyze_variables(self, tree):
        visitor = VariableVisitor()
        visitor.visit(tree)
        return visitor.variables

    def analysis(self):
        report = {}
        for f in self.detect_files():
            try:
                with open(f, "r", encoding="utf-8") as file:
                    code = file.read()
                tree = ast.parse(code)

                imports = []
                classes = {}
                functions = {}
                variables = self._analyze_variables(tree)

                for node in ast.iter_child_nodes(tree):
                    if import_str := self._analyze_imports(node):
                        imports.append(import_str)
                    elif class_info := self._analyze_classes(node):
                        classes[class_info[0]] = class_info[1]
                    elif func_info := self._analyze_functions(node):
                        functions[func_info[0]] = func_info[1]

                report[f] = {
                    "imports": imports,
                    "classes": classes,
                    "functions": functions,
                    "variables": variables,
                    "lines": len(code.splitlines())
                }
            except (SyntaxError, UnicodeDecodeError, FileNotFoundError) as e:
                report[f] = {"error": f"Failed to process: {str(e)}"}
                continue
        return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Python code in a directory")
    parser.add_argument("directory", default=".", nargs="?", help="Directory to analyze")
    parser.add_argument("--ext", default=".py", help="File extensions to analyze")
    args = parser.parse_args()

    console = Console()
    a = Analysis(args.directory, args.ext)
    analysis_report = a.analysis()

    for f, data in analysis_report.items():
        table = Table(title=f"File: {f}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        if "error" in data:
            table.add_row("Error", data["error"])
        else:
            table.add_row("Imports", str(data["imports"]))
            table.add_row("Classes", str(data["classes"]))
            table.add_row("Functions", str(data["functions"]))
            table.add_row("Variables", str(data["variables"]))
            table.add_row("Lines", str(data["lines"]))
        
        console.print(table)
