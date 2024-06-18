from dataclasses import dataclass


@dataclass
class LData:
    ccat: str
    ctype: str
    value: float
    vatcat: int
    vatExc: int

    @property
    def vat(self):
        try:
            return round(self.value * FPA[self.vatcat], 2)
        except KeyError:
            return 0

    @property
    def total(self):
        return round(self.value + self.vat, 2)


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


FPA = {
    1: 0.24,
    2: 0.13,
    3: 0.06,
    4: 0.17,
    5: 0.09,
    6: 0.04,
    7: 0,  # Άνευ Φ.Π.Α.
    8: 0,  # Εγγραφές χωρίς ΦΠΑ (πχ Μισθοδοσία, Αποσβέσεις)
}
