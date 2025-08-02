import os
import re
import json

checker_ml_path = r"C:\Poorcomputer\Study\软件所实习\静态分析工具规则知识图谱\infer-main\infer-main\infer\src\base\Checker.ml"
src_base_dir = r"C:\Poorcomputer\Study\软件所实习\静态分析工具规则知识图谱\infer-main\infer-main\infer\src"
output_dir = r"C:\Poorcomputer\Study\软件所实习\静态分析工具规则知识图谱\infer\Rule formation\groups"

# 提取所有规则名
with open(checker_ml_path, encoding='utf-8') as f:
    content = f.read()

pattern = re.compile(r"\|\s*(\w+)\s*->")
all_rules = pattern.findall(content)
rule_set = set(rule.lower() for rule in all_rules)  # 不区分大小写

group_dict = {}

# 遍历 src 下所有子目录
for dirpath, dirnames, filenames in os.walk(src_base_dir):
    group_name = os.path.basename(dirpath)
    matched_rules = []

    for file in filenames:
        if file.lower().endswith('.ml'):
            rule_candidate = os.path.splitext(file)[0].lower()
            if rule_candidate in rule_set:
                matched_rules.append(file[:-3])  # 去掉 .ml 后缀

    if matched_rules:
        group_dict[group_name] = group_dict.get(group_name, []) + matched_rules

# 保存为 json 文件
for group, rules in group_dict.items():
    group_data = {
        "name": group,
        "description": None,
        "rules": sorted(set(rules))  # 去重并排序
    }
    output_path = os.path.join(output_dir, f"{group}.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(group_data, f, indent=2, ensure_ascii=False)
