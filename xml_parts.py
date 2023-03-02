from xml.etree.ElementTree import SubElement

import parameters as par


def issuer(parent, *, afm, country='GR', branch='0'):
    issuer = SubElement(parent, "issuer")
    SubElement(issuer, "vatNumber").text = afm
    SubElement(issuer, "country").text = country
    SubElement(issuer, "branch").text = branch
    return issuer


def counter_part(parent, *, afm, country='GR', branch='0'):
    cpart = SubElement(parent, "counterpart")
    SubElement(cpart, "vatNumber").text = afm
    SubElement(cpart, "country").text = country
    SubElement(cpart, "branch").text = branch
    return cpart


def header(parent, *, series, aa, date, typ, currency='EUR'):
    header = SubElement(parent, "invoiceHeader")
    SubElement(header, "series").text = series
    SubElement(header, "aa").text = aa
    SubElement(header, "issueDate").text = date
    SubElement(header, "invoiceType").text = typ
    SubElement(header, "currency").text = currency
    return header


def payment(parent, *, typ, amount, info):
    paymeth = SubElement(parent, "paymentMethods")
    payd = SubElement(paymeth, "paymentMethodDetails")
    SubElement(payd, "type").text = typ
    SubElement(payd, "amount").text = f'{amount:.2f}'
    SubElement(payd, "paymentMethodInfo").text = info
    return payd


def income_classification(parent, typ, category, amount):
    det_clas = SubElement(parent, "incomeClassification")
    SubElement(det_clas, "icls:classificationType").text = typ
    SubElement(det_clas, "icls:classificationCategory").text = category
    SubElement(det_clas, "icls:amount").text = f'{amount:.2f}'
    return det_clas


def _details(parent, aa, line: par.LData):
    det = SubElement(parent, "invoiceDetails")
    SubElement(det, "lineNumber").text = str(aa)
    SubElement(det, "netValue").text = f'{line.value:.2f}'
    SubElement(det, "vatCategory").text = str(line.vatcat)
    SubElement(det, "vatAmount").text = f'{line.vat:.2f}'
    income_classification(det, line.ctype, line.ccat, line.value)
    return det


def lines(parent, *, data: par.InvData):
    for i, lin in enumerate(data.lines):
        _details(parent, i+1, lin)


def summary(parent, *, data: par.InvData):
    sum = SubElement(parent, "invoiceSummary")
    SubElement(sum, "totalNetValue").text = f'{data.total_value:.2f}'
    SubElement(sum, "totalVatAmount").text = f'{data.total_vat:.2f}'
    SubElement(sum, "totalWithheldAmount").text = '0.00'
    SubElement(sum, "totalFeesAmount").text = '0.00'
    SubElement(sum, "totalStampDutyAmount").text = '0.00'
    SubElement(sum, "totalOtherTaxesAmount").text = '0.00'
    SubElement(sum, "totalDeductionsAmount").text = '0.00'
    SubElement(sum, "totalGrossValue").text = f'{data.total:.2f}'
    for cat_typ, val in data.total_per_cat.items():
        cat, typ = cat_typ
        income_classification(sum, typ, cat, val)
    return sum
