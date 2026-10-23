#!/usr/bin/env python3
"""Conservative, dependency-free structural audit for PPTX files.

This does not replace opening the deck or reviewing its rendered slides.
"""

import argparse
import posixpath
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PR = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"p": P, "a": A, "r": R, "pr": PR}
PLACEHOLDER = re.compile(r"(?i)\b(?:TODO|TBD|lorem ipsum)\b|待补充|占位符|\[\s*(?:填写|填入)[^\]]{0,30}\]")


def inspect(path: Path):
    findings = []

    def add(level, where, message):
        findings.append((level, where, message))

    try:
        with zipfile.ZipFile(path) as archive:
            damaged = archive.testzip()
            if damaged:
                add("问题", "文件", f"ZIP 成员损坏：{damaged}")
                return 0, findings, True
            names = set(archive.namelist())
            required = {"[Content_Types].xml", "ppt/presentation.xml", "ppt/_rels/presentation.xml.rels"}
            missing = required - names
            if missing:
                add("问题", "文件", f"缺少核心成员：{', '.join(sorted(missing))}")
                return 0, findings, True

            def xml(name):
                try:
                    return ET.fromstring(archive.read(name))
                except (KeyError, ET.ParseError) as exc:
                    raise ValueError(f"{name} 无法解析：{exc}") from exc

            presentation = xml("ppt/presentation.xml")
            rels = xml("ppt/_rels/presentation.xml.rels")
            size = presentation.find("p:sldSz", NS)
            if size is None:
                add("问题", "文件", "缺少幻灯片尺寸")
                return 0, findings, True
            try:
                width, height = int(size.attrib["cx"]), int(size.attrib["cy"])
                if width <= 0 or height <= 0:
                    raise ValueError("非正数")
            except (KeyError, ValueError):
                add("问题", "文件", "幻灯片尺寸无效")
                return 0, findings, True

            targets = {r.attrib.get("Id"): r.attrib.get("Target", "") for r in rels.findall("pr:Relationship", NS)}
            ids = presentation.findall("p:sldIdLst/p:sldId", NS)
            if not ids:
                add("问题", "文件", "演示文稿没有幻灯片")
            for index, slide_id in enumerate(ids, 1):
                where = f"第 {index} 页"
                relationship = slide_id.attrib.get(f"{{{R}}}id")
                target = targets.get(relationship)
                if not target or "://" in target:
                    add("问题", where, "找不到有效的幻灯片关系")
                    continue
                member = posixpath.normpath(posixpath.join("ppt", target.lstrip("/"))) if not target.startswith("/") else target.lstrip("/")
                if member not in names or not member.startswith("ppt/slides/"):
                    add("问题", where, f"幻灯片成员缺失或位置异常：{member}")
                    continue
                slide = xml(member)
                texts = [el.text or "" for el in slide.findall(".//a:t", NS)]
                joined = " ".join(texts)
                if PLACEHOLDER.search(joined):
                    add("警告", where, "发现疑似占位文字，请人工确认")
                visible = bool(joined.strip() or slide.findall(".//p:pic", NS) or slide.findall(".//p:graphicFrame", NS))
                if not visible:
                    add("警告", where, "疑似空白页；装饰形状或有意留白可能属正常")

                # Only inspect top-level objects with simple absolute transforms.
                shape_tree = slide.find("p:cSld/p:spTree", NS)
                if shape_tree is None:
                    add("问题", where, "缺少形状树")
                    continue
                for obj in shape_tree:
                    if obj.tag == f"{{{P}}}sp" or obj.tag == f"{{{P}}}pic":
                        transform = obj.find("p:spPr/a:xfrm", NS)
                    elif obj.tag == f"{{{P}}}graphicFrame":
                        transform = obj.find("p:xfrm", NS)
                    else:
                        continue
                    if transform is None:
                        continue
                    off, ext = transform.find("a:off", NS), transform.find("a:ext", NS)
                    if off is None or ext is None:
                        continue
                    try:
                        x, y = int(off.attrib["x"]), int(off.attrib["y"])
                        w, h = int(ext.attrib["cx"]), int(ext.attrib["cy"])
                    except (KeyError, ValueError):
                        add("警告", where, "对象位置或尺寸无法解析")
                        continue
                    if w < 0 or h < 0:
                        add("警告", where, "对象尺寸为负数")
                    # A one-percent margin avoids noisy reports from small design bleeds.
                    if x < -width // 100 or y < -height // 100 or x + w > width * 1.01 or y + h > height * 1.01:
                        add("警告", where, "对象可能越出页面；请渲染后核对")
            return len(ids), findings, False
    except (OSError, zipfile.BadZipFile, ValueError) as exc:
        add("问题", "文件", f"无法完成 PPTX 解析：{exc}")
        return 0, findings, True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", type=Path, help="待检查的 PPTX 文件")
    args = parser.parse_args()
    count, findings, invalid = inspect(args.pptx)
    print(f"文件：{args.pptx}\n幻灯片：{count} 页")
    if findings:
        for level, where, message in findings:
            print(f"[{level}] {where}：{message}")
    else:
        print("未发现脚本可识别的结构问题。仍须实际打开并检查视觉与科学内容。")
    if invalid:
        return 2
    return 1 if any(level == "问题" for level, _, _ in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
