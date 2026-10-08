import random
from pathlib import Path

# 1-100 arasinda 10 rastgele sayi uret
sayilar = [random.randint(1, 100) for _ in range(10)]

# data/prova-sema.csv dosyasina tek sutun olarak yaz (baslik: deger)
cikti = Path(__file__).resolve().parent.parent / "data" / "prova-sema.csv"
cikti.parent.mkdir(parents=True, exist_ok=True)
cikti.write_text("deger\n" + "\n".join(str(s) for s in sayilar) + "\n", encoding="utf-8")

print(f"{len(sayilar)} sayi yazildi: {cikti}")
