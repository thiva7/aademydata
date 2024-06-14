import json
import xml.etree.ElementTree as ET

import parameters as par
import xml_parts as prt
from afm_checks import can_be_afm
from invoice import InvoiceHead
from settings import AADE_ATTRIBUTES, AADE_URL_TEST , forbiddencounterpart, forbiddenMovePurposes
from xml_parse import parse_response, parse_xml_invoice

def create_xml(ihd: InvoiceHead, linedata: par.InvData):
    root = ET.Element("InvoicesDoc", attrib=AADE_ATTRIBUTES)
    invoice = ET.SubElement(root, "invoice")
    prt.issuer(invoice, afm=ihd.afm, country='GR', branch=ihd.branch)
    if ihd.type not in forbiddencounterpart: # Αν ο τύπος τιμολογίου επιτρέπει τον αντίστοιχο τύπο αντισυμβαλλόμενου
        prt.counter_part(invoice, afm=ihd.cafm)
    prt.header(invoice, series=ihd.series, aa=ihd.aa,date=ihd.date, typ=ihd.type, currency='EUR')

    # if ihd.type not in forbiddenMovePurposes:
    #     prt.move_purpose(invoiceHeader, dispatchDate=ihd.date, dispatchTime='', vehicleNumber='ΕΚΑ 5485', purpose=1)

    prt.payment(invoice, typ='3', amount=linedata.total, info='Μετρητά')
    prt.lines(invoice, data=linedata)
    prt.summary(invoice, data=linedata)
    # *********
    # tree = ET.ElementTree(root)
    # tree.write(f'xxx.xml', encoding="UTF-8", xml_declaration=True)
    # *********
    return ET.tostring(root, encoding="UTF-8", xml_declaration=True)

def is_uid_in_aade(api, uid, dat) -> bool:
    uids = api.request_uids(dat)
    return uid in uids

def xmlinvoice2json(invoice_xml, response):
    invoice = parse_xml_invoice(invoice_xml)
    resp = parse_response(response)

    if resp:
        invoice['uid'] = resp['invoiceUid']
        invoice['mark'] = resp['invoiceMark']
    head = invoice['invoice']['invoiceHeader']
    json_name = f"{head['issueDate']}.{head['series']}.{head['aa']}.json"
    with open(json_name, "w", encoding='utf-8') as outfile:
        json.dump(invoice, outfile, ensure_ascii=False , indent=4) # για να αποθηκευτεί το json σε ευκολοδιάβαστη μορφή
    return invoice


def post_invoice(api, ihd: InvoiceHead, data):

    if not can_be_afm(ihd.afm):
        return 'Issuer AFM is not ok'

    if is_uid_in_aade(api, ihd.uid, ihd.date):

        return 'Invoice already exists'

    xml = create_xml(ihd, data)

    response = api.send_invoices(xml)

    xmlinvoice2json(xml, response)
    return response


if __name__ == '__main__':
    from environs import Env

    from aade_api import AadeApi
    from aade_user import AadeUser
    env = Env()
    env.read_env()

    user = AadeUser(env.str('SAM_USER'), env.str('SAM_KEY'))
    test_api = AadeApi(AADE_URL_TEST, user , True)
    ldt = par.InvData([
        par.LData('category1_1', 'E3_561_003', 127, 7 , vatExc=1),
        par.LData('category1_1', 'E3_561_003', 132, 1 , vatExc=''),

    ])
    ihead = InvoiceHead(env.str('AFM'), '2023-02-11', '0', '11.1', 'AA', '12', '')
    res = post_invoice(test_api, ihead, ldt)
    print(res)
    # root = ET.fromstring(res)
    # invoice_uid = root.find('response/invoiceUid').text
    # # auth_code = root.find('response/authenticationCode').text
    # invoiceMark = root.find('response/invoiceMark').text
    # status_code = root.find('response/statusCode').text
    # QrURL = root.find('response/qrUrl').text
    #
    # print(f"invoice_uid: {invoice_uid}")
    # # print(f"auth_code: {auth_code}")
    # print(f"invoiceMark: {invoiceMark}")
    # print(f"status_code: {status_code}")