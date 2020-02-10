from xml.etree import ElementTree
root = ElementTree.parse("pom.xml").getroot()
c = ElementTree.Element("c")
c.text = "3"

root.insert(1, c)
ElementTree.dump(root)