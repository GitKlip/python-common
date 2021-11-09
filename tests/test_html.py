from common.html import document_to_text


class TestDocumentToText:

    HTML_DOC = str(
        '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" '
        '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\r\n'
        '<html xmlns="http://www.w3.org/1999/xhtml">\r\n'
        '<head>\r\n<meta http-equiv="Content-Type" content="text/html; '
        'charset=iso-8859-1"/>\r\n'
        '<title>404 - File or directory not found.</title>\r\n'
        '<style type="text/css">\r\n<!--\r\n'
        'body{margin:0;font-size:.7em;font-family:Verdana, Arial, Helvetica, sans-serif;background:#EEEEEE;}\r\n'
        'fieldset{padding:0 15px 10px 15px;} \r\nh1{font-size:2.4em;margin:0;color:#FFF;}\r\n'
        'h2{font-size:1.7em;margin:0;color:#CC0000;} \r\n'
        'h3{font-size:1.2em;margin:10px 0 0 0;color:#000000;} \r\n'
        '#header{width:96%;margin:0 0 0 0;padding:6px 2% 6px '
        '2%;font-family:"trebuchet MS", Verdana, sans-serif;color:#FFF;\r\n'
        'background-color:#555555;}\r\n#content{margin:0 0 0 2%;position:relative;}\r\n'
        '.content-container{background:#FFF;width:96%;margin-top:8px;padding:10px;position:relative;}\r\n-->\r\n'
        '</style>\r\n</head>\r\n'
        '<body>\r\n<div id="header"><h1>Server Error</h1></div>\r\n'
        '<div id="content">\r\n <div class="content-container"><fieldset>\r\n '
        '<h2>404 - File or directory not found.</h2>\r\n '
        '<h3>The resource you are looking for might have been removed, '
        'had its name changed, or is temporarily unavailable.</h3>\r\n '
        '</fieldset></div>\r\n</div>\r\n</body>\r\n</html>\r\n'
    )

    def test_document_to_text(self):
        expected = str(
            "Server Error\n "
            "404 - File or directory not found.\n "
            "The resource you are looking for might have been removed, "
            "had its name changed, or is temporarily unavailable."
        )
        assert document_to_text(self.HTML_DOC) == expected

    def test_document_to_text_single_line(self):
        expected = str(
            "Server Error 404 - File or directory not found. "
            "The resource you are looking for might have been removed, "
            "had its name changed, or is temporarily unavailable."
        )
        assert document_to_text(self.HTML_DOC, processing='single_line') == expected

    def test_document_to_text_no_processing(self):
        expected = str(
            '\nServer Error\n\n \n 404 - File or directory not found.\n '
            'The resource you are looking for might have been removed, '
            'had its name changed, or is temporarily unavailable.\n \n\n'
        )
        assert document_to_text(self.HTML_DOC, processing=None) == expected
