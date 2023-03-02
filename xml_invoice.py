import json
import xml.etree.ElementTree as ET

import parameters as par
import xml_parts as prt
from afm_checks import can_be_afm
from invoice import InvoiceHead
from settings import AADE_ATTRIBUTES, AADE_URL_TEST
from xml_parse import parse_response, parse_xml_invoice


def create_xml(ihd: InvoiceHead, linedata: par.InvData):

    root = ET.Element("InvoicesDoc", attrib=AADE_ATTRIBUTES)
    invoice = ET.SubElement(root, "invoice")
    prt.issuer(invoice, afm=ihd.afm, country='GR', branch=ihd.branch)
    prt.counter_part(invoice, afm=ihd.cafm)
    prt.header(invoice, series=ihd.series, aa=ihd.aa,
               date=ihd.date, typ=ihd.type, currency='EUR')
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
        json.dump(invoice, outfile, ensure_ascii=False)
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

    user = AadeUser(env.str('TED_USER'), env.str('TED_KEY'))
    test_api = AadeApi(AADE_URL_TEST, user)
    ldt = par.InvData([
        par.LData('category1_2', 'E3_561_001', 127, 1),
        par.LData('category1_2', 'E3_561_002', 12, 2),
        par.LData('category1_2', 'E3_561_002', 31, 1),
    ])
    ihead = InvoiceHead(env.str('TED_AFM'), '2023-02-11', '0',
                        '1.1', '0', '43', env.str('TEST_AFM'))
    res = post_invoice(test_api, ihead, ldt)
    print(res)
    # print(api.cancel_invoice('400001904257340'))
    # booki = api.request_my_income('2023-01-01', '2023-02-28')
    # print(booki)
