from __future__ import annotations

import pydantic
import yaml
import typing


class Description(typing.Dict):
    pass

class TOCSection(pydantic.BaseModel):
    head: typing.Dict[str, str]
    children: typing.Optional[typing.Dict[str, TOCSection]]
    description: typing.Optional[Description]

TOCSection.update_forward_refs()

class Link(pydantic.BaseModel):
    link: str
    name: typing.Optional[str]
    description: typing.Optional[Description]

class Item(pydantic.BaseModel):
    link: typing.Optional[str]
    name: typing.Optional[str]
    description: typing.Optional[Description]
    links: typing.Optional[typing.List[Link]]

class Section(pydantic.BaseModel):
    items: typing.Optional[typing.List[Item]]
    children: typing.Optional[typing.Dict[str, Section]]

Section.update_forward_refs()

class Document(pydantic.BaseModel):
    languages: typing.Dict[str, typing.Dict]
    head: typing.Dict[str, str]
    description: typing.Dict[str, str]
    toc: typing.Dict[str, TOCSection]
    content: typing.Dict[str, Section]

Document.update_forward_refs()

data = Document(**yaml.safe_load(open('README.yaml')))

def print_toc(toc: typing.Dict[str, TOCSection], lang: str, depth = 0):
    for name, section in toc.items():
        link = section.head[lang].replace(' ', '-')
        print(f"{depth * ' '}- [{section.head[lang]}](#{link})")
        if section.children:
            print_toc(section.children, lang, depth + 2)

def print_item(item: Item, lang: str, child = False):
    line = "" if not child else " * "
    if item.name:
        if item.link:
            line = f"[{item.name}]({item.link})"
        else:
            line = item.name
    else:
        if item.link:
            line = f"<{item.link}>"
    if item.description:
        if item.name or item.link:
            line += " - "
        line += item.description[lang]
    print(line)
    if item.links:
        for link in item.links:
            print_item(Item(**link.dict()), lang, True)


def print_content(content: typing.Dict[str, Section], toc: typing.Dict[str, TOCSection], lang: str, depth = 0):
    for name, section in content.items():
        heading = toc[name].head[lang]
        print(f"#{depth * '#'}", heading)
        print()
        for item in section.items:
            print_item(item, lang)
            print()
        if section.children:
            toc_section = toc[name].children
            print_content(section.children, toc_section, lang, depth + 1)

for lang in data.languages:
    print("#", data.head[lang])
    print()
    print(data.description[lang])
    print()
    print_toc(data.toc, lang)
    print()
    print_content(data.content, data.toc, lang)