import os
import json

base_dir = r"C:\Poorcomputer\Study\Github\error-prone\core\src\main\java\com\google\errorprone\bugpatterns"
output_base = r"C:\Poorcomputer\Study\Github\CodingRuleMap\Raw Data\Static Analysis Tool\Error-prone\Rule Information\groups"

def is_rule_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            return '@BugPattern' in content
    except:
        return False

groups = {}

# 处理 base 目录下的规则文件
base_files = []
for f in os.listdir(base_dir):
    if f.endswith(".java"):
        full_path = os.path.join(base_dir, f)
        if is_rule_file(full_path):
            base_files.append(os.path.splitext(f)[0])

if base_files:
    groups["bugpatterns"] = base_files

# 遍历一级子目录，收集规则文件
for entry in os.listdir(base_dir):
    full_path = os.path.join(base_dir, entry)
    if os.path.isdir(full_path):
        rules = []
        for f in os.listdir(full_path):
            if f.endswith(".java"):
                rule_path = os.path.join(full_path, f)
                if is_rule_file(rule_path):
                    rules.append(os.path.splitext(f)[0])
        if rules:
            groups[entry] = rules

# 保存每个组的 JSON 文件
for group_name, rules in groups.items():
    group_info = {
        "name": group_name,
        "description": None,
        "rules": rules
    }

    output_path = os.path.join(output_base, f"{group_name}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(group_info, f, indent=2, ensure_ascii=False)

    print(f"生成组文件: {output_path}")
