import os
import json
import xml.etree.ElementTree as ET
import re

def extract_description_from_xml(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        module = root.find("module")
        check = module.find("check") if module is not None else None
        return check.attrib.get("name"), check.findtext("description", default="").strip()
    except Exception as e:
        print(f"❌ Failed to parse XML: {xml_path} - {e}")
        return None, None

def count_loc_branches_apis(java_path):
    loc = 0
    branches = 0
    apis = set()
    branch_keywords = {"if", "else if", "switch", "case", "for", "while", "?"}

    try:
        with open(java_path, encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
                    continue
                loc += 1
                if any(kw in stripped for kw in branch_keywords):
                    branches += 1
                apis.update(re.findall(r"(\w+)\s*\(", stripped))
    except Exception as e:
        print(f"⚠️ Error parsing Java file: {java_path} - {e}")
    return loc, branches, len(apis)

def extract_tests_from_input_java(java_file_path):
    tests = []
    try:
        with open(java_file_path, encoding='utf-8') as f:
            lines = f.readlines()

        cleaned_lines = []
        original_line_map = []

        in_block_comment = False
        for idx, line in enumerate(lines):
            stripped = line.strip()
            if in_block_comment:
                if '*/' in stripped:
                    in_block_comment = False
                continue
            if stripped.startswith("/*"):
                if '*/' not in stripped:
                    in_block_comment = True
                continue
            if not stripped or stripped.startswith("//"):
                continue
            # remove inline comments
            line = re.sub(r'//.*', '', line)
            line = re.sub(r'/\*.*?\*/', '', line)
            if line.strip():
                cleaned_lines.append(line.rstrip('\n'))
                original_line_map.append(idx)

        expected_lines = []
        for i, line in enumerate(lines):
            if "// violation" in line:
                for j in range(len(original_line_map) - 1, -1, -1):
                    if original_line_map[j] < i:
                        expected_lines.append(original_line_map[j] + 1)
                        break

        if expected_lines:
            tests.append({
                "description": f"Auto test from {os.path.basename(java_file_path)}",
                "expected-problems": len(expected_lines),
                "expected-linenumbers": expected_lines,
                "code": "\n".join(cleaned_lines)
            })
    except Exception as e:
        print(f"⚠️ Failed to extract tests from {java_file_path}: {e}")
    return tests

def build_checkstyle_checker_data(meta_dir, java_dir, test_dir, output_base):
    for group in os.listdir(meta_dir):
        group_path = os.path.join(meta_dir, group)
        if not group.endswith(".xml") and not os.path.isdir(group_path):
            continue

        if os.path.isfile(group_path):
            group_name = "bestpractice"
            xml_files = [group_path]
        else:
            group_name = group
            xml_files = [os.path.join(group_path, f) for f in os.listdir(group_path) if f.endswith(".xml")]

        for xml_path in xml_files:
            rule_name, description = extract_description_from_xml(xml_path)
            if not rule_name:
                continue

            java_subdir = os.path.join(java_dir, group_name) if group_name != "bestpractice" else java_dir
            java_file = os.path.join(java_subdir, f"{rule_name}Check.java")
            loc, branches, apis = count_loc_branches_apis(java_file) if os.path.exists(java_file) else (0, 0, 0)

            test_subdir = os.path.join(test_dir, group_name) if group_name != "bestpractice" else test_dir
            rule_test_dir = os.path.join(test_subdir, rule_name.lower())
            test_files = []

            if os.path.isdir(rule_test_dir):
                test_files = [os.path.join(rule_test_dir, f) for f in os.listdir(rule_test_dir) if f.endswith(".java")]
            else:
                for f in os.listdir(test_subdir):
                    if f.startswith(f"Input{rule_name}") and f.endswith(".java"):
                        test_files.append(os.path.join(test_subdir, f))

            tests = []
            for tf in test_files:
                tests.extend(extract_tests_from_input_java(tf))

            checker_data = {
                "name": rule_name,
                "language": "java",
                "description": description or None,
                "example": None,
                "cwe": None,
                "cwe-description": None,
                "checker-language": "java",
                "loc": loc,
                "branches": branches,
                "apis": apis,
                "test": tests
            }

            output_path = os.path.join(output_base, "checkstyle-java", group_name)
            os.makedirs(output_path, exist_ok=True)
            output_file = os.path.join(output_path, f"{rule_name}.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(checker_data, f, indent=2, ensure_ascii=False)

            print(f"✅ Wrote: {output_file}")

# === 修改为你的本地路径 ===
if __name__ == "__main__":
    build_checkstyle_checker_data(
        meta_dir=r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\checkstyle-master\src\main\resources\com\puppycrawl\tools\checkstyle\meta\checks",
        java_dir=r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\checkstyle-master\src\main\java\com\puppycrawl\tools\checkstyle\checks",
        test_dir=r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\checkstyle-master\src\test\resources\com\puppycrawl\tools\checkstyle\checks",
        output_base=r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\checkstyle_analysis\checkers"
    )
