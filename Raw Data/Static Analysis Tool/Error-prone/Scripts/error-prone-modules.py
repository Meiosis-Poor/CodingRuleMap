import os
import json

base_dir = r"C:\Poorcomputer\Study\Github\error-prone\core\src\main\java\com\google\errorprone\bugpatterns"
output_base = r"C:\Poorcomputer\Study\Github\CodingRuleMap\Raw Data\Static Analysis Tool\Error-prone\Rule Information\modules"
modules_json_path = os.path.join(output_base, "modules.json")

def is_rule_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            return '@BugPattern' in content
    except:
        return False

groups = []

# 检查根目录是否有规则文件
root_rules = []
for f in os.listdir(base_dir):
    full_path = os.path.join(base_dir, f)
    if f.endswith(".java") and is_rule_file(full_path):
        root_rules.append(f)
if root_rules:
    groups.append("bugpatterns")

# 遍历一级子目录，判断是否为规则组
for entry in os.listdir(base_dir):
    full_path = os.path.join(base_dir, entry)
    if os.path.isdir(full_path):
        has_rule = False
        for f in os.listdir(full_path):
            if f.endswith(".java") and is_rule_file(os.path.join(full_path, f)):
                has_rule = True
                break
        if has_rule:
            groups.append(entry)

modules_info = {
    "artifactId": "errorprone-java",
    "name": "error-prone",
    "modelVersion": None,
    "groups": sorted(groups)
}

os.makedirs(output_base, exist_ok=True)
with open(modules_json_path, "w", encoding="utf-8") as f:
    json.dump(modules_info, f, indent=2, ensure_ascii=False)

print(f"生成 modules 文件: {modules_json_path}")
