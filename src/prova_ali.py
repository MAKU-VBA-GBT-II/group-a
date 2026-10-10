"""H2 ısınma — 1-100 arasında 10 rastgele sayı üretip data/prova-ali.csv dosyasına yazar."""
import csv
import random
from pathlib import Path

TOHUM = 42          # sabit tohum: aynı tohum -> aynı dosya
ADET = 10
CIKTI = Path(__file__).resolve().parent.parent / "data" / "prova-ali.csv"


def main():
    random.seed(TOHUM)
    sayilar = [random.randint(1, 100) for _ in range(ADET)]
    CIKTI.parent.mkdir(parents=True, exist_ok=True)
    with open(CIKTI, "w", newline="", encoding="utf-8") as f:
        yazici = csv.writer(f)
        yazici.writerow(["deger"])
        for s in sayilar:
            yazici.writerow([s])
    print(f"{CIKTI} yazıldı ({len(sayilar)} satır)")


if __name__ == "__main__":
    main()
