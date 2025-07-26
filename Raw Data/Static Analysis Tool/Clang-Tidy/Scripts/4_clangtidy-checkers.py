import os
import json
import re

base_output_dir = r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\clangtidy_analysis\checkers\clangtidy-cpp"
group_dir = r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\clangtidy_analysis\groups\clangtidy-cpp"
source_dir = r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\clangtidy-main\clang-tidy"
doc_dir = r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\clangtidy-main\docs\clang-tidy\checks"
test_dir = r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\clangtidy-main\test\clang-tidy\checkers"

def camel_to_kebab(name):
    return re.sub(r'(?<!^)(?=[A-Z])', '-', name).lower()

def count_loc_branch_api(code):
    loc = len(code.strip().splitlines())
    branches = len(re.findall(r'\bif\b|\belse\b|\bfor\b|\bwhile\b|\bswitch\b|\bcase\b', code))
    apis = len(re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\s*\(', code))  # 粗略统计函数调用
    return loc, branches, apis

def extract_description_from_rst(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding='utf-8') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if line.strip() and not line.startswith('=') and not lines[i-1].startswith('='):
            return line.strip()
    return None

def extract_test_info(test_path):
    if not os.path.exists(test_path):
        return {
            "description": None,
            "expected-problems": 0,
            "expected-linenumbers": [],
            "code": None
        }
    with open(test_path, encoding='utf-8') as f:
        code = f.read()
    lines = code.splitlines()
    linenumbers = [i+1 for i, line in enumerate(lines) if "expected-warning" in line or "CHECK-MESSAGES" in line]
    return {
        "description": None,
        "expected-problems": len(linenumbers),
        "expected-linenumbers": linenumbers,
        "code": "\n" + "\n".join(lines)
    }

for group_file in os.listdir(group_dir):
    if not group_file.endswith(".json"):
        continue
    group_name = os.path.splitext(group_file)[0]
    group_path = os.path.join(group_dir, group_file)
    with open(group_path, encoding='utf-8') as f:
        group_data = json.load(f)

    for rule in group_data.get("rules", []):
        rule_kebab = camel_to_kebab(rule)
        output_folder = os.path.join(base_output_dir, group_name)
        os.makedirs(output_folder, exist_ok=True)

        cpp_path = os.path.join(source_dir, group_name, rule + "Check.cpp")
        doc_path = os.path.join(doc_dir, group_name, rule_kebab + ".rst")
        test_path = os.path.join(test_dir, group_name, rule_kebab + ".cpp")
        output_path = os.path.join(output_folder, rule + ".json")

        try:
            with open(cpp_path, encoding='utf-8') as f:
                code = f.read()
            loc, branches, apis = count_loc_branch_api(code)
        except FileNotFoundError:
            loc, branches, apis = 0, 0, 0
            code = ""

        description = extract_description_from_rst(doc_path)
        test_info = extract_test_info(test_path)

        data = {
            "name": rule,
            "language": "cpp",
            "description": description,
            "example": None,
            "cwe": None,
            "cwe-description": None,
            "checker-language": "cpp",
            "loc": loc,
            "branches": branches,
            "apis": apis,
            "test": [test_info]
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
