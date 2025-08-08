import os
import json

base_dir = r"C:\Poorcomputer\Study\Github\sonarqube\sonar-core\src\main\java\org\sonar\core"  # 规则根目录
output_dir = r"C:\Poorcomputer\Study\Github\CodingRuleMap\Raw Data\Static Analysis Tool\Sonarqube\Rule Information\groups"  # 输出路径

def extract_groups(base_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for group_name in os.listdir(base_dir):
        group_path = os.path.join(base_dir, group_name)
        if not os.path.isdir(group_path):
            continue

        rules = []
        for filename in os.listdir(group_path):
            if filename == "package-info.java":
                continue
            if os.path.isfile(os.path.join(group_path, filename)):
                rule_name, ext = os.path.splitext(filename)
                rules.append(rule_name)

        group_json = {
            "name": group_name,
            "description": None,
            "rules": sorted(rules)
        }

        output_path = os.path.join(output_dir, f"{group_name}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(group_json, f, indent=2, ensure_ascii=False)
        print(f"Saved group '{group_name}' with {len(rules)} rules.")

if __name__ == "__main__":
    extract_groups(base_dir, output_dir)