import re
from xml.etree import ElementTree


class SimpleParser:
    """ Simplify parsing heavily nested, single namespaced xml.

    All nodes are ElementTree nodes, so you have access to the full capability
    of ElementTree.

    Example:
        from common.xml.simple_parser import SimpleParser

        parser = SimpleParser("myfile.xml")
        some_node = parser.find_descendant("SomeNode")
        some_nodes = parser.find_descendants("SomeNode")
        deepest_node = parser.deepest_descendant("HeavilyNested")
    """
    SCHEMA_RE = r"({[^}]+})\w+"

    def __init__(self, filename):
        self.tree = ElementTree.parse(filename)
        self.root = self.tree.getroot()
        self.schema = re.search(self.SCHEMA_RE, self.root.tag)[1]

    def ns(self, name):
        """ Namespace whatever name is given.

        Example:
            parser.ns("NodeName")  # -> "{https://some.namespace}NodeName"
        """
        namespaced = f"{self.schema}{name}"
        return namespaced

    def deepest_descendant(self, name, node=None):
        """ Finds the deepest descendant of the given name.

        Example:
            dog_node = parser.deepest_descendant("Dog")

                <Dog>  # <- will skip this
                    ...
                       <Dog>  # <- will return this node
                       ...
                       </Dog>
                    ...
                </Dog>
        """
        node = self.root if node is None else node
        previous_deepest = self.find_descendant(name, node)
        deepest = True
        while deepest:
            deepest = self.find_descendant(name, previous_deepest)
            if deepest:
                previous_deepest = deepest
        return previous_deepest

    def find_descendant(self, name, node=None, many=False):
        """ Starting at the depth of the given node, searches for the first descendant node. """
        node = self.root if node is None else node
        methd = 'findall' if many else 'find'
        return getattr(node, methd)(f".//{self.ns(name)}")

    def find_descendants(self, name, node=None):
        """ Starting at the depth of the given node, searches for all descendant nodes of that name. """
        return self.find_descendant(name, node, many=True)
