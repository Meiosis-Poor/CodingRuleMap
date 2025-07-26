import os
import json

# 输入和输出路径
base_input_dir = r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\clangtidy-main\clang-tidy"
output_dir = r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\clangtidy_analysis\groups\clangtidy-cpp"
os.makedirs(output_dir, exist_ok=True)

# 遍历每个检查器组（即文件夹）
for group_name in os.listdir(base_input_dir):
    group_path = os.path.join(base_input_dir, group_name)
    if not os.path.isdir(group_path):
        continue

    rule_names = []

    for file_name in os.listdir(group_path):
        if file_name.endswith("Check.cpp"):
            rule_base = file_name[:-9]  # 去掉 "Check.cpp"
            rule_names.append(rule_base)

    rule_names.sort()

    group_data = {
        "name": group_name,
        "description": None,
        "rules": rule_names
    }

    output_path = os.path.join(output_dir, f"{group_name}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(group_data, f, indent=2, ensure_ascii=False)

    print(f"✅ 已生成：{output_path}")
