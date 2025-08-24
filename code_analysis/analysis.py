import os


class Analysis:
    def __init__(self, folder: str, file_extensions: str = ".py"):
        self.folder = folder

        # Supporting multiple extensions
        self.file_extensions = file_extensions.split(",")

    def detect_files(self):
        """Search all files with need extensions"""
        result = []
        for root, dirs, files in os.walk(self.folder):
            for file in files:
                if any(file.endswith(ext) for ext in self.file_extensions):
                    result.append(os.path.join(root, file))
        return result

    def analysis(self):
        """Simply example, returning number of lines in file"""
        files = self.detect_files()
        report = {}
        for f in files:
            with open(f, "r", encoding="utf-8") as file:
                report[f] = len(file.readlines())
        return report


a = Analysis(".", ".py")
print("File list in dir:")
for f in a.detect_files():
    print(f" - {f}")

print("\nNumber of lines in file:")
for f, lines in a.analysis().items():
    print(f" - {f}: {lines} lines")
