from html.parser import HTMLParser


class _OnlyTextInBody(HTMLParser):
    """ Captures text in the body and removes all carriage returns. """
    def __init__(self):
        self.text = ""  # required by the parser
        self.in_body = False
        super().__init__()

    def handle_data(self, data):
        if self.in_body:
            no_carriage_returns = data.replace("\r", '')
            self.text += no_carriage_returns

    def handle_starttag(self, tag, attrs):
        if tag == 'body':
            self.in_body = True

    def handle_endtag(self, tag):
        if tag == 'body':
            self.in_body = False


def document_to_text(html, processing='remove_empty_lines'):
    """ Takes an html document (so, must have `body` tags) and returns the text. """
    html_filter = _OnlyTextInBody()
    html_filter.feed(html)
    text = html_filter.text
    if processing == 'remove_empty_lines':
        return "\n".join([line for line in text.split("\n") if line.strip()])
    elif processing == 'single_line':
        return " ".join([line.strip() for line in text.split("\n") if line.strip()])
    else:
        return text
