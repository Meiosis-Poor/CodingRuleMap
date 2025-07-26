import os
import re
import json
from pathlib import Path

# 你在这里填写语言列表（文件夹名）
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

base_repo = Path(r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\codeql-main")
output_root = Path(r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\codeql_analysis\checkers")


# 清洗文件名，替换非法字符
def sanitize_filename(name):
    # 替换非法字符（如 :, *, ?, ", <, >, |, /, \）为合法字符（如 _）
    return re.sub(r'[<>:"/\\|?*]', '_', name)


def is_valid_rule(file_content):
    return re.search(r"@kind\s+(problem|path-problem)", file_content) is not None


def extract_meta_info(file_content):
    def find_tag(tag):
        match = re.search(rf"@{tag}\s+(.*)", file_content)
        return match.group(1).strip() if match else None

    return {
        "name": find_tag("name"),
        "description": find_tag("description"),
        "cwe": find_tag("tags") if re.search(r"external/cwe", file_content) else None,
        "cwe-description": None
    }


def count_effective_lines(code):
    lines = code.splitlines()
    effective = []
    in_block_comment = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("/*"):
            in_block_comment = True
        if not in_block_comment and not stripped.startswith("//"):
            effective.append(stripped)
        if "*/" in stripped:
            in_block_comment = False
    return len(effective)


def count_branches_and_apis(code):
    branches = len(re.findall(r"\b(if|for|while|switch|case)\b", code))
    apis = len(re.findall(r"\w+\s*\(", code))
    return branches, apis

def extract_test_info(expected_file_path, rule_folder):
    """
    解析 .expected 文件，生成 test 数组，code 字段为对应 .cpp 测试文件完整内容字符串
    """
    test_info = []
    try:
        with open(expected_file_path, encoding="utf-8") as f:
            lines = f.readlines()

        # 找到与 .expected 文件同名前缀的 cpp 文件
        expected_stem = expected_file_path.stem  # 比如 cwmf
        cpp_file = None
        for ext in ['.cpp', '.c', '.cc']:
            candidate = rule_folder / (expected_stem + ext)
            if candidate.exists():
                cpp_file = candidate
                break

        # 读取cpp文件完整内容
        code_content = ""
        if cpp_file is not None:
            with open(cpp_file, encoding="utf-8") as fcpp:
                code_content = fcpp.read()

        for line in lines:
            line = line.strip()
            if not line.startswith("|") or line.count("|") < 5:
                continue
            parts = line.split("|")
            if len(parts) < 2:
                continue
            location_str = parts[1].strip()  # 例如 cwmf.cpp:8:3:9:12
            description = ""

            # 解析所有行号数字
            nums = re.findall(r":(\d+)", location_str)
            linenos = list(set(int(n) for n in nums))  # 去重

            test_info.append({
                "description": description,
                "expected-problems": 1,
                "expected-linenumbers": sorted(linenos),
                "code": code_content
            })

    except Exception as e:
        print(f"跳过无法解析的文件: {expected_file_path}, 错误: {e}")
        return []

    return test_info

def process_language(language):
    src_path = base_repo / language / "ql" / "src"
    output_path = output_root / f"codeql-{language}"
    output_path.mkdir(parents=True, exist_ok=True)

    for group_dir in src_path.iterdir():
        if not group_dir.is_dir():
            continue

        group_name = group_dir.name
        group_output_dir = output_path / group_name
        group_output_dir.mkdir(parents=True, exist_ok=True)

        # 查找所有的 .ql 文件
        for ql_file in group_dir.rglob("*.ql"):
            try:
                with open(ql_file, encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                print(f"跳过无法读取的文件: {ql_file}, 错误: {e}")
                continue

            if not is_valid_rule(content):
                continue

            meta = extract_meta_info(content)
            meta.update({
                "language": language,
                "checker-language": "ql",
                "example": None,
                "loc": count_effective_lines(content),
                "test": []
            })
            meta["branches"], meta["apis"] = count_branches_and_apis(content)

            # 获取规则名：规则名即 .ql 文件所在的文件夹名称
            rule_name = ql_file.stem  # 规则名为文件名，不包含扩展名

            # 查找测试用例文件夹（与规则同名的文件夹）
            rule_folder = base_repo / language / "ql" / "test" / "query-tests" / group_name
            rule_test_folder = None

            for subfolder in rule_folder.rglob(rule_name):
                if subfolder.is_dir():
                    rule_test_folder = subfolder
                    break

            if rule_test_folder:
                expected_file_path = rule_test_folder / "cwmf.expected"
                if expected_file_path.exists():
                    test_info = extract_test_info(expected_file_path, rule_test_folder)
                    meta["test"] = test_info

            # 保存为对应规则名的JSON文件
            rule_filename = f"{rule_name}.json"  # 使用规则名生成文件名
            rule_path = group_output_dir / rule_filename
            with open(rule_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2, ensure_ascii=False)

# 主调度逻辑
for lang in languages:
    print(f"处理语言：{lang}")
    process_language(lang)

print("所有规则已处理完成。")


