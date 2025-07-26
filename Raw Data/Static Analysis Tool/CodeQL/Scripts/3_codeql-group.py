import os
import json
from pathlib import Path

# 生成好的规则 JSON 所在目录
output_root = Path(r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\codeql_analysis\checkers")
# 要写出的“规则组索引”文件目录
groups_output_root = Path(r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\codeql_analysis\groups")
groups_output_root.mkdir(parents=True, exist_ok=True)


from typing import List

def generate_group_json(language: str, group_name: str, rule_files: List[str]) -> None:
    """
    为每个规则组生成一个 json 文件：{name, description=null, rules=[规则文件名]}
    """
    group_json_path = groups_output_root / f"codeql-{language}" / f"{group_name}.json"
    group_json_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "name": group_name,
        "description": None,          # 按要求设为 null
        "rules": rule_files           # 已是文件名（不含扩展名）
    }

    with open(group_json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"已生成规则组文件: {group_json_path}")


def process_language(language: str) -> None:
    """
    遍历 codeql-[language] 下的规则组目录，把每个组里 *.json 文件名收集为 rules 列表
    """
    lang_root = output_root / f"codeql-{language}"
    if not lang_root.exists():
        return

    for group_dir in lang_root.iterdir():
        if not group_dir.is_dir():
            continue

        group_name = group_dir.name
        rule_names: list[str] = []

        # 读取该组下所有规则 json 文件名，去掉扩展名
        for rule_path in group_dir.glob("*.json"):
            rule_names.append(rule_path.stem)   # 仅文件名，无 .json

        # 只为包含规则的组写文件
        if rule_names:
            generate_group_json(language, group_name, sorted(rule_names))


# 需要处理的语言列表
languages = [
    "cpp", "csharp", "go", "java", "javascript",
    "python", "ql", "ruby", "rust", "swift"
]

for lang in languages:
    print(f"处理语言: {lang}")
    process_language(lang)

print("全部规则组索引已生成。")

