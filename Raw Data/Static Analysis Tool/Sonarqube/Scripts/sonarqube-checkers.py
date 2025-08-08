import os
import json
import re

rule_base_path = r"C:\Poorcomputer\Study\Github\sonarqube\sonar-core\src\main\java\org\sonar\core"
test_base_path = r"C:\Poorcomputer\Study\Github\sonarqube\sonar-core\src\test\java\org\sonar\core"
output_base = r"C:\Poorcomputer\Study\Github\CodingRuleMap\Raw Data\Static Analysis Tool\Sonarqube\Rule Information\checkers"

def count_branches(lines):
    keywords = ['if', 'else', 'switch', 'for', 'while', 'do']
    return sum(1 for line in lines for kw in keywords if re.search(r'\b' + kw + r'\b', line))

def count_apis(lines):
    return sum(len(re.findall(r'\.\w+\s*\(', line)) for line in lines)

def extract_class_body(lines, class_name):
    code = "\n".join(lines)
    pattern = re.compile(rf'\b(class|interface|enum)\s+{class_name}\b[^\n]*{{')
    match = pattern.search(code)
    if not match:
        return None
    start = match.start()
    return extract_block_from(code[start:])

def extract_block_from(code_fragment):
    brace_count = 0
    body_lines = []
    started = False
    for line in code_fragment.splitlines():
        if '{' in line:
            brace_count += line.count('{')
            started = True
        if started:
            body_lines.append(line)
        if '}' in line:
            brace_count -= line.count('}')
            if brace_count == 0:
                break
    return body_lines

def extract_tests(test_file_path):
    with open(test_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    code = "\n".join(lines)
    test_entries = []

    # 找所有 @Test 方法
    test_pattern = re.compile(r'@Test\s+public\s+void\s+(\w+)\s*\([^)]*\)\s*{', re.MULTILINE)
    matches = list(test_pattern.finditer(code))

    for match in matches:
        method_name = match.group(1)
        start = match.start()

        # 提取方法体
        method_body_lines = extract_block_from(code[start:])
        if not method_body_lines:
            continue

        test_code = "\n".join(method_body_lines)
        test_lines = sum(1 for line in method_body_lines if line.strip())

        test_entries.append({
            "description": method_name,
            "expected-problems": None,
            "expected-linenumbers": test_lines,
            "code": test_code
        })

    return test_entries

def process_java_file(java_path, relative_path):
    if os.path.basename(java_path) == "package-info.java":
        return

    rule_name = os.path.splitext(os.path.basename(java_path))[0]

    with open(java_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    class_body = extract_class_body(lines, rule_name)
    if not class_body:
        return

    loc = sum(1 for line in class_body if line.strip())
    branches = count_branches(class_body)
    apis = count_apis(class_body)

    # 尝试匹配测试文件路径
    test_relative_path = os.path.join(os.path.dirname(relative_path), f"{rule_name}Test.java")
    test_file_path = os.path.join(test_base_path, test_relative_path)
    test_entries = []

    if os.path.exists(test_file_path):
        test_entries = extract_tests(test_file_path)

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
        "test": test_entries
    }

    rel_dir = os.path.dirname(relative_path)
    output_dir = os.path.join(output_base, rel_dir)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{rule_name}.json")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(rule_info, f, indent=2, ensure_ascii=False)

def scan_java_files():
    for root, _, files in os.walk(rule_base_path):
        for file in files:
            if file.endswith(".java") and file != "package-info.java":
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, rule_base_path)
                process_java_file(full_path, relative_path)

if __name__ == "__main__":
    scan_java_files()
