import os
import json
import xml.etree.ElementTree as ET
import re
import lizard

ns = {'p': 'http://pmd.sourceforge.net/ruleset/2.0.0'}

groups_dir = r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\pmd_analysis\groups"
main_pmd_root = r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\pmd_main"
output_base = r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\pmd_analysis\checkers"
os.makedirs(output_base, exist_ok=True)

FRAMEWORK_API_KEYWORDS = [
    "net.sourceforge.pmd.lang.java.rule",
    "net.sourceforge.pmd.lang.java.ast",
]

def count_apis(java_code: str) -> int:
    imports = {
        line.strip()
        for line in java_code.splitlines()
        if line.strip().startswith("import net.sourceforge.pmd")
    }
    return len(imports)

def parse_tests(test_xml_path):
    tests = []
    if not os.path.exists(test_xml_path):
        return []
    try:
        tree = ET.parse(test_xml_path)
        root = tree.getroot()
        ns_test = {'t': 'http://pmd.sourceforge.net/rule-tests'}

        # 找所有 t:test-code
        for test_code in root.findall(".//t:test-code", ns_test):
            description = test_code.findtext("t:description", default=None, namespaces=ns_test)
            expected_problems_text = test_code.findtext("t:expected-problems", default="0", namespaces=ns_test)
            expected_linenumbers_text = test_code.findtext("t:expected-linenumbers", default="", namespaces=ns_test)
            code = test_code.findtext("t:code", default=None, namespaces=ns_test)

            expected_problems = int(expected_problems_text.strip()) if expected_problems_text.strip().isdigit() else 0
            expected_linenumbers = [int(x.strip()) for x in expected_linenumbers_text.split(",") if x.strip().isdigit()]

            tests.append({
                "description": description,
                "expected-problems": expected_problems,
                "expected-linenumbers": expected_linenumbers,
                "code": code
            })
    except Exception as e:
        print(f"❌ 解析测试文件失败：{test_xml_path}，错误：{e}")
    return tests

for module_name in os.listdir(groups_dir):
    module_path = os.path.join(groups_dir, module_name)
    if not os.path.isdir(module_path):
        continue

    language = module_name.replace("pmd-", "")

    for group_file in os.listdir(module_path):
        if not group_file.endswith(".json"):
            continue

        group_name = os.path.splitext(group_file)[0]
        group_path = os.path.join(module_path, group_file)

        try:
            with open(group_path, "r", encoding="utf-8") as f:
                group_data = json.load(f)
        except Exception:
            group_data = {}

        # 找对应 ruleset XML 文件
        xml_path = None
        candidate_dir = os.path.join(main_pmd_root, module_name, "src", "main", "resources", "category")
        for root_dir, _, files in os.walk(candidate_dir):
            for file in files:
                if file == group_file.replace(".json", ".xml"):
                    xml_path = os.path.join(root_dir, file)
                    break
            if xml_path:
                break

        if not xml_path or not os.path.exists(xml_path):
            print(f"❌ 找不到 XML 文件：{group_file} in {module_name}")
            continue

        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            for rule_elem in root.findall("p:rule", ns):
                rule_name = rule_elem.attrib.get("name", "")
                description = rule_elem.findtext("p:description", default=None, namespaces=ns)
                example_elem = rule_elem.find("p:example", ns)
                example = example_elem.text.strip() if example_elem is not None and example_elem.text else None

                # Java 源代码路径
                java_file_path = os.path.join(
                    main_pmd_root,
                    module_name,
                    "src", "main", "java",
                    "net", "sourceforge", "pmd", "lang",
                    language, "rule", group_name,
                    f"{rule_name}Rule.java"
                )

                loc = 0
                branches = 0
                apis = 0
                if os.path.exists(java_file_path):
                    try:
                        with open(java_file_path, "r", encoding="utf-8") as jf:
                            java_code = jf.read()
                        loc = java_code.count('\n') + 1
                        analysis = lizard.analyze_file(java_file_path)
                        branches = sum(func.cyclomatic_complexity for func in analysis.function_list)
                        apis = count_apis(java_code)
                    except Exception as e:
                        print(f"⚠️ 解析 Java 文件失败：{java_file_path}，错误：{e}")
                else:
                    print(f"⚠️ 找不到 Java 文件: {java_file_path}")

                # 测试 XML 文件路径
                test_xml_path = os.path.join(
                    main_pmd_root,
                    module_name,
                    "src", "test", "resources",
                    "net", "sourceforge", "pmd", "lang",
                    language, "rule", group_name,
                    "xml", f"{rule_name}.xml"
                )
                tests = parse_tests(test_xml_path)

                checker_data = {
                    "name": rule_name or None,
                    "language": language or None,
                    "description": description or None,
                    "example": example or None,
                    "cwe": None,
                    "cwe-description": None,
                    "checker-language": "java",
                    "loc": loc,
                    "branches": branches,
                    "apis": apis,
                    "test": tests or []
                }

                rule_output_dir = os.path.join(output_base, module_name, group_name)
                os.makedirs(rule_output_dir, exist_ok=True)
                output_path = os.path.join(rule_output_dir, f"{rule_name}.json")

                with open(output_path, "w", encoding="utf-8") as out_f:
                    json.dump(checker_data, out_f, indent=2, ensure_ascii=False)

                print(f"✅ 写入规则：{output_path}")

        except Exception as e:
            print(f"❌ 解析失败：{xml_path}，错误：{e}")
