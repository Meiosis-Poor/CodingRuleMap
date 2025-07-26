import os
import json
from pathlib import Path

# 基本路径设置
groups_root = Path(r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\codeql_analysis\groups")
modules_output_root = Path(r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\codeql_analysis\modules")

# 确保modules文件夹存在
modules_output_root.mkdir(parents=True, exist_ok=True)

def generate_module_json(language: str, groups: list) -> None:
    """
    为每个语言生成一个JSON文件，包含该语言的所有规则组。
    """
    # module的json路径
    module_json_path = modules_output_root / f"codeql-{language}.json"

    # 生成的json结构
    module_data = {
        "artifactId": f"codeql-{language}",
        "name": f"codeql-{language}",
        "modelVersion": None,
        "groups": groups
    }

    # 将json数据写入文件
    with open(module_json_path, 'w', encoding="utf-8") as f:
        json.dump(module_data, f, indent=2, ensure_ascii=False)
    print(f"已生成模块json文件：{module_json_path}")


def process_language(language: str) -> None:
    """
    处理每种语言的规则组，收集规则组并生成模块json文件。
    """
    language_groups_path = groups_root / f"codeql-{language}"

    if language_groups_path.exists() and language_groups_path.is_dir():
        groups = []
        # 读取该语言下所有规则组文件夹的json文件
        for group_file in language_groups_path.glob("*.json"):
            groups.append(group_file.stem)  # 文件名即为规则组名

        if groups:  # 如果存在规则组
            generate_module_json(language, groups)


# 处理每种语言
languages = [
    "cpp",
    "csharp",
    "go",
    "java",
    "javascript",
    "python",
    "ql",
    "ruby",
    "rust",
    "swift"
]

for language in languages:
    print(f"处理语言：{language}")
    process_language(language)

print("所有模块的JSON文件已生成。")
