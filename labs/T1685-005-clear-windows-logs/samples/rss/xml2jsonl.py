"""Convert Windows events in XML format to JSON Lines, with the same structure
as evtx2jsonl.py (attributes under "#attributes"), for the evtx:json sourcetype.

Usage: python xml2jsonl.py <input.xml> <output.jsonl>
The input file can contain one or several <Event> elements.
"""
import json
import re
import sys
import xml.etree.ElementTree as ET


def local(tag: str) -> str:
    """Remove the XML namespace from a tag or attribute name."""
    return tag.split("}", 1)[-1]


def typed(value: str):
    """Return numbers as int, like the EVTX parser does."""
    return int(value) if value.isdigit() else value


def normalize_time(value: str) -> str:
    """Keep 7 decimals on SystemTime, like the EVTX parser, so the
    evtx:json TIME_FORMAT (%7N) also matches events exported as XML."""
    match = re.match(r"^(.*T\d{2}:\d{2}:\d{2})(?:\.(\d+))?Z$", value)
    if not match:
        return value
    decimals = (match.group(2) or "").ljust(7, "0")[:7]
    return f"{match.group(1)}.{decimals}Z"


def convert(elem: ET.Element):
    attrs = {local(k): typed(v) for k, v in elem.attrib.items()}
    if "SystemTime" in attrs:
        attrs["SystemTime"] = normalize_time(attrs["SystemTime"])
    children = list(elem)
    text = (elem.text or "").strip()

    if not children:
        if attrs and text:
            return {"#attributes": attrs, "#text": typed(text)}
        if attrs:
            return {"#attributes": attrs}
        return typed(text) if text else None

    node = {"#attributes": attrs} if attrs else {}
    for child in children:
        name = local(child.tag)
        # <Data Name="X">value</Data> becomes "X": value, as in the EVTX parser
        if name == "Data" and "Name" in child.attrib:
            value = (child.text or "").strip()
            node[child.attrib["Name"]] = typed(value) if value else None
            continue
        value = convert(child)
        if name in node:
            if not isinstance(node[name], list):
                node[name] = [node[name]]
            node[name].append(value)
        else:
            node[name] = value
    return node


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit("Usage: python xml2jsonl.py <input.xml> <output.jsonl>")

    with open(sys.argv[1], encoding="utf-8") as f:
        content = re.sub(r"<\?xml[^>]*\?>", "", f.read())

    root = ET.fromstring(f"<Events>{content}</Events>")
    count = 0
    with open(sys.argv[2], "w", encoding="utf-8") as out:
        for event in root:
            out.write(json.dumps({"Event": convert(event)}) + "\n")
            count += 1
    print(f"{count} events written to {sys.argv[2]}")


if __name__ == "__main__":
    main()
