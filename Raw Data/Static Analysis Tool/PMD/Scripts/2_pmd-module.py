import os
import json
import xml.etree.ElementTree as ET

# 命名空间处理（Maven pom.xml 默认命名空间）
ns = {'m': 'http://maven.apache.org/POM/4.0.0'}

a = r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\pmd_main"
b = r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\pmd_analyze\main\pmd_modules.json"

# 读取 pmd_modules.json 文件
with open(b, "r", encoding="utf-8") as f:
    module_json = json.load(f)

module_list = module_json.get("module", [])

for module_name in module_list:
    module_path = os.path.join(a, module_name)
    pom_path = os.path.join(module_path, "pom.xml")

    # 检查 pom.xml 是否存在
    if not os.path.exists(pom_path):
        print(f"⚠️  跳过模块 {module_name}：找不到 pom.xml")
        continue

    # 解析 pom.xml
    try:
        tree = ET.parse(pom_path)
        root = tree.getroot()
        artifact_id = root.find("m:artifactId", ns)
        model_version = root.find("m:modelVersion", ns)
        name_elem = root.find("m:name", ns)

        # 处理空值
        artifact_id = artifact_id.text if artifact_id is not None else ""
        model_version = model_version.text if model_version is not None else ""
        name = name_elem.text if name_elem is not None else ""
    except Exception as e:
        print(f"❌ 解析 pom.xml 失败：{pom_path}，错误：{e}")
        continue

    # 找规则组（查找 category 下 .xml 文件）
    category_dir = os.path.join(module_path, "src", "main", "resources", "category")
    group_names = []

    if os.path.exists(category_dir):
        for root_dir, dirs, files in os.walk(category_dir):
            for file in files:
                if file.endswith(".xml"):
                    group_name = os.path.splitext(file)[0]  # 去除 .xml 扩展名
                    group_names.append(group_name)
    else:
        print(f"⚠️  模块 {module_name} 没有 category 目录，可能无规则组")

    # 如果 group 为空则跳过
    if not group_names:
        print(f"⏭️  模块 {module_name} 无规则组，跳过生成 json")
        continue

    # 构造结果
    module_info = {
        "artifactId": artifact_id,
        "name": name,
        "modelVersion": model_version,
        "groups": group_names
    }

    # 写入 JSON 文件
    output_path = r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\pmd_analyze\modules"
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, f"{module_name}.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(module_info, f, indent=2, ensure_ascii=False)

    print(f"✅ 已生成模块信息文件：{output_file}")
