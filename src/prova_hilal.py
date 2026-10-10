"""H2 isinma gorevi: 1-100 arasi 10 rastgele sayi uretip CSV'ye yazar."""

import csv
import random
from pathlib import Path

ADET = 10
ALT, UST = 1, 100
DOSYA = Path(__file__).resolve().parents[1] / "data" / "prova-hilal.csv"


def rastgele_uret(adet=ADET):
    """adet kadar tamsayi dondur."""
    return [random.randint(ALT, UST) for _ in range(adet)]


def csv_kaydet(degerler, hedef=DOSYA):
    """Degerleri tek sutunlu CSV olarak yazar, basligi 'deger'."""
    hedef.parent.mkdir(parents=True, exist_ok=True)
    with hedef.open("w", newline="", encoding="utf-8") as dosya:
        yazici = csv.writer(dosya)
        yazici.writerow(["deger"])
        yazici.writerows([[d] for d in degerler])


def main():
    degerler = rastgele_uret()
    csv_kaydet(degerler)
    print(f"Uretilen degerler: {degerler}")
    print(f"{len(degerler)} satir yazildi -> {DOSYA.relative_to(Path.cwd())}")


if __name__ == "__main__":
    main()
