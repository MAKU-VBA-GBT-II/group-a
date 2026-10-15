"""Isınma görevi: 1-100 arasında 10 rastgele tam sayı üretip data/prova-ebru.csv dosyasına yazar."""

import csv
import random
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
OUTPUT_FILE = DATA_DIR / "prova-ebru.csv"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    generator = random.Random(20261015)
    values = [generator.randint(1, 100) for _ in range(10)]

    with OUTPUT_FILE.open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(["deger"])
        writer.writerows([[value] for value in values])

    print(f"{len(values)} sayı yazıldı: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()