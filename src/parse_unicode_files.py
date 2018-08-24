import json
import argparse
from pathlib import Path
from xml.etree import ElementTree
from collections import defaultdict

import metadata


def parse_ldml_annotation(filepath):
    ldml_file = Path(filepath)

    tree = ElementTree.parse(ldml_file)
    root = tree.getroot()

    emoji_dict = defaultdict(dict)
    for annotation in root[1]:
        emoji = annotation.get("cp")

        if emoji in metadata.emoji_modifier:
            continue

        if annotation.get("type"):
            short_name = annotation.text
            emoji_dict[emoji]["short_name"] = short_name
        else:
            keywords = [s.strip() for s in annotation.text.split("|")]
            emoji_dict[emoji]["keywords"] = keywords
    return emoji_dict


def parse_emoji_test(filepath, translate=True):
    emoji_dict = {}
    with open(filepath) as f:
        group_name = ""
        subgroup_name = ""
        for line in f:
            if "# group" in line:
                group_name = line.split(":")[-1].strip()
                subgroup_name = ""
            if "# subgroup:" in line:
                subgroup_name = line.split(":")[-1].strip()

            if line[0] == "#" or line.strip() == "":
                continue

            codepoints = line.split(";")[0].strip()
            if " " in codepoints:
                emoji = "".join([chr(int(c, 16)) for c in codepoints.split(" ")])
            else:
                emoji = chr(int(codepoints, 16))

            if translate:
                if group_name and group_name in metadata.group:
                    group_name = metadata.group[group_name]
                if subgroup_name and subgroup_name in metadata.subgroup:
                    subgroup_name = metadata.subgroup[subgroup_name]

            emoji_dict[emoji] = {"group": group_name, "subgroup": subgroup_name}
    return emoji_dict


def make_keyword2emoji(d):
    keyword2emoji = defaultdict(list)
    for k, v in d.items():
        for keyword in v["keywords"]:
            keyword2emoji[keyword].append(k)
    return keyword2emoji


def make_group2emoji(d):
    group2emoji = defaultdict(list)
    subgroup2emoji = defaultdict(list)
    for k, v in d.items():
        group2emoji[v["group"]].append(k)
        subgroup2emoji[v["subgroup"]].append(k)
    return {"group": group2emoji, "subgroup": subgroup2emoji}


def dump_to_json(d, filepath):
    with open(filepath, "w") as f:
        json.dump(d, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotation", type=str,  default='data/unicode/ja.xml', help='CJK Annotations file')
    parser.add_argument("--full_emoji", type=str,  default='data/unicode/emoji-test.txt', help='Full Emoji List')
    args = parser.parse_args()

    emoji_ja = parse_ldml_annotation(args.annotation)
    emoji_group = parse_emoji_test(args.full_emoji, translate=True)

    # 国旗を追加する(REGIONAL INDICATORのペア)
    for emoji, short_name in metadata.flag.items():
        if emoji in emoji_group:
            emoji_group[emoji]
            emoji_group[emoji]["short_name"] = short_name
            emoji_group[emoji]["keywords"] = metadata.flag_keyword
            emoji_ja[emoji] = emoji_group[emoji]

    # emoji_jaとemoji_groupをマージする
    output = {}
    for emoji, meta in emoji_ja.items():
        output[emoji] = meta
        if emoji in emoji_group:
            output[emoji].update(emoji_group[emoji])
        else:
            output[emoji].update({"group": "", "subgroup": ""})

    # 出力
    dump_to_json(output, "data/emoji_ja.json")
    dump_to_json(make_keyword2emoji(emoji_ja), "data/keyword2emoji_ja.json")
    dump_to_json(make_group2emoji(emoji_group), "data/group2emoji_ja.json")
