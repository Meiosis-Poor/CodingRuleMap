import os
import json

# 输入路径（Cppcheck lib 目录）
cppcheck_lib_dir = r"C:\Poorcomputer\Study\Github\cppcheck\lib"

# 输出路径
output_dir = r"C:\Poorcomputer\Study\Github\CodingRuleMap\Raw Data\Static Analysis Tool\cppcheck\Rule Information\modules"
output_path = os.path.join(output_dir, "cppcheck-cpp.json")

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 获取所有 cpp 文件名作为模块名
module_names = [
    os.path.splitext(f)[0]
    for f in os.listdir(cppcheck_lib_dir)
    if f.endswith(".cpp") and f[0].islower()
]

# 构造 JSON 结构
data = {
    "artifactId": "cppcheck-cpp",
    "name": "Cppcheck",
    "modelVersion": None,
    "groups": sorted(module_names)
}

# 写入 JSON 文件
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ 已生成模块信息：{output_path}")
