import os
import json

base_dir = r"C:\Poorcomputer\Study\Github\sonarqube\sonar-core\src\main\java\org\sonar\core"  # 规则根目录
output_dir = r"C:\Poorcomputer\Study\Github\CodingRuleMap\Raw Data\Static Analysis Tool\Sonarqube\Rule Information\modules\modules.json"  # 输出路径

def extract_sonarqube_modules(base_dir, output_path):
    modules = []
    for item in os.listdir(base_dir):
        full_path = os.path.join(base_dir, item)
        if os.path.isdir(full_path):
            modules.append(item)

    modules.sort()

    result = {
        "artifactId": "sonarqube",
        "name": "sonarqube",
        "modelVersion": None,
        "groups": modules  # 这里用 groups 字段存模块列表，格式你可以根据需要改
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"SonarQube模块信息已保存到：{output_path}")

if __name__ == "__main__":
    extract_sonarqube_modules(base_dir, output_dir)
