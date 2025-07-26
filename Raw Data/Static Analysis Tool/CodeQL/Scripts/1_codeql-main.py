import json
from pathlib import Path

# 你在这里填写 CodeQL 支持的语言列表
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

output_path = Path(r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\codeql_analysis\main\module.json")

# 构造 JSON 数据
module_json = {
    "artifactId": "codeql",
    "groupId": None,
    "version": None,
    "module": [f"codeql-{lang}" for lang in languages]
}

# 写入 JSON 文件
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(module_json, f, indent=2, ensure_ascii=False)

print(f"✅ module.json 文件已生成于：{output_path}")
