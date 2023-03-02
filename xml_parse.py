import re
import xml.etree.ElementTree as ET


def getattrs(root):
    pattern = r'\{[^{}]+\}'
    ddi = {}
    elements = {}
    for el in root:
        # tag = el.tag
        tag = re.sub(pattern, '', el.tag)
        if tag in elements.keys():
            elements[tag] = 'list'
        else:
            elements[tag] = 'mono'
    for val, key in elements.items():
        if key == 'list':
            ddi[val] = []
        else:
            ddi[val] = ''

    for el in root:
        el_clean = re.sub(pattern, '', el.tag)
        eltext = ''
        if el.text:
            eltext = el.text.strip().replace('\n', '')
        if elements[el_clean] == 'list':
            if eltext == '':
                ddi[el_clean].append(getattrs(el))
            else:
                ddi[el_clean] = getattrs(el)
        else:
            if eltext == '':
                ddi[el_clean] = getattrs(el)
            else:
                ddi[el_clean] = el.text
    return ddi


def read_xml_invoices(xml_file):
    namespace = '{http://www.aade.gr/myDATA/invoice/v1.0}'
    tree = ET.parse(xml_file)
    root = tree.getroot()
    invoices = []
    for invdoc in root.findall(f'{namespace}invoicesDoc'):
        for inv in invdoc.findall(f'{namespace}invoice'):
            invoices.append(getattrs(inv))
    print(invoices)


def parse_xml_invoices(xml: str) -> list[dict]:
    namespace = '{http://www.aade.gr/myDATA/invoice/v1.0}'
    root = ET.fromstring(xml)
    invoices = []
    for invdoc in root.findall(f'{namespace}invoicesDoc'):
        for inv in invdoc.findall(f'{namespace}invoice'):
            invoices.append(getattrs(inv))
    return invoices


def parse_xml_invoice(xml: str):
    root = ET.fromstring(xml)
    return getattrs(root)


def parse_xml_books(xml: str, typ):
    namespace = '{http://www.aade.gr/myDATA/invoice/v1.0}'
    root = ET.fromstring(xml)
    docs = []
    for bookdoc in root.findall(f'{namespace}bookInfo'):
        docdict = getattrs(bookdoc)
        docdict['linetype'] = typ
        docs.append(docdict)
    return docs


def parse_response(xml: str) -> dict:
    root = ET.fromstring(xml)
    res = {}
    for resdoc in root.findall('response'):
        res = getattrs(resdoc)
    return res
