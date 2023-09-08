"""
Unit tests for the import of existing Galaxy XML to galaxyxml.
"""
import sys
import unittest

from galaxyxml.tool.import_xml import GalaxyXmlParser

gxp = GalaxyXmlParser()
xpath = sys.argv[1] 
print('reading from', xpath)
tool = gxp.import_xml(xpath)
exml = tool.export()
print(exml)
outf = open("%s.xml" % xpath,'w')
outf.write(exml)
outf.write('\n')
outf.close()
