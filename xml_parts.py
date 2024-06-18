from xml.etree.ElementTree import SubElement

import parameters as par


def issuer(parent, *, afm, country='GR', branch='0'):
    iss = SubElement(parent, "issuer")
    SubElement(iss, "vatNumber").text = afm
    SubElement(iss, "country").text = country
    SubElement(iss, "branch").text = branch
    return iss


def counter_part(parent, *, afm, name= '' , country='GR', branch='0' , street='', postalCode='', city=''):
    cpart = SubElement(parent, "counterpart")
    SubElement(cpart, "vatNumber").text = afm
    SubElement(cpart, "country").text = country
    SubElement(cpart, "branch").text = branch
    if country != 'GR' and name != '': # οταν ειναι 1.2 η 1.3 ειναι υποχρεωτικό να υπάρχει το όνομα του συμβαλλόμενου
        SubElement(cpart, "name").text = name
    if street != '' and postalCode != '' and city != '':
        address = SubElement(cpart, "address")
        SubElement(address, "street").text = street
        SubElement(address, "postalCode").text = postalCode
        SubElement(address, "city").text = city

    return cpart


def header(parent, *, series, aa, date, typ, currency='EUR'):
    head = SubElement(parent, "invoiceHeader")
    SubElement(head, "series").text = series
    SubElement(head, "aa").text = aa
    SubElement(head, "issueDate").text = date
    SubElement(head, "invoiceType").text = typ
    SubElement(head, "currency").text = currency
    return head

def move_purpose( parent, * ,dispatchDate,dispatchTime, vehicleNumber ,  purpose):
    SubElement(parent, "dispatchDate").text =dispatchDate
    if dispatchTime != '':
        SubElement(parent, "dispatchTime").text = dispatchTime
    SubElement(parent, "vehicleNumber").text = vehicleNumber
    SubElement(parent, "movePurpose").text = str(purpose)


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
    if line.taxType == "1":
        SubElement(det, "withheldAmount").text = f'{line.taxTypesWithheld:.2f}'
        SubElement(det, "withheldPercentCategory").text = line.taxTypeCategory
    elif line.taxType == "2":
        SubElement(det, "feesAmount").text = f'{line.taxTypesFees:.2f}'
        SubElement(det, "feesPercentCategory").text = line.taxTypeCategory
    elif line.taxType == "3":
        SubElement(det, "stampDutyAmount").text = f'{line.taxTypesStampDuty:.2f}'
        SubElement(det, "stampDutyPercentCategory").text = line.taxTypeCategory
    elif line.taxType == "4":
        SubElement(det, "otherTaxesAmount").text = f'{line.taxTypesOtherTaxes:.2f}'
        SubElement(det, "otherTaxesPercentCategory").text = line.taxTypeCategory
    else:
        pass

    if line.vatcat == 7: # προσθήκη κατηγορίας απαλλαγής ΦΠΑ για τις εξαιρέσεις
        SubElement(det, "vatExemptionCategory").text = f'{line.vatExc}'
    income_classification(det, line.ctype, line.ccat, line.value)
    return det


def lines(parent, *, data: par.InvData):
    for i, lin in enumerate(data.lines):
        _details(parent, i+1, lin)


def summary(parent, *, data: par.InvData):

    isum = SubElement(parent, "invoiceSummary")
    SubElement(isum, "totalNetValue").text = f'{data.total_value:.2f}'
    SubElement(isum, "totalVatAmount").text = f'{data.total_vat:.2f}'
    SubElement(isum, "totalWithheldAmount").text = f'{data.total_withheld:.2f}'
    SubElement(isum, "totalFeesAmount").text = f'{data.total_fees:.2f}'
    SubElement(isum, "totalStampDutyAmount").text = f'{data.total_stampDuty:.2f}'
    SubElement(isum, "totalOtherTaxesAmount").text = f'{data.total_otherTaxes:.2f}'
    SubElement(isum, "totalDeductionsAmount").text = '0.00'
    SubElement(isum, "totalGrossValue").text = f'{data.total_gross:.2f}'
    for cat_typ, val in data.total_per_cat.items():
        cat, typ = cat_typ
        income_classification(isum, typ, cat, val)
    return isum
