
import os
import redocparse.matcher as m

def namify(match: str):
    return "".join([w[0].upper() + w[1:] for w in match.split()])

import inflect
p = inflect.engine()

def make_singular(match: str):
    singular = p.singular_noun(match)
    if isinstance(singular, str): return singular
    return match

@m.Matcher()
def root():
    return f"""
from __future__ import annotations

import dataclasses as dc
import typing as t

from dubious.discord.disc import Snowflake

"""

@root.matcher(r"###### (.+?) Structure[\w\W]+?\s+\|\n\n")
def disc_class(name: str):
    return f"@dc.dataclass\nclass {name}:\n"

@disc_class.group()
def disc_name(name: str):
    return namify(name)

noneable = " | None"

field_pat = r"\| ([a-zA-Z_]+?\??)[ \\\*]+\| (.+?) +\| (.+?) +\|"
@disc_class.matcher(field_pat)
def format_field(name: str, ftype: str, desc: str):
    if not name: return ""

    if "#" in ftype:
        ftype, extra_desc = ftype.split("#")
        desc += extra_desc

    if name.endswith("?"):
        # the steps for ftype might have already added " | None"
        if not ftype.endswith(" | None"):
            ftype += " | None"
        ftype += " = dc.field(kw_only=True, default=None)"
        name = name[:-1]
    
    return f'    {name}: {ftype}\n    """ {desc} """\n\n'

@format_field.group()
def format_field_name(name: str):
    if name == "Field": name = ""
    elif name == "global": name = "_global"
    return name

@format_field.group()
def format_field_type(ftype: str):
    return ftype

format_field_type.quick_steps({
        # Raw types
        r"string": "str",
        r"(?:integer)|(?:number)": "int",
        r"double": "float",
        r"boolean": "bool",
        r"snowflake": "Snowflake",
        r"ISO8601 timestamp": "str",
        r"file contents": "Any",

        # Noneable fields (prepended or appended with "?")
        r"^\?(.+)": r"\1 | None",
        r"(.+)\?$": r"\1 | None",

        # Internal type references
        r"\[(.+?)\].*": lambda match: (
            namify(match.group(1))
        ),
        
        # Collections
        r".*?(?:[a|A]rray|[l|L]ist) of (.+)": lambda re_match: (
            f"list[{make_singular(re_match.group(1))}]"
        ),
        r".*?[m|M]ap of (.+) to (.+)": lambda re_match: (
            f"dict[{make_singular(re_match.group(1))}, {make_singular(re_match.group(2))}]"
        ),

        # Fixing 
        r"^mixed(.*)": r"t.Any# \1",
})

@format_field.group()
def format_field_desc(desc: str):
    return desc

format_field_desc.quick_steps({
    r"\[(.+?)\]\(.+\)": r"`\1`"
})


if __name__ == "__main__":

    inp: list[str] = []
    path_root = os.path.join("src/docparse/discord-api-docs", "docs")
    for folder in ["interactions", "resources"]:
        path_folder = os.path.join(path_root, folder)
        for file in os.listdir(path_folder):
            path_file = os.path.join(path_folder, file)
            with open(path_file, "r") as f:
                inp.append(f.read())
    path_topics_folder = os.path.join(path_root, "topics")
    for specific in ["OAuth2.md", "Permissions.md", "Teams.md"]:
        path_file = os.path.join(path_topics_folder, specific)
        with open(path_file, "r") as f:
            inp.append(f.read())

    with open("src/docparse/api.py", "w") as f:
        f.write(root.process("\n\n\n".join(content for content in inp)))