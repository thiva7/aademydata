from dataclasses import dataclass , field
import helper
from typing import Optional

@dataclass
class LData:
    """
    @param ccat: Κατηγορία Εσόδων
    @param ctype: Είδος Εσόδου
    @param value: Αξία
    @param vatcat: Κατηγορία ΦΠΑ || πιθανές τιμές:
        1: ["ΦΠΑ συντελεστής 24%"],
        2: ["ΦΠΑ συντελεστής 13%"],
        3: ["ΦΠΑ συντελεστής 6%"],
        4: ["ΦΠΑ συντελεστής 17%"],
        5: ["ΦΠΑ συντελεστής 9%"],
        6: ["ΦΠΑ συντελεστής 4%"],
        7: ["Άνευ Φ.Π.Α.", 0],
        8: ["Εγγραφές χωρίς ΦΠΑ"],
        9: ["ΦΠΑ συντελεστής 3%"]
    @param vatExc: Κατηγορία Απαλλαγής ΦΠΑ || πιθανές τιμές 1- 31:
        δες στο helper.py τη συνάρτηση vatExemptionCategories()
    @param taxType: Είδος Φόρου || πιθανές τιμές:
        1 = Παρακρατούμενος Φόρος
        2 = Τέλη
        3 = Λοιποί Φόροι
        4 = Χαρτόσημο
        5 = Κρατήσεις # δεν εχει υλοποιηθεί ακομα
    @param taxTypeCategory: Κατηγορία Φόρου
    @param taxTypePrice: Ποσό Φόρου || οταν ο φόρος είναι << ποσό >>
    """
    ccat: str
    ctype: str
    value: float
    vatcat: int
    vatExc: Optional[int] = field(default=None)
    taxType: Optional[int] = field(default=None)
    taxTypeCategory: Optional[int] = field(default=None)
    taxTypePrice: Optional[float] = field(default=None)
    Helper = helper.Helper()

    def __post_init__(self):
        if self.vatcat == 7 and (self.vatExc is None or self.vatExc == ''):
            raise ValueError("vatExemptionCategory (vatExc) is required when vatCategory is 7")
        if self.taxType is not None and self.taxTypeCategory is None:
            raise ValueError("taxTypeCategory is required when taxType is set")

    @property
    def vat(self):
        try:
            return round(self.value * self.Helper.vatCategories()[self.vatcat][1], 2)
        except KeyError:
            return 0

    @property
    def total(self):
        return round(self.value + self.vat, 2)

    @property
    def taxTypesWithheld(self):
        try:
            if self.taxType == '1':
                checkOne = self.Helper.withheld()[self.taxTypeCategory][1]
                if checkOne == 'ποσό':
                    if self.taxTypePrice is None:
                        raise ValueError("taxTypePrice is required ")
                    return round(float(self.taxTypePrice), 2)
            else:
                return 0
            return round(self.value * checkOne, 2)
        except KeyError:
            return 0

    @property
    def taxTypesFees(self):
        try:
            if self.taxType == '2':
                checkOne = self.Helper.Fees()[self.taxTypeCategory][1]
                if checkOne == 'ποσό':
                    if self.taxTypePrice is None:
                        raise ValueError("taxTypePrice is required ")
                    return round(float(self.taxTypePrice), 2)
            else:
                return 0
            return round(self.value * checkOne, 2)
        except KeyError:
            return 0

    @property
    def taxTypesStampDuty(self):
        try:
            if self.taxType == '3':
                checkOne = self.Helper.stampDuty()[self.taxTypeCategory][1]
                if checkOne == 'ποσό':
                    if self.taxTypePrice is None:
                        raise ValueError("taxTypePrice is required ")
                    return round(float(self.taxTypePrice), 2)
            else:
                return 0
            return round(self.value * checkOne, 2)
        except KeyError:
            return 0

    @property
    def taxTypesOtherTaxes(self):
        try:
            if self.taxType == '4':
                checkOne = self.Helper.otherTaxes()[self.taxTypeCategory][1]
                if checkOne == 'ποσό':
                    if self.taxTypePrice is None:
                        raise ValueError("taxTypePrice is required ")
                    return round(float(self.taxTypePrice), 2)
            else:
                return 0

            return round(self.value * checkOne, 2)
        except KeyError:
            return 0


@dataclass
class InvData:
    lines: list[LData]

    @property
    def total_per_cat(self):
        dtotal = {}
        for lin in self.lines:
            key = (lin.ccat, lin.ctype)
            dtotal[key] = dtotal.get(key, 0)
            dtotal[key] = round(dtotal[key] + lin.value, 2)
        return dtotal

    @property
    def total_value(self):
        tval = 0
        for lin in self.lines:
            tval += lin.value
        return round(tval, 2)

    @property
    def total_vat(self):
        tval = 0
        for lin in self.lines:
            tval += lin.vat
        return round(tval, 2)

    @property
    def total(self):
        return round(self.total_value + self.total_vat, 2)

    @property
    def total_withheld(self):
        tval = 0
        for lin in self.lines:
            tval += lin.taxTypesWithheld
        return round(tval, 2)

    @property
    def total_fees(self):
        tval = 0
        for lin in self.lines:
            tval += lin.taxTypesFees
        return round(tval, 2)

    @property
    def total_stampDuty(self):
        tval = 0
        for lin in self.lines:
            tval += lin.taxTypesStampDuty
        return round(tval, 2)

    @property
    def total_otherTaxes(self):
        tval = 0
        for lin in self.lines:
            tval += lin.taxTypesOtherTaxes
        return round(tval, 2)

    @property
    def total_gross(self):
        return round(self.total + self.total_fees + self.total_stampDuty + self.total_otherTaxes - self.total_withheld, 2)


