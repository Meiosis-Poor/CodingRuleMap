import os
import json

# 源码基础路径
base_path = r"C:\Poorcomputer\Study\Github\spotbugs\spotbugs\src\main\java\edu\umd\cs\findbugs"

# 输出模块信息 JSON 路径
output_path = r"C:\Poorcomputer\Study\Github\CodingRuleMap\Raw Data\Static Analysis Tool\Spotbugs\Rule Information\modules\modules.json"

# 初始化 set 防止重复
group_names = set()

# 遍历所有 Java 文件
for root, _, files in os.walk(base_path):
    for file in files:
        if not file.endswith(".java"):
            continue

        full_path = os.path.join(root, file)
        rel_path = os.path.relpath(full_path, base_path)
        parts = rel_path.split(os.sep)

        if len(parts) == 1:
            group_names.add("findbug")
        else:
            group_names.add(parts[0])

# 构造 modules 信息
module_info = {
    "artifactId": "spotbugs-java",
    "name": "spotbugs",
    "modelVersion": None,
    "groups": sorted(group_names)
}

# 保存 JSON
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(module_info, f, indent=2, ensure_ascii=False)

print("模块信息提取完成，输出文件为：modules.json")
