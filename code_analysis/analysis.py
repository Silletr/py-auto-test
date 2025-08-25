import ast
import os


class Analysis:
    def __init__(self, folder: str, file_extensions: str = ".py"):
        self.folder = folder
        self.file_extensions = file_extensions.split(",")

    # Deceting all files in current dir
    def detect_files(self):
        result = []
        for root, dirs, files in os.walk(self.folder):
            for file in files:
                if any(file.endswith(ext) for ext in self.file_extensions):
                    result.append(os.path.join(root, file))
        return result

    # Output all def`s, classe`s and etc in files
    def analysis(self):
        report = {}
        for f in self.detect_files():
            with open(f, "r", encoding="utf-8") as file:
                code = file.read()
            tree = ast.parse(code)

            imports = []
            classes = {}
            functions = {}
            variables = []

            # Outputting all def (with arguments), classes, and all files
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                    imports.append(ast.unparse(node))
                elif isinstance(node, ast.ClassDef):
                    classes[node.name] = [
                        n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                elif isinstance(node, ast.FunctionDef):
                    functions[node.name] = [arg.arg for arg in node.args.args]
                elif isinstance(node, ast.Assign):
                    variables.append([ast.unparse(t) for t in node.targets])

            report[f] = {
                "imports": imports,
                "classes": classes,
                "functions": functions,
                "variables": variables,
                "lines": len(code.splitlines())
            }
        return report


# Creating test example
a = Analysis(".", ".py")
analysis_report = a.analysis()

for f, data in analysis_report.items():
    print(f"\nFile: {f}")
    print(" Imports:", data["imports"])
    print(" Classes:", data["classes"])
    print(" Functions:", data["functions"])
    print(" Variables:", data["variables"])
    print(" Lines:", data["lines"])
