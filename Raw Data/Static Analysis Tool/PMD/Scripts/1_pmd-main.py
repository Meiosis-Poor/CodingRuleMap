import os
import xml.etree.ElementTree as ET
import json

# 指定你的 PMD 根目录路径（这里留空给你填写）
a = r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\pmd_main"

# 最终结果结构
result = {
    "artifactId": "pmd",
    "groupId": "net.sourceforge.pmd",
    "version": "7.15.0-SNAPSHOT",
    "module": []
}

# 命名空间解析器（Maven pom.xml 通常使用该命名空间）
ns = {'m': 'http://maven.apache.org/POM/4.0.0'}

# 遍历 a 文件夹下的所有以 "pmd-" 开头的目录
for item in os.listdir(a):
    subdir_path = os.path.join(a, item)
    if os.path.isdir(subdir_path) and item.startswith("pmd-"):
        pom_path = os.path.join(subdir_path, "pom.xml")
        if os.path.exists(pom_path):
            try:
                tree = ET.parse(pom_path)
                root = tree.getroot()
                artifact_id_elem = root.find("m:artifactId", ns)
                if artifact_id_elem is not None:
                    result["module"].append(artifact_id_elem.text)
            except Exception as e:
                print(f"❌ 解析失败：{pom_path}，原因：{e}")

# 保存结果为 JSON 文件
output_path = r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\pmd_analyze\main\pmd_modules.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"✅ 生成成功：{output_path}")

