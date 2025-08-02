import os
import re
import json

checker_file = r"C:\Poorcomputer\Study\软件所实习\静态分析工具规则知识图谱\infer-main\infer-main\infer\src\base\Checker.ml"
src_root_dir = r"C:\Poorcomputer\Study\软件所实习\静态分析工具规则知识图谱\infer-main\infer-main\infer\src"
test_base_dir = r"C:\Poorcomputer\Study\软件所实习\静态分析工具规则知识图谱\infer-main\infer-main\infer\tests\codetoanalyze"
output_root_dir = r"C:\Poorcomputer\Study\软件所实习\静态分析工具规则知识图谱\infer\Rule formation\checkers"

os.makedirs(output_root_dir, exist_ok=True)

with open(checker_file, encoding="utf-8") as f:
    content = f.read()

# 提取每个规则的内容
pattern = re.compile(r"\|\s*(\w+)\s*->\s*\{(.*?)(?=^\s*\| |\Z)", re.DOTALL | re.MULTILINE)
matches = pattern.findall(content)

def count_loc(code: str) -> int:
    return len([line for line in code.strip().splitlines() if line.strip() and not line.strip().startswith(';')])

def count_branches(code: str) -> int:
    return len(re.findall(r"\b(if|match|function|try|when|&&|\|\|)\b", code))

def count_apis(code: str) -> int:
    return len(re.findall(r"\b\w+\s*\(", code))

def extract_test_info(rule_name):
    result = []

    # 移除规则名后缀的 "checker"（不区分大小写）
    rule_base = re.sub(r'checker$', '', rule_name, flags=re.IGNORECASE).lower()

    for lang_folder in ["c", "cpp", "java", "python"]:
        lang_path = os.path.join(test_base_dir, lang_folder)
        if not os.path.isdir(lang_path):
            continue

        for subdir in os.listdir(lang_path):
            if subdir.lower() == rule_base:
                rule_test_path = os.path.join(lang_path, subdir)
                file_ext = {
                    "c": ".c",
                    "cpp": ".cpp",
                    "java": ".java",
                    "python": ".py"
                }[lang_folder]

                # 递归遍历 rule_test_path 下所有文件
                for root, _, files in os.walk(rule_test_path):
                    for file in files:
                        if file.endswith(file_ext):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, encoding='utf-8') as f:
                                    code = f.read()
                            except:
                                continue

                            func_count = len(re.findall(
                                r'\b(def|void|int|float|char|double|boolean|public|private|static|class)\b', code))

                            result.append({
                                "testname": file,
                                "testlanguage": "c++" if lang_folder == "cpp" else lang_folder,
                                "expected-problems": func_count,
                                "code": code
                            })

    return result




def find_rule_ml_path(rule_name: str, root_dir: str) -> tuple[str, str] or tuple[None, None]:
    """
    遍历 root_dir 子目录，寻找名为 rule_name.ml 的文件
    返回 (规则文件完整路径, 规则文件所在文件夹名) ，找不到返回 (None, None)
    """
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower() == f"{rule_name.lower()}.ml":
                folder_name = os.path.basename(dirpath)
                return os.path.join(dirpath, filename), folder_name
    return None, None

for rule_name, rule_body in matches:
    languages = []
    # 匹配支持语言
    support_match = re.search(r"support\s*=\s*mk_support_func\s*~([^)]*)\)", rule_body)
    if support_match:
        lang_str = support_match.group(1)
        for lang in ["clang", "java", "erlang", "hack", "python"]:
            if f"{lang}:" in lang_str:
                languages.append(lang)

    # 匹配描述
    desc_match = re.search(r'short_documentation\s*=\s*"([^"]+)"', rule_body)
    description = desc_match.group(1) if desc_match else ""

    # 初始化统计数据
    loc = branches = apis = 0

    # 查找规则对应的 ml 文件及所在文件夹名
    rule_ml_path, folder_name = find_rule_ml_path(rule_name, src_root_dir)
    if rule_ml_path and os.path.isfile(rule_ml_path):
        with open(rule_ml_path, encoding="utf-8") as rf:
            rule_code = rf.read()
            loc = count_loc(rule_code)
            branches = count_branches(rule_code)
            apis = count_apis(rule_code)
    else:
        folder_name = "unknown"


    # 构造输出目录，确保存在
    output_dir = os.path.join(output_root_dir, folder_name)
    os.makedirs(output_dir, exist_ok=True)

    # 生成 JSON 数据
    json_data = {
        "name": rule_name,
        "language": languages,
        "description": description,
        "example": None,
        "cwe": None,
        "cwe-description": None,
        "checker-language": "OCaml",
        "loc": loc,
        "branches": branches,
        "apis": apis,
        "test": extract_test_info(rule_name)
    }

    # 保存 JSON 文件
    output_path = os.path.join(output_dir, f"{rule_name}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

print(f"共提取 {len(matches)} 个规则，已写入至 {output_root_dir}")
