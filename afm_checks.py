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


def check_afm_vies(afm: str, country='EL') -> tuple[bool, dict]:
    soap_client = Client(URL)
    response = soap_client.service.checkVat(country, afm)
    if not response['valid']:
        return False, {f'{afm}': 'Not valid in VIES'}
    return True, {f"{response['vatNumber']}": {response['name']}}


def can_be_afm(afm: str):
    """
    Algorithmic validation of Greek Vat Numbers
    """
    if not afm.isdigit() or afm.startswith("00000") or len(afm) != 9:
        return False

    pars = [256, 128, 64, 32, 16, 8, 4, 2]

    va1 = sum([int(afm[i]) * pars[i] for i in range(8)])

    return (va1 % 11) % 10 == int(afm[8])
