import hashlib
from dataclasses import dataclass


@dataclass
class InvoiceHead:
    afm: str
    date: str  # isodate
    branch: str
    type: str
    series: str
    aa: str
    cafm: str  # Counterpart AFM

    @property
    def uid(self):
        val = f'{self.afm}-{self.date}-{self.branch}-{self.type}-{self.series}-{self.aa}'
        return hashlib.sha1(val.encode(encoding='ISO-8859-7')).hexdigest().upper()
