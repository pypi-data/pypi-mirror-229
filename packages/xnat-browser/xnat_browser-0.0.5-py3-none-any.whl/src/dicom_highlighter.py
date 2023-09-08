from rich.highlighter import RegexHighlighter


class DicomHighlighter(RegexHighlighter):
    """Highlights the text produced by pydicom. """

    base_style = "repr."
    highlights = [
        r"(?P<tag_start>\()(?P<attrib_name>.{4}), (?P<attrib_value>.{4})(?P<tag_end>\)) (?P<str>.*) "
        r"(?P<none>([A-Z]{2})|([A-Z]{2}.[A-Z]{2})): (?P<number>.*)",
    ]
