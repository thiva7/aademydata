import xml.etree.ElementTree as ET

from settings import AADE_ATTRIBUTES


def xml_taxes(parent, typ, amount, category):
    taxes = ET.SubElement(parent, "taxes")
    ET.SubElement(taxes, "taxType").text = str(typ)
    if category:
        ET.SubElement(taxes, "taxCategory").text = str(category)
    ET.SubElement(taxes, "taxAmount").text = amount


def xml_invoice_details(parent, aa, net, typ):
    det = ET.SubElement(parent, "invoiceDetails")
    ET.SubElement(det, "lineNumber").text = str(aa)
    ET.SubElement(det, "netValue").text = net
    ET.SubElement(det, "vatCategory").text = '8'
    ET.SubElement(det, "vatAmount").text = '0.00'
    xml_expenses_classification(det, typ, 'category2_6', net)
    return det


def xml_expenses_classification(parent, typ, category, amount):
    det_clas = ET.SubElement(parent, "expensesClassification")
    ET.SubElement(det_clas, "ecls:classificationType").text = typ
    ET.SubElement(det_clas, "ecls:classificationCategory").text = category
    ET.SubElement(det_clas, "ecls:amount").text = amount
    return det_clas


def xml_income_classification(parent, typ, category, amount):
    det_clas = ET.SubElement(parent, "incomeClassification")
    ET.SubElement(det_clas, "icls:classificationType").text = typ
    ET.SubElement(det_clas, "icls:classificationCategory").text = category
    ET.SubElement(det_clas, "icls:amount").text = amount
    return det_clas


def xml_invoice_summary(parent, val, held, ded, gross):
    isum = ET.SubElement(parent, "invoiceSummary")
    ET.SubElement(isum, "totalNetValue").text = val
    ET.SubElement(isum, "totalVatAmount").text = '0.00'
    ET.SubElement(isum, "totalWithheldAmount").text = held
    ET.SubElement(isum, "totalFeesAmount").text = '0.00'
    ET.SubElement(isum, "totalStampDutyAmount").text = '0.00'
    ET.SubElement(isum, "totalOtherTaxesAmount").text = '0.00'
    ET.SubElement(isum, "totalDeductionsAmount").text = ded
    ET.SubElement(isum, "totalGrossValue").text = gross
    return isum


def xml_issuer(parent, *, afm, country='GR', branch='1'):
    issuer = ET.SubElement(parent, "issuer")
    ET.SubElement(issuer, "vatNumber").text = afm
    ET.SubElement(issuer, "country").text = country
    ET.SubElement(issuer, "branch").text = branch
    return issuer


def xml_counterpart(parent, *, afm, tk, city, country=None, branch=None):
    cpa = ET.SubElement(parent, "counterpart")
    ET.SubElement(cpa, "vatNumber").text = afm
    ET.SubElement(cpa, "country").text = country or 'GR'
    ET.SubElement(cpa, "branch").text = branch or '0'
    addr = ET.SubElement(cpa, "address")
    ET.SubElement(addr, "postalCode").text = tk
    ET.SubElement(addr, "city").text = city


def xml_header(parent, *, series, aa, date, typ, currency='EUR'):
    header = ET.SubElement(parent, "invoiceHeader")
    ET.SubElement(header, "series").text = series
    ET.SubElement(header, "aa").text = aa
    ET.SubElement(header, "issueDate").text = date
    ET.SubElement(header, "invoiceType").text = typ
    ET.SubElement(header, "currency").text = currency
    return header


def xml_pay(parent, *, typ, amount, info):
    payd = ET.SubElement(parent, "paymentMethodDetails")
    ET.SubElement(payd, "type").text = typ
    ET.SubElement(payd, "amount").text = amount
    ET.SubElement(payd, "paymentMethodInfo").text = info
    return payd


def xml_lines(parent, *, data: list[dict]):
    for i, lin in enumerate(data):
        xml_invoice_details(parent, i+1, lin['val'], lin['typ'])


def create(afm: str, aa: str, date: str, ldata):
    # Create the root element
    root = ET.Element("InvoicesDoc", attrib=AADE_ATTRIBUTES)

    invoice = ET.SubElement(root, "invoice")

    xml_issuer(invoice, afm=afm, country='GR', branch='1')
    # xml_counterpart(invoice, afm='888888888', tk='22222',
    #                 city='IRAKLIO', country=None, branch=None)
    xml_header(invoice, series='0', aa=aa, date=date, typ='17.1')

    pay = ET.SubElement(invoice, "paymentMethods")
    xml_pay(pay, typ='3', amount='900.00', info='Payment Method Info...')

    xml_lines(invoice, data=ldata)

    # taxes_totals = ET.SubElement(invoice, "taxesTotals")
    # xml_taxes(taxes_totals, 1, '10.00', 11)
    # xml_taxes(taxes_totals, 5, '160.00', None)
    # xml_taxes(taxes_totals, 5, '240.00', None)
    # xml_taxes(taxes_totals, 1, '1.00', 14)

    isum = xml_invoice_summary(invoice, '900.00', '0.00', '0.00', '900.00')

    xml_expenses_classification(isum, 'E3_581_001', 'category2_6', '900.00')
    # xml_expenses_classification(isum, 'E3_581_002', 'category2_6', '240.00')

    tree = ET.ElementTree(root)
    xml_string = ET.tostring(root, encoding="UTF-8", xml_declaration=True)
    tree.write(f'misthodosia-{date}.xml',
               encoding="UTF-8", xml_declaration=True)
    return xml_string


if __name__ == '__main__':
    test_data = [
        {'val': '900.00', 'typ': 'E3_581_001'},
        # {'val': '240.00', 'typ': 'E3_581_002'},
        # {'val': '100.00', 'typ': 'E3_581_001'}
    ]
    create('999999999', '17', '2023-02-01', test_data)
