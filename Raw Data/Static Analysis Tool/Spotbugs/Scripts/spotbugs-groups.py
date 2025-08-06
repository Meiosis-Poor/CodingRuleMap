import os
import json

# 源路径（规则实现路径）
base_path = r"C:\Poorcomputer\Study\Github\spotbugs\spotbugs\src\main\java\edu\umd\cs\findbugs"

# 输出路径（保存 group json 的地方）
output_dir = r"C:\Poorcomputer\Study\Github\CodingRuleMap\Raw Data\Static Analysis Tool\Spotbugs\Rule Information\groups"
os.makedirs(output_dir, exist_ok=True)

# 所有组的规则字典
groups = {}

# 遍历所有 java 文件
for root, _, files in os.walk(base_path):
    for file in files:
        if not file.endswith(".java"):
            continue

        full_path = os.path.join(root, file)
        rel_path = os.path.relpath(full_path, base_path)
        parts = rel_path.split(os.sep)

        if len(parts) == 1:
            group_name = "findbug"
        else:
            group_name = parts[0]

        rule_name = os.path.splitext(file)[0]

        if group_name not in groups:
            groups[group_name] = []

        groups[group_name].append(rule_name)

# 写入每个组为单独 json
for group_name, rule_list in groups.items():
    group_json = {
        "name": group_name,
        "description": None,
        "rules": sorted(rule_list)
    }

    output_path = os.path.join(output_dir, f"{group_name}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(group_json, f, indent=2, ensure_ascii=False)

print("所有 group 信息已提取完成")
