import os

from common.xml.simple_parser import SimpleParser

this_dir = os.path.dirname(os.path.realpath(__file__))


class TestSimpleParser:
    """ Test SimpleParser. """
    XML_FILEPATH = os.path.join(this_dir, 'files', 'simple.xml')
    NAMESPACE = "{http://schemas.microsoft.com/sqlserver/reporting/2008/01/reportdefinition}"

    def setup_method(self):
        self.parser = SimpleParser(self.XML_FILEPATH)

    def test_ns(self):
        """ Should attach the schema as namespace to the name. """
        namespaced = self.parser.ns("Something")
        assert namespaced == f"{self.NAMESPACE}Something"

    def test_find_descendant(self):
        """ Should return the first descendant of a given name. """
        node = self.parser.find_descendant('TablixBody')
        assert node.attrib['Name'] == 'first'

    def test_find_descendants(self):
        """ Should return all descendants of a given name. """
        names = [node.attrib['Name'] for node in self.parser.find_descendants('TablixBody')]
        assert names == ['first', 'last']

    def test_deepest_descendant(self):
        """ Should return the deepest nested descendant of a given name. """
        deep_node = self.parser.deepest_descendant('TablixBody')
        assert deep_node.attrib['Name'] == 'last'
