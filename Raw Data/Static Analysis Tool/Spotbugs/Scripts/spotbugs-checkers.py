import os
import json
import re

# 规则源码路径
base_path = r"C:\Poorcomputer\Study\Github\spotbugs\spotbugs\src\main\java\edu\umd\cs\findbugs"
# 测试路径
test_base = r"C:\Poorcomputer\Study\Github\spotbugs\spotbugs-tests\src\test\java\edu\umd\cs\findbugs"
# 输出路径
output_base = r"C:\Poorcomputer\Study\Github\CodingRuleMap\Raw Data\Static Analysis Tool\Spotbugs\Rule Information\checkers"

def extract_rule_name(filepath):
    return os.path.splitext(os.path.basename(filepath))[0]

def analyze_java_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    loc = len(lines)
    branches = sum(1 for line in lines if re.search(r'\b(if|else\s+if|for|while|case|catch|switch)\b', line))
    apis = sum(1 for line in lines if '.' in line and '(' in line and not line.strip().startswith("//"))
    return loc, branches, apis

def build_output_path(filepath):
    rel_path = os.path.relpath(filepath, base_path)
    rel_dir = os.path.dirname(rel_path)
    rule_name = extract_rule_name(filepath)
    output_dir = os.path.join(output_base, rel_dir)
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, f"{rule_name}.json")

def find_test_file(rule_name):
    # 查找 Test 文件
    test_filename = rule_name + "Test.java"
    for root, _, files in os.walk(test_base):
        if test_filename in files:
            return os.path.join(root, test_filename)
    return None

def extract_tests_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    tests = []

    idx = 0
    while idx < len(lines):
        line = lines[idx]
        if "@Test" in line:
            inside_test = True
            func_code = [line]
            func_name = ""
            start_line = idx + 1  # 1-based line number
            brace_balance = 0
            idx += 1

            # 找到函数头
            while idx < len(lines):
                func_code.append(lines[idx])
                match = re.search(r'\bvoid\s+(\w+)\s*\(', lines[idx])
                if match:
                    func_name = match.group(1)
                    # 检查是否有 '{'
                    brace_balance += lines[idx].count('{') - lines[idx].count('}')
                    break
                idx += 1

            # 找到函数体结束（brace balance = 0）
            idx += 1
            while idx < len(lines) and brace_balance >= 0:
                func_code.append(lines[idx])
                brace_balance += lines[idx].count('{') - lines[idx].count('}')
                if brace_balance == 0:
                    end_line = idx + 1  # 1-based
                    break
                idx += 1

            tests.append({
                "description": func_name,
                "expected-problems": None,
                "expected-linenumbers": [start_line, end_line],
                "code": "".join(func_code).strip()
            })
        idx += 1

    return tests

# 主流程
for root, _, files in os.walk(base_path):
    for file in files:
        if not file.endswith(".java"):
            continue

        full_path = os.path.join(root, file)
        rule_name = extract_rule_name(full_path)
        loc, branches, apis = analyze_java_file(full_path)

        rule_info = {
            "name": rule_name,
            "language": "java",
            "description": None,
            "example": None,
            "cwe": None,
            "cwe-description": None,
            "checker-language": "java",
            "loc": loc,
            "branches": branches,
            "apis": apis,
            "test": []
        }

        # 查找对应测试
        test_file = find_test_file(rule_name)
        if test_file:
            rule_info["test"] = extract_tests_from_file(test_file)

        # 保存 JSON
        output_path = build_output_path(full_path)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(rule_info, f, indent=2, ensure_ascii=False)

print("规则与测试信息提取完成")
