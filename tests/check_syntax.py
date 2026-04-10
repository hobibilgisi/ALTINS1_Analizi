import ast
with open("main.py", "r", encoding="utf-8") as f:
    source = f.read()
ast.parse(source)
lines = source.count("\n") + 1
print(f"Syntax OK — {lines} satır")
