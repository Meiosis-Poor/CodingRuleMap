import os
import re
import json
from collections import defaultdict
from difflib import SequenceMatcher

checkers_path = r"C:\Poorcomputer\Study\Github\cppcheck\lib\checkers.cpp"
lib_dir = r"C:\Poorcomputer\Study\Github\cppcheck\lib"
test_dir = r"C:\Poorcomputer\Study\Github\cppcheck\test"
output_base = r"C:\Poorcomputer\Study\Github\CodingRuleMap\Raw Data\Static Analysis Tool\cppcheck\Rule Information\checkers"

# 分词（支持 CamelCase 和 snake_case）
def split_words(name):
    # 先按下划线分割（snake_case）
    parts = re.split(r'_', name)
    tokens = []
    for part in parts:
        # 对每一部分再按 CamelCase 分割
        camel_parts = re.findall(r'[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|\d+', part)
        tokens.extend([p.lower() for p in camel_parts if p])
    return tokens


# 模糊度：词集合对称差
def word_sequence_similarity(a, b):
    a_words = split_words(a)
    b_words = split_words(b)
    sm = SequenceMatcher(None, a_words, b_words)
    return sm.ratio()

# 提取 checkers 中的规则名
def extract_checkers(path):
    pattern = re.compile(r'"(Check\w+)::(\w+)"')
    with open(path, encoding='utf-8') as f:
        return pattern.findall(f.read())

# 计算 LOC、分支数、API 数
def count_metrics(code):
    loc = len([line for line in code.splitlines() if line.strip()])
    branches = len(re.findall(r'\bif\b|\belse\b|\bfor\b|\bwhile\b|\bswitch\b|\bcase\b', code))
    apis = len(re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\s*\(', code))
    return loc, branches, apis



import re

def extract_code_by_logchecker(code: str, checker_name: str):
    def block(start: int) -> str | None:
        """从 start 开始提取完整的 {...} 块，忽略字符串与字符常量中的大括号"""
        brace_count = 0
        in_string = in_char = escape = False
        for i in range(start, len(code)):
            c = code[i]
            if escape and c == '\n':
                escape = False
            elif c == '\\':
                escape = True
            elif in_string:
                if c == '"':
                    in_string = False
            elif c == '"':
                in_string = True
            elif c == '{':
                if brace_count == 0:
                    brace_start = i
                brace_count += 1
            elif c == '}':
                brace_count -= 1
                if brace_count == 0:
                    return code[brace_start:i + 1]
        return None

    # 1. 定位 logChecker("CheckXxx::checkYyy")
    log_pattern = re.escape(f'logChecker("{checker_name}")')
    log_match = re.search(log_pattern, code)
    if not log_match:
        return None

    log_pos = log_match.start()

    # 2. 向上查找函数头
    func_header_pattern = re.compile(
        r'^[\w:<>\s*&]+::\s*\w+\s*\([^)]*\)\s*(const)?\s*\{',
        re.MULTILINE
    )
    for match in reversed(list(func_header_pattern.finditer(code, 0, log_pos))):
        func_start = match.start()
        return block(func_start)

    print(f"未找到函数头：{checker_name}")
    return None




# 匹配 lib 目录中的 cpp 实现文件（CheckXxx → checkxxx.cpp）
def match_cpp_file(group):
    # 如果后缀是 Portability，就删掉这个后缀
    if group.lower().endswith("portability"):
        group = group[:-len("Portability")]
    target = group.lower()
    for f in os.listdir(lib_dir):
        if f.endswith(".cpp") and f[:-4].lower() == target:
            return os.path.join(lib_dir, f)
    print(f"未找到实现文件：{group}")
    return None


# 匹配 test 目录中的测试文件（CheckXxx → testxxx.cpp）
import os
import re

def extract_test_info(group, rule_base):
    if group.lower().endswith("portability"):
        group = group[:-len("Portability")]
    test_file = os.path.join(test_dir, f"test{group[5:].lower()}.cpp")
    if not os.path.exists(test_file):
        print(f"未找到测试文件：test{group[5:].lower()}.cpp")
        return None

    with open(test_file, encoding='utf-8') as f:
        code = f.read()

    if rule_base.lower().startswith("check"):
        rule_base = rule_base[5:]
    # 1. 准确匹配函数
    pattern_exact = re.compile(
        rf'void\s+(?:check)?{re.escape(rule_base)}(?:\d*|Error)?\s*\(',
        re.IGNORECASE
    )
    matches = list(pattern_exact.finditer(code))
    if matches:
        linenumbers = [code[:m.start()].count('\n') + 1 for m in matches]
        print(f"准确匹配到 {len(matches)} 个测试函数，规则名：{rule_base}，测试文件：test{group[5:].lower()}.cpp")
        return {
            "description": None,
            "expected-problems": len(linenumbers),
            "expected-linenumbers": linenumbers,
            "code": "\n" + code
        }

    # 2. 模糊匹配
    all_funcs = re.findall(
        r'[\w\s:&*<>]+\s+(?:check)?([A-Za-z_][A-Za-z0-9_:]*)\s*\(',
        code,
        re.IGNORECASE
    )
    candidates = [(name, word_sequence_similarity(rule_base.lower(), name.lower()))
                  for name in all_funcs]
    candidates.sort(key=lambda x: x[1], reverse=True)

    for candidate, score in candidates:
        if score >= 0.6:
            print(f"模糊匹配尝试2：{rule_base} -> {candidate}（相似度 {score:.2f}）")
            pattern_candidate = re.compile(
                rf'void\s+(?:check)?{re.escape(candidate)}\s*\(',
                re.IGNORECASE
            )
            candidate_matches = list(pattern_candidate.finditer(code))
            if candidate_matches:
                linenumbers = [code[:m.start()].count('\n') + 1 for m in candidate_matches]
                return {
                    "description": None,
                    "expected-problems": len(linenumbers),
                    "expected-linenumbers": linenumbers,
                    "code": "\n" + code
                }

    # 3. 延迟 check(...) 内容提取的 ASSERT_EQUALS 匹配
    assert_pattern = re.compile(
        rf'ASSERT_EQUALS\(\s*".*?\[.*?{re.escape(rule_base)}.*?\]\\n",\s*errout_str\(\)\s*\);',
        re.DOTALL
    )

    check_pattern = re.compile(
        r'check\s*\(\s*((?:"(?:[^"\\]|\\.)*"\s*)+)\)',
        re.DOTALL
    )

    # 只记录位置 + match 对象
    check_candidates = [(m.start(), m) for m in check_pattern.finditer(code)]

    assert_matches = list(assert_pattern.finditer(code))
    check_strings = []
    linenumbers = []

    for am in assert_matches:
        a_pos = am.start()

        nearest = None
        for c_pos, c_match in reversed(check_candidates):
            if c_pos < a_pos and (a_pos - c_pos <= 100):
                nearest = (c_match, code[:c_pos].count('\n') + 1)
                break

        if nearest:
            c_match, c_line = nearest
            raw_args = c_match.group(1)
            string_parts = re.findall(r'"((?:[^"\\]|\\.)*)"', raw_args)
            joined = '\n'.join(string_parts)
            check_strings.append(joined)
            linenumbers.append(c_line)

    if check_strings:
        full_code = 'check("' + '\\n"\n"'.join(check_strings) + '");'
        print(f"通过 ASSERT_EQUALS 匹配到 {len(check_strings)} 个 check 测试代码段，规则名：{rule_base}，测试文件：test{group[5:].lower()}.cpp")
        return {
            "description": None,
            "expected-problems": len(check_strings),
            "expected-linenumbers": linenumbers,
            "code": full_code
        }

    print(f"未找到匹配的测试函数，规则名：{rule_base}，测试文件：test{group[5:].lower()}.cpp")
    return None



# 主流程：解析所有规则，聚合变体并输出为 JSON
checkers_raw = extract_checkers(checkers_path)
group_rules = defaultdict(list)

# 聚合规则名（去除 Error / 数字后缀）
for group, rule in checkers_raw:
    rule_base = re.sub(r'(Error|\d+)$', '', rule)
    key = (group, rule_base)
    group_rules[key].append(rule)

for (group, rule_base), rule_variants in group_rules.items():
    rule_name = rule_base
    cpp_path = match_cpp_file(group)
    if not cpp_path:
        continue

    with open(cpp_path, encoding='utf-8') as f:
        cpp_code = f.read()

    combined_code = ""
    for variant in rule_variants:
        func_code = extract_code_by_logchecker(cpp_code, f"{group}::{variant}")
        if func_code:
            combined_code += func_code + "\n"

    if not combined_code:
        print(f"未找到函数代码：{group}::{rule_base}")
        continue

    loc, branches, apis = count_metrics(combined_code)
    test_info = extract_test_info(group, rule_base)

    rule_info = {
        "name": rule_name,
        "language": "cpp",
        "description": None,
        "example": None,
        "cwe": None,
        "cwe-description": None,
        "checker-language": "cpp",
        "loc": loc,
        "branches": branches,
        "apis": apis,
        "test": [test_info] if test_info else []
    }

    output_dir = os.path.join(output_base, group)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{rule_name}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(rule_info, f, indent=2, ensure_ascii=False)

print("所有规则信息提取完毕")