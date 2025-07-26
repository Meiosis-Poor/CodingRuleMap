import os
import json
import xml.etree.ElementTree as ET

# 命名空间处理（Maven pom.xml 默认命名空间）
ns = {'m': 'http://maven.apache.org/POM/4.0.0'}

# Checkstyle 根目录路径
checkstyle_path = r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\checkstyle-master"
pom_path = os.path.join(checkstyle_path, "pom.xml")

# meta/checks 路径（存放 checker 描述 XML 文件）
checks_meta_path = os.path.join(
    checkstyle_path,
    "src", "main", "resources",
    "com", "puppycrawl", "tools", "checkstyle", "meta", "checks"
)

# 提取 pom.xml 中的 name 和 modelVersion
try:
    tree = ET.parse(pom_path)
    root = tree.getroot()

    def get_text(tag):
        elem = root.find(f"m:{tag}", ns)
        return elem.text.strip() if elem is not None else ""

    name = get_text("name")
    model_version = get_text("modelVersion")

except Exception as e:
    print(f"❌ 解析 pom.xml 失败：{e}")
    exit(1)

# 获取规则组名（子文件夹 + bestpractice）
group_names = []

if not os.path.exists(checks_meta_path):
    print(f"❌ 未找到 checker 描述路径：{checks_meta_path}")
    exit(1)

# 子文件夹视为分组
for entry in os.scandir(checks_meta_path):
    if entry.is_dir():
        group_names.append(entry.name)

# 检查是否存在直接放在 checks/ 目录下的 .xml 文件
has_top_level_xml = any(
    file.endswith(".xml") for file in os.listdir(checks_meta_path)
    if os.path.isfile(os.path.join(checks_meta_path, file))
)
if has_top_level_xml:
    group_names.append("bestpractice")  # 加入默认组名

# 构造结果
module_info = {
    "artifactId": "checkstyle-java",
    "name": name,
    "modelVersion": model_version,
    "groups": sorted(group_names)
}

# 写入 JSON 文件
output_dir = r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\checkstyle_analysis\modules"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "checkstyle-java.json")

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(module_info, f, indent=2, ensure_ascii=False)

print(f"✅ 已生成 Checkstyle 模块信息文件：{output_file}")

