from rich.console import RenderableType
from rich.markdown import Markdown

from xnat.core import XNATBaseObject
from xnat.mixin import ProjectData, ImageScanData, SubjectData, ImageSessionData


def create_markdown(data: XNATBaseObject) -> RenderableType:
    if isinstance(data, ProjectData):
        return create_project_markdown(data)

    if isinstance(data, SubjectData):
        markdown = ['# Subject info.', str(data)]
        return Markdown('\n'.join(markdown))

    if isinstance(data, ImageSessionData):
        markdown = ['# Experiment info.', str(data)]
        return Markdown('\n'.join(markdown))

    if isinstance(data, ImageScanData):
        return create_scandata_markdown(data)

    return Markdown('No information.')


def create_project_markdown(data: ProjectData) -> RenderableType:
    markdown = ['# Project info.']

    if data.description:  # type: ignore
        markdown.append(f'- Description: "{data.description}"')  # type: ignore

    markdown.append(f'- Name: {data.name}')  # type: ignore
    markdown.append(f'- ID: {data.id}')
    markdown.append(f'- Secondary ID: {data.secondary_id}')  # type: ignore

    if data.keywords:  # type: ignore
        keywords = [f"'{x}'" for x in data.keywords.split()]  # type: ignore
        markdown.append(f'- Keywords: {", ".join(keywords)}')

    return Markdown('\n'.join(markdown))


def create_scandata_markdown(data: ImageScanData) -> RenderableType:
    markdown = ['# Scan info.']

    markdown.extend(['|Key|Value', '|---|---|'])
    for key, value in sorted(data.data.items()):
        markdown.append(f'|{key}|{value}|')

    return Markdown('\n'.join(markdown))
