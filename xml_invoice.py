import json
import xml.etree.ElementTree as ET

import parameters as par
import xml_parts as prt
from afm_checks import can_be_afm
from invoice import InvoiceHead
from settings import AADE_ATTRIBUTES, AADE_URL
from xml_parse import parse_response, parse_xml_invoice
from helper import forbiddenMovePurposes, forbiddencounterpart

def create_xml(ihd: InvoiceHead, linedata: par.InvData):
    root = ET.Element("InvoicesDoc", attrib=AADE_ATTRIBUTES)
    invoice = ET.SubElement(root, "invoice")
    prt.issuer(invoice, afm=ihd.afm, country='GR', branch=ihd.branch)
    if ihd.type not in forbiddencounterpart: # Αν ο τύπος τιμολογίου επιτρέπει τον αντίστοιχο τύπο αντισυμβαλλόμενου
        prt.counter_part(invoice, afm=ihd.cafm ,name="name", country='GR', branch='1' , street='str',  postalCode='32200', city="chalkida")
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

    # print(resp['statusCode'])
    if resp['statusCode'] == 'Success':
        invoice['uid'] = resp['invoiceUid']
        invoice['mark'] = resp['invoiceMark']
    head = invoice['invoice']['invoiceHeader']
    json_name = f"CompleteJsons/{head['issueDate']}.{head['series']}.{head['aa']}.json"
    with open(json_name, "w", encoding='utf-8') as outfile:
        json.dump(invoice, outfile, ensure_ascii=False , indent=4) # για να αποθηκευτεί το json σε ευκολοδιάβαστη μορφή
    return invoice


def post_invoice(api, ihd: InvoiceHead, data):
    if not can_be_afm(ihd.afm):
        return  '{"message" :  Invalid issuer AFM}'
    if is_uid_in_aade(api, ihd.uid, ihd.date):
        return {"message": "Invoice already exists"}
    xml = create_xml(ihd, data)
    response = api.send_invoices(xml)
    # check if response is xml or json
    if response.startswith('<?xml'):
        xmlinvoice2json(xml, response)
        return response
    else:
        response = json.loads(response)
        return response



if __name__ == '__main__':
    from environs import Env

    from aade_api import AadeApi
    from aade_user import AadeUser
    env = Env()
    env.read_env()

    user = AadeUser(env.str('SAM_USER'), env.str('SAM_KEY'))
    test_api = AadeApi(AADE_URL, user , True)
    ldt = par.InvData(
        lines=[
            par.LData('category1_8', 'E3_562', value=26.88, vatcat=4), # απλο
        ],
        per_invoice_taxes= [
            par.TaxData(value=26.88, taxType=1, taxTypeCategory=2),
        ])


    # kotsovolos AFM for test is 094077783
    ihead = InvoiceHead(afm=env.str('AFM'), date='2023-02-12', branch='0', type='1.1', series='AA', aa='138', cafm='094077783')
    res = post_invoice(test_api, ihead, ldt)

    if '<?xml' in res:
        root = ET.fromstring(res)
        # message = root.find('.//message').text8.2
        status_code = root.find('response/statusCode').text
        if status_code == 'Success':
            # print(res)
            invoice_uid = root.find('response/invoiceUid').text
            invoiceMark = root.find('response/invoiceMark').text
            QrURL = root.find('response/qrUrl').text
            print(f"invoice_uid: {invoice_uid}")
            print(f"invoiceMark: {invoiceMark}")
            print(f"QrURL: {QrURL}")
        else:
            message = root.find('.//message').text
            print(f"{message}")

    else:
        print(res['message'])

