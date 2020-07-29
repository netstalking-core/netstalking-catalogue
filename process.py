# required for self-referencing to work in pydantic models
from __future__ import annotations

# models
from typing import Dict, Optional, List
import pydantic

import yaml


class Description(Dict):
    pass

class TOCSection(pydantic.BaseModel):
    head: Dict[str, str]
    children: Optional[Dict[str, TOCSection]] = None
    description: Optional[Description]

# required because of self-referencing
TOCSection.update_forward_refs()

class Link(pydantic.BaseModel):
    link: Optional[str]
    name: Optional[str]
    description: Optional[Description]

# Item is a Link with or without child Links
class Item(Link):
    links: Optional[List[Link]]

class Section(pydantic.BaseModel):
    items: Optional[List[Item]]
    children: Optional[Dict[str, Section]] = None

# required because of self-referencing
Section.update_forward_refs()

class Document(pydantic.BaseModel):
    languages: Dict[str, Dict]
    head: Dict[str, str]
    description: Dict[str, str]
    toc: Dict[str, TOCSection]
    content: Dict[str, Section]

# required because of self-referencing
Document.update_forward_refs()


# recursively generate Table of Contents
def generate_toc(toc: Dict[str, TOCSection], lang: str, depth = 0):
    # for each section
    for name, section in toc.items():
        # prepare link by replacing spaces in header with hyphens
        link = section.head[lang].replace(' ', '-')
        # yield link as '- [HeaderName](#HeaderLink)'
        yield f"{depth * ' '}- [{section.head[lang]}](#{link})"
        # call the same for children, if any
        if section.children:
            yield from generate_toc(section.children, lang, depth + 2)


# Link(link='http', name='name', description={'lg': 'desc'}) => ' * [name](http) - desc'
# Link(name='name', description={'lg': 'desc'}) => ' * name - desc'
# Link(link='http', description={'lg': 'desc'}) => ' * <http> - desc'
# Link(link='http', name='name') => ' * [name](http)'
# `child` parameter adds two spaces, making link a sub-link of previous one
def generate_link(link: Link, lang: str, child = False):
    line = " * " if not child else "   * "
    if link.name:
        if link.link:
            line += f"[{link.name}]({link.link})"
        else:
            line += link.name
    else:
        if link.link:
            line += f"<{link.link}>"
    if link.description:
        if link.name or link.link:
            line += " - "
        line += link.description[lang]
    yield line


# generate link from itself
def generate_item(item: Item, lang: str):
    yield from generate_link(item, lang)
    # do the same for children if any
    if item.links:
        for link in item.links:
            yield from generate_link(Item(**link.dict()), lang, True)


# recursively generate contents
def generate_content(content: Dict[str, Section], toc: Dict[str, TOCSection], lang: str, depth = 0):
    # for each section
    for name, section in content.items():
        print(' - Section', name)
        # yield heading and empty line
        heading = toc[name].head[lang]
        yield f"#{depth * '#'} {heading}"
        yield ""
        # if there is description, yield it
        if toc[name].description:
            yield toc[name].description[lang]
        # yield each item
        for item in section.items:
            yield from generate_item(item, lang)
            yield ""
        # do the same for children if any
        if section.children:
            toc_section = toc[name].children
            yield from generate_content(section.children, toc_section, lang, depth + 1)


def generate_readme(document: Document, lang: str):
    # yield heading
    yield f"# {document.head[lang]}"
    yield ""
    # yield description
    yield document.description[lang]
    yield ""
    # yield table of contents
    yield from generate_toc(data.toc, lang)
    yield ""
    # yield content
    yield from generate_content(data.content, data.toc, lang)


# load Document from yaml
data = Document(**yaml.safe_load(open('README.yaml')))

# for each language
for lang in data.languages:
    print('Generating for lang', lang)
    # open i18n file
    with open(f"README.{lang}.md", 'w') as readme:
        # generate content
        for line in generate_readme(data, lang):
            # write each line
            readme.write(line + '\n')
