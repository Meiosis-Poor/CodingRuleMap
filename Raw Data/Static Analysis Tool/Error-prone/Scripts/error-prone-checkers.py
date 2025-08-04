import os
import re
import json

# 规则代码目录
base_dir = r"C:\Poorcomputer\Study\Github\error-prone\core\src\main\java\com\google\errorprone\bugpatterns"
# 测试代码目录
test_base_dir = r"C:\Poorcomputer\Study\Github\error-prone\core\src\test\java\com\google\errorprone\bugpatterns"
# 输出目录
output_base = r"C:\Poorcomputer\Study\Github\CodingRuleMap\Raw Data\Static Analysis Tool\Error-prone\Rule Information\checkers"

def count_code_metrics(code: str):
    loc = sum(1 for line in code.splitlines() if line.strip() and not line.strip().startswith("//"))
    branches = len(re.findall(r'\b(if|else|switch|case|for|while|catch)\b', code))
    apis = len(re.findall(r'\b[A-Z][A-Za-z0-9_]+\s*\(', code))
    return loc, branches, apis

def extract_summary(annotation_block: str):
    pattern = re.compile(
        r'summary\s*=\s*((?:"[^"]*"\s*\+\s*)*"[^"]*")',
        re.DOTALL
    )
    m = pattern.search(annotation_block)
    if not m:
        return None
    raw_summary = m.group(1)
    parts = re.findall(r'"([^"]*)"', raw_summary)
    summary = ''.join(parts)
    return summary

def extract_annotation_content(text, start_pos):
    stack = []
    i = start_pos
    n = len(text)
    if text[i] != '(':
        return None, i
    stack.append('(')
    i += 1
    start_content = i
    while i < n and stack:
        if text[i] == '(':
            stack.append('(')
        elif text[i] == ')':
            stack.pop()
        i += 1
    if stack:
        return None, i
    end_content = i - 1
    return text[start_content:end_content], i

def find_matching_brace(text, start_pos):
    if start_pos >= len(text) or text[start_pos] != '{':
        return -1
    stack = ['{']
    i = start_pos + 1
    while i < len(text) and stack:
        if text[i] == '{':
            stack.append('{')
        elif text[i] == '}':
            stack.pop()
        i += 1
    if stack:
        return -1
    return i - 1

def extract_tests_for_rule(rule_name):
    tests = []
    for root, _, files in os.walk(test_base_dir):
        for f in files:
            if f == f"{rule_name}Test.java":
                test_file_path = os.path.join(root, f)
                with open(test_file_path, "r", encoding="utf-8") as tf:
                    test_content = tf.read()

                test_positions = [m.start() for m in re.finditer(r'@Test', test_content)]

                for pos in test_positions:
                    method_match = re.search(
                        r'@Test\s*[\r\n\s]*public\s+\w+\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[^{]+)?\s*\{',
                        test_content[pos:], re.MULTILINE)
                    if not method_match:
                        continue
                    method_name = method_match.group(1)

                    method_start = pos + method_match.start()
                    start_line_num = test_content[:method_start].count('\n') + 1

                    brace_start = test_content.find('{', method_start)
                    if brace_start == -1:
                        continue
                    brace_end = find_matching_brace(test_content, brace_start)
                    if brace_end == -1:
                        continue
                    method_code_block = test_content[method_start:brace_end+1]

                    triple_quote_matches = re.findall(r'"""(.*?)"""', method_code_block, re.DOTALL)
                    code_str = "\n".join(triple_quote_matches).strip() if triple_quote_matches else ""

                    tests.append({
                        "description": method_name,
                        "expected-problems": None,
                        "expected-linenumbers": [start_line_num],
                        "code": code_str
                    })

                return tests
    return []

for root, _, files in os.walk(base_dir):
    for file in files:
        if not file.endswith(".java"):
            continue

        file_path = os.path.join(root, file)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        positions = [m.start() for m in re.finditer(r'@BugPattern', content)]
        if not positions:
            continue

        for pos in positions:
            start_paren = content.find('(', pos)
            if start_paren == -1:
                continue
            annotation_block, _ = extract_annotation_content(content, start_paren)
            if not annotation_block:
                continue

            summary = extract_summary(annotation_block)
            if not summary:
                continue

            class_match = re.search(r'public\s+(?:final\s+)?class\s+(\w+)', content)
            if not class_match:
                continue
            class_name = class_match.group(1)

            loc, branches, apis = count_code_metrics(content)

            tests = extract_tests_for_rule(class_name)

            relative_path = os.path.relpath(file_path, base_dir)
            subfolder = os.path.dirname(relative_path)
            rule_name = os.path.splitext(file)[0]
            output_dir = os.path.join(output_base, subfolder)
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, rule_name + ".json")

            rule_info = {
                "name": rule_name,
                "language": "java",
                "description": summary,
                "example": None,
                "cwe": None,
                "cwe-description": None,
                "checker-language": "java",
                "loc": loc,
                "branches": branches,
                "apis": apis,
                "test": tests if tests else [
                    {
                        "description": None,
                        "expected-problems": None,
                        "expected-linenumbers": [],
                        "code": ""
                    }
                ]
            }

            with open(output_path, "w", encoding="utf-8") as out_f:
                json.dump(rule_info, out_f, indent=2, ensure_ascii=False)
            print(f"生成规则文件: {output_path}")

            break  # 每文件只处理第一个规则
