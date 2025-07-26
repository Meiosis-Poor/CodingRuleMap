import xml.etree.ElementTree as ET
import json

def parse_pom(pom_path):
    tree = ET.parse(pom_path)
    root = tree.getroot()

    # 处理命名空间
    ns = {'mvn': 'http://maven.apache.org/POM/4.0.0'}
    ET.register_namespace('', ns['mvn'])

    # 获取元素
    def get_text(tag):
        elem = root.find(f"mvn:{tag}", ns)
        return elem.text.strip() if elem is not None else None

    artifact_id = get_text("artifactId")
    group_id = get_text("groupId")
    version = get_text("version")

    # 如果groupId/version在父级project中声明（<parent>标签），需要特殊处理
    if group_id is None or version is None:
        parent = root.find("mvn:parent", ns)
        if parent is not None:
            if group_id is None:
                group_elem = parent.find("mvn:groupId", ns)
                if group_elem is not None:
                    group_id = group_elem.text.strip()
            if version is None:
                version_elem = parent.find("mvn:version", ns)
                if version_elem is not None:
                    version = version_elem.text.strip()

    return {
        "artifactId": artifact_id,
        "groupId": group_id,
        "version": version,
        "module": ["checkstyle-java"]
    }

if __name__ == "__main__":
    pom_path = r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\checkstyle-master\pom.xml"  # 可根据需要修改路径
    result = parse_pom(pom_path)

    with open(r"C:\Users\nyr\Documents\GitHub\StaticAnalysisTool\checkstyle_analysis\main\checkstyle_modules.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("JSON 文件已生成")

