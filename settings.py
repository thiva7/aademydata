AADE_ATTRIBUTES = {
    'xmlns': 'http://www.aade.gr/myDATA/invoice/v1.0',
    'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
    'xsi:schemaLocation': "http://www.aade.gr/myDATA/invoice/v1.0/InvoicesDoc-v0.6.xsd",
    'xmlns:icls': "https://www.aade.gr/myDATA/incomeClassificaton/v1.0",
    'xmlns:ecls': "https://www.aade.gr/myDATA/expensesClassificaton/v1.0"
}
forbiddencounterpart = ['11.1', '11.2', '11.3', '11.4', '11.5']
forbiddenMovePurposes = ['1.5' , '2.1', '2.2', '2.3', '7.1', '8.1', '11.2']
forbiddenMeasurement = ['2.1', '2.2', '2.3', '7.1', '8.1','8.2' , '11.2']
Measurements = [ '-', 'Τεμάχια', 'Κιλά', 'Λίτρα']



# AADE_URL = 'https://mydatapi.aade.gr/myDATA'
AADE_URL_TEST = 'https://mydataapidev.aade.gr'
