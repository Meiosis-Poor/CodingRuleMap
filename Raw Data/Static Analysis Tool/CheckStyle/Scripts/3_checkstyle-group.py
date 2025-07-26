import os
import json
import xml.etree.ElementTree as ET

def create_checkstyle_group_json(meta_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # 先处理顶层无分组的 xml 文件，归为 bestpractice 组
    bestpractice_rules = []
    for f in os.listdir(meta_dir):
        if f.endswith(".xml") and os.path.isfile(os.path.join(meta_dir, f)):
            xml_path = os.path.join(meta_dir, f)
            try:
                tree = ET.parse(xml_path)
                root = tree.getroot()
                module = root.find("module")
                check = module.find("check") if module is not None else None
                name = check.attrib.get("name") if check is not None else None
                if name:
                    bestpractice_rules.append(name)
            except Exception as e:
                print(f"⚠️ Error parsing {xml_path}: {e}")

    if bestpractice_rules:
        group_json = {
            "name": "bestpractice",
            "description": None,
            "rules": sorted(bestpractice_rules)
        }
        output_path = os.path.join(output_dir, "bestpractice.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(group_json, f, indent=2, ensure_ascii=False)
        print(f"✅ Wrote group: {output_path}")

    # 再处理各个子文件夹（分组）
    for item in os.listdir(meta_dir):
        item_path = os.path.join(meta_dir, item)
        if os.path.isdir(item_path):
            rule_names = []
            for rule_file in os.listdir(item_path):
                if not rule_file.endswith(".xml"):
                    continue
                xml_path = os.path.join(item_path, rule_file)
                try:
                    tree = ET.parse(xml_path)
                    root = tree.getroot()
                    module = root.find("module")
                    check = module.find("check") if module is not None else None
                    name = check.attrib.get("name") if check is not None else None
                    if name:
                        rule_names.append(name)
                except Exception as e:
                    print(f"⚠️ Error parsing {xml_path}: {e}")

            if rule_names:
                group_json = {
                    "name": item,
                    "description": None,
                    "rules": sorted(rule_names)
                }
                output_path = os.path.join(output_dir, f"{item}.json")
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(group_json, f, indent=2, ensure_ascii=False)
                print(f"✅ Wrote group: {output_path}")

if __name__ == "__main__":
    create_checkstyle_group_json(
        meta_dir=r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\checkstyle-master\src\main\resources\com\puppycrawl\tools\checkstyle\meta\checks",
        output_dir=r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\checkstyle_analysis\groups\checkstyle-java"
    )

