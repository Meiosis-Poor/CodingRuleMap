import os
import json

# 输入路径（clang-tidy 源码目录）
clang_tidy_dir = r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\clangtidy-main\clang-tidy"

# 输出路径
output_dir = r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\clangtidy_analysis\modules"
output_path = os.path.join(output_dir, "clangtidy-cpp.json")
 
# 保证输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 获取所有子目录名（分组名）
group_names = [
    name for name in os.listdir(clang_tidy_dir)
    if os.path.isdir(os.path.join(clang_tidy_dir, name))
]

# 构造 JSON 结构
data = {
    "artifactId": "clangtidy-cpp",
    "name": "clang-tidy",
    "modelVersion": None,
    "groups": sorted(group_names)
}

# 写入 JSON 文件
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ 已生成：{output_path}")
