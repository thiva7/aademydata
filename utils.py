import os
import pickle

from zeep import Client

URL = "http://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl"


def check_afms(afm_list: list) -> tuple[dict, list]:
    afm_list.sort()
    afm_err = []

    cln = Client(URL)
    responses = []
    for afm in afm_list:
        rsp = cln.service.checkVat("EL", afm)
        if not rsp["valid"]:
            afm_err.append(afm)
        else:
            responses.append(rsp)
        print(f"{rsp['vatNumber']} {rsp['valid']} {rsp['name']}")

    verified = {i['vatNumber']: i['name'] for i in responses}
    return verified, afm_err


def afm_names(fname, afms_file):
    validated_afms = read_text_dict(afms_file)
    data = read_picled(fname)
    afms = list(set([inv['issuer']['vatNumber'] for inv in data]))
    afms2check = []
    for afm in afms:
        if afm not in validated_afms.keys():
            afms2check.append(afm)
    if afms2check == []:
        print('No New AFMs to check. Returning')
        return
    checked_afms, error_afms = check_afms(afms2check)
    write_text_dict(afms_file, validated_afms | checked_afms)
    write_text(f'errors.{afms_file}', error_afms)


def read_picled(fname):
    with open(fname, 'rb') as handle:
        data = pickle.load(handle)
    return data


def read_text_dict(fname: str) -> dict:
    data = {}
    with open(fname, encoding='utf-8') as handle:
        for line in handle.readlines():
            key, *val = line.strip().split(' ')
            data[key] = ' '.join(val)
    return data


def write_text_dict(fname: str, data: dict):
    if not data:
        return
    with open(fname, 'w', encoding='utf-8') as handle:
        handle.write('\n'.join([f'{k} {v}' for k, v in data.items()]))


def write_text(fname: str, data: list):
    if not data:
        return
    with open(fname, 'w') as handle:
        handle.write('\n'.join(data))


def clean_afms(afms: list) -> list:
    uni_afms = list(set(afms))
    not_empty = [afm for afm in uni_afms if afm != '']
    return not_empty


def update_afms(afms_file: str, new_afms: list) -> dict:
    validated_afms = read_text_dict(afms_file)
    afms = clean_afms(new_afms)
    afms2check = [afm for afm in afms if afm not in validated_afms.keys()]
    if afms2check == []:
        print('No New AFMs to check.')
        return validated_afms
    checked_afms, error_afms = check_afms(afms2check)
    for afm in error_afms:
        checked_afms[afm] = 'error-Not in Vies database'
    updated_afms = validated_afms | checked_afms
    write_text_dict(afms_file, updated_afms)
    return updated_afms


def set_value(list_dict: list[dict], search_key: str, new_key: str, dic_vals: dict) -> list[dict]:
    for adic in list_dict:
        val = adic.get(search_key, '')
        adic[new_key] = dic_vals.get(val, '')
    return list_dict


def write_pickle(invoices, filename):
    data = []
    old_marks = []
    if os.path.exists(filename):
        with open(filename, 'rb') as handle:
            data = pickle.load(handle)
            old_marks = [i['mark'] for i in data]
    for inv in invoices:
        if inv['mark'] in old_marks:
            continue
        data.append(inv)
    data = sorted(data, key=lambda d: d['invoiceHeader']['issueDate'])
    with open(filename, 'wb') as handle:
        pickle.dump(data, handle)


def print_inv(datafile, afmfile):
    data = read_picled(datafile)
    afms = read_text_dict(afmfile)
    for inv in data:
        dat = inv['invoiceHeader']['issueDate']
        aaa = inv['invoiceHeader']['aa']
        typ = inv['invoiceHeader']['invoiceType']
        pro = inv['issuer']['vatNumber']
        nam = afms.get(pro, '')
        net = float(inv['invoiceSummary']['totalNetValue'])
        vat = float(inv['invoiceSummary']['totalVatAmount'])
        tot = float(inv['invoiceSummary']['totalGrossValue'])
        mrk = inv['mark']
        print(
            f'{mrk} {pro} {nam:45}{dat} {typ:4} {aaa:^10} {net:>10.2f} {vat:>10.2f} {tot:>10.2f}')
