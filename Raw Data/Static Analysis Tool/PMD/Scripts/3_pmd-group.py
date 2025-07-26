import os
import json
import xml.etree.ElementTree as ET

ns = {'p': 'http://pmd.sourceforge.net/ruleset/2.0.0'}  # 命名空间

# 输入包含 pmd-java.json 的文件夹（之前 modules 生成的）
modules_dir = r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\pmd_analyze\modules"

# 设置主项目代码所在的根目录（用于构造完整路径）
main_pmd_root = r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\pmd_main"

# 输出目录
output_base = r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\pmd_analyze\groups"
os.makedirs(output_base, exist_ok=True)

# 遍历 modules_dir 下所有 .json 文件
for file_name in os.listdir(modules_dir):
    if not file_name.endswith(".json"):
        continue

    file_path = os.path.join(modules_dir, file_name)

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    artifact_id = data.get("artifactId")
    groups = data.get("groups", [])

    if not artifact_id or not groups:
        print(f"⚠️  跳过 {file_name}：artifactId 或 groups 缺失")
        continue

    # 构造输出子文件夹路径
    module_output_dir = os.path.join(output_base, artifact_id)
    os.makedirs(module_output_dir, exist_ok=True)

    # 构造当前模块下所有 group 文件路径映射（支持子目录）
    category_root = os.path.join(
        main_pmd_root,
        artifact_id,
        "src", "main", "resources", "category"
    )
    xml_path_map = {}  # key: 文件名，value: 完整路径
    for root_dir, _, files in os.walk(category_root):
        for file in files:
            if file.endswith(".xml"):
                full_path = os.path.join(root_dir, file)
                xml_path_map[file] = full_path

    for group_file in groups:
        if not group_file.endswith(".xml"):
            continue

        group_path = xml_path_map.get(group_file)

        if not group_path or not os.path.exists(group_path):
            print(f"❌ 找不到 group 文件：{group_file}（在 {artifact_id} 中）")
            continue

        try:
            tree = ET.parse(group_path)
            root = tree.getroot()

            # 获取 ruleset name 属性
            ruleset_name = root.attrib.get("name", "")

            # 获取 description 标签内容
            description_elem = root.find("p:description", ns)
            description = description_elem.text.strip() if description_elem is not None else ""

            # 获取所有 <rule name="">
            rules = []
            for rule in root.findall("p:rule", ns):  # 使用前缀p
                rule_name = rule.attrib.get("name")
                if rule_name:
                    rules.append(rule_name)

            # 构造输出内容
            group_info = {
                "name": ruleset_name,
                "description": description,
                "rules": rules
            }

            # 写出 JSON 文件
            group_json_name = group_file.replace(".xml", ".json")
            output_path = os.path.join(module_output_dir, group_json_name)

            with open(output_path, "w", encoding="utf-8") as out_f:
                json.dump(group_info, out_f, indent=2, ensure_ascii=False)

            print(f"✅ 成功写入：{output_path}")

        except Exception as e:
            print(f"❌ 解析失败：{group_path}，错误：{e}")

