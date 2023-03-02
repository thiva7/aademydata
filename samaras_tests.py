import xml_parse as xmlp
from aade_api import AadeApi
from utils import set_value, update_afms, write_pickle


def samaras_inv2pickle(api, apo, eos, filename):
    invoices = samaras_get_invoices(api, apo, eos)
    write_pickle(invoices, filename)


def samaras_get_invoices(api, apo, eos):
    xml = api.request_docs(apo, eos)
    invoices = xmlp.parse_xml_invoices(xml)
    return invoices


def samaras_book_expenses(api, apo, eos, afms_file='afms.txt'):
    xml = api.request_my_expenses(apo, eos)
    data = xmlp.parse_xml_books(xml, 6)
    docafms = [i.get('counterVatNumber', '') for i in data]
    afms = update_afms(afms_file, docafms)
    data = set_value(data, 'counterVatNumber', 'name', afms)
    return data


def samaras_book_income(api, apo, eos, afms_file='afms.txt'):
    xml = api.request_my_income(apo, eos)
    data = xmlp.parse_xml_books(xml, 7)
    docafms = [i.get('counterVatNumber', '') for i in data]
    afms = update_afms(afms_file, docafms)
    data = set_value(data, 'counterVatNumber', 'name', afms)
    return data


if __name__ == '__main__':
    from environs import Env

    from aade_user import AadeUser
    env = Env()
    env.read_env()
    URL = env.str('AADE_URL')
    USER = env.str('SAM_USER')
    KEY = env.str('SAM_KEY')
    user = AadeUser(USER, KEY)
    api = AadeApi(URL, user, True)
    data = samaras_book_expenses(api, '2022-12-28', '2022-12-28')
    # data = samaras_book_income(api, '2022-12-01', '2022-12-31', 'afms.txt')
    for el in data:
        print(el, '\n')
