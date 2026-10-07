"""Isınma görevi: 1-100 arasında 10 rastgele tam sayı üretip data/prova-tugba.csv dosyasına yazar."""

import csv
import random
from pathlib import Path

# Depo kökü = src klasörünün bir üstü
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
OUTPUT_FILE = DATA_DIR / "prova-tugba.csv"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    sayilar = [random.randint(1, 100) for _ in range(10)]

    with OUTPUT_FILE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["deger"])
        for sayi in sayilar:
            writer.writerow([sayi])

    print(f"{len(sayilar)} sayı yazıldı: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
