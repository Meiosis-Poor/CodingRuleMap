import os
import re
import json

checker_ml_path = r"C:\Poorcomputer\Study\软件所实习\静态分析工具规则知识图谱\infer-main\infer-main\infer\src\base\Checker.ml"
src_root_dir = r"C:\Poorcomputer\Study\软件所实习\静态分析工具规则知识图谱\infer-main\infer-main\infer\src"
output_json_path = r"C:\Poorcomputer\Study\软件所实习\静态分析工具规则知识图谱\infer\Rule formation\modules\infer-modules.json"

pattern = re.compile(r"\|\s*(\w+)\s*->\s*\{", re.MULTILINE)
with open(checker_ml_path, "r", encoding="utf-8") as f:
    content = f.read()

rule_names = pattern.findall(content)
print(f"共提取规则数量: {len(rule_names)}")

file_index = {}
for root, dirs, files in os.walk(src_root_dir):
    for file in files:
        if file.lower().endswith(".ml"):
            name_without_ext = file[:-3].lower()
            folder_name = os.path.basename(root)
            file_index[name_without_ext] = folder_name

groups_set = set()
for rule in rule_names:
    rule_lower = rule.lower()
    group = file_index.get(rule_lower)
    if group:
        groups_set.add(group)

groups_list = sorted(groups_set)
print(f"找到规则组数量: {len(groups_list)}")

summary = {
    "artifactId": "infer",
    "name": "infer",
    "modelVersion": None,
    "groups": groups_list,
}

os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
with open(output_json_path, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

print(f"规则组汇总已保存到：{output_json_path}")
