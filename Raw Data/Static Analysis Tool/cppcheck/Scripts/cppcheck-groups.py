import os
import re
import json

# 源码路径（Cppcheck lib 目录）
cppcheck_lib_dir = r"C:\Poorcomputer\Study\Github\cppcheck\lib"
# 输出路径
output_dir = r"C:\Poorcomputer\Study\Github\CodingRuleMap\Raw Data\Static Analysis Tool\cppcheck\Rule Information\groups"
os.makedirs(output_dir, exist_ok=True)

# 正则：提取 runChecks 函数体中调用的所有 xxx.yyy(...)，提取 yyy
run_checks_pattern = re.compile(r'\b\w+\.(\w+)\s*\(')

for filename in os.listdir(cppcheck_lib_dir):
    if not filename.endswith('.cpp') or not filename[0].islower():
        continue

    filepath = os.path.join(cppcheck_lib_dir, filename)
    module_name = filename[:-4]

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()

    # 提取 runChecks 函数体（函数体内部的内容）
    run_match = re.search(r'void\s+\w+::runChecks\s*\([^)]*\)\s*\{(.*?)\n\}', code, re.DOTALL)
    if not run_match:
        continue

    run_body = run_match.group(1)
    function_calls = run_checks_pattern.findall(run_body)

    if not function_calls:
        continue

    rules = sorted(set(function_calls))  # 去重排序

    group_data = {
        "name": module_name,
        "description": None,
        "rules": rules
    }

    output_path = os.path.join(output_dir, f"{module_name}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(group_data, f, indent=2, ensure_ascii=False)

    print(f"✅ {module_name}.json 已生成，规则数: {len(rules)}")