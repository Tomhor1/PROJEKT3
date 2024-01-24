"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie
author: Tomáš Horniak
email: tomas.horniak27@gmail.com
discord: just#7854
"""

from bs4 import BeautifulSoup as BS
import csv
import requests
import sys


# zadanie vstupnych 2 argumentov a prvotna kontrola ich poctu:

def zadanie_vstupnych_argumentov(argv: str):
    print("Zadajte webovy odkaz na uzemny celok (1. vstup) a nazov vystupneho suboru vo formate .csv (2. vstup)")

    if len(argv) != 2:
        print("Zadali ste nesprávné vstupné data")
        sys.exit(1)

    # definicia argumentov:
    web_odkaz = argv[0]
    nazov_vystup_suboru = argv[1]

    # ak su zadané obe argumenty, kontrola najprv spravnosti odkazu (aj poradia argumentov):
    if not web_odkaz.startswith("https://volby.cz/pls/ps2017nss/"):
        print("Zadali ste nesprávny odkaz")
        sys.exit(1)

    # kontrola spravnosti vystupneho suboru
    elif not nazov_vystup_suboru.endswith(".csv"):
        print("zadany vystupny subor je v nespravnom formate")
        sys.exit(1)

    else:
        print("Stahujem data zo zadaneho odkazu, prosim pockajte")

        return web_odkaz, nazov_vystup_suboru

        
# zadefinovanie funkcie na parsing najdenie kodov a mien lokacii + ulozenie do zoznamu a vytvorenie slovnika

def najdenie_kodu(web_odkaz: str):
    parsovany_web = BS(requests.get(web_odkaz).text, features="html.parser")
    pouzivany_odkaz = "https://www.volby.cz/pls/ps2017nss/"
    vsetky_tr_tagy = parsovany_web.find_all("tr")
    vsetky_odkazy = []
    volby = []
    rozsah = range(1,4)

    for tr_tag in vsetky_tr_tagy:
        kody_a_nazov_lokacii = dict ()
        kod = tr_tag.find("td", {"class": "cislo"})
        for cislo in rozsah:
            nazov = tr_tag.find ("td", {"headers": f"t{cislo}sa1 t{cislo}sb2"})        
            if kod and nazov is not None:
                kody_a_nazov_lokacii["code"] = kod.text
                kody_a_nazov_lokacii["location"] = nazov.text
                #zapis kod a nazov lokacie do zoznamu
                volby.append(kody_a_nazov_lokacii)
                # zapis do zoznamu odkaz na konkretny vyber obce:
                vsetky_odkazy.append(pouzivany_odkaz + kod.find("a")["href"])
                break
    return vsetky_odkazy, volby

# zadefinovanive funkcie na zistenie zvysnych potrebnych udajov o pocte volicov, vydane obalkok a platnych hlasov

def udaje_o_volicoch_a_obalkach (vsetky_odkazy, volby):
    for index, kody_a_nazov_lokacii in enumerate(volby):
        web_odkaz = vsetky_odkazy[index]
        parsovany_web = BS(requests.get(web_odkaz).text, features="html.parser")
        kody_a_nazov_lokacii["registered"] = parsovany_web.find("td", {"headers": "sa2"}).text
        kody_a_nazov_lokacii["envelopes"] = parsovany_web.find("td", {"headers": "sa5"}).text
        kody_a_nazov_lokacii["valid"] = parsovany_web.find("td", {"headers": "sa6"}).text
       
    return volby

# zadefinovanie funkcie na vycitanie kandidujich stran a pocet ich hlasov

def strany_a_hlasy (vsetky_odkazy: list, hlasy: list):
    for index, rada in enumerate(hlasy):
        web_odkaz = vsetky_odkazy[index]
        parsovany_web = BS(requests.get(web_odkaz).text, features="html.parser")
        div_tagy = parsovany_web.find("div", {"id": "inner"})

        for div_tag in div_tagy:
            tr_tagy = div_tagy.find_all("tr")

            for tr_tag in tr_tagy:
                    nazov_strany = tr_tag.find("td", {"class": "overflow_name"})
                    rozsah = range(1, 4)


                    for cislo in rozsah:
                        pocet_hlasov = tr_tag.find("td", {"headers": f"t{cislo}sa2 t{cislo}sb3"})

                        if nazov_strany is not None and pocet_hlasov is not None:
                            rada[nazov_strany.text] = pocet_hlasov.text
                            break
    return hlasy

# zadefinovanive funkcie na ulozenie dat do suboru vo formate CSV

def finalne_ulozenie_suboru(nazov_vystup_suboru, volby):
    try:
        with open(nazov_vystup_suboru, mode="w", newline="") as CSVsubor:
            hlavicka = volby[0].keys()
            zapisovac = csv.DictWriter(CSVsubor, fieldnames=hlavicka)
            zapisovac.writeheader()
            zapisovac.writerows(volby)
            print("Data boli uspesne stiahnute z", web_odkaz, "ukladam do suboru a ukončujem program")

    except Exception as e:
        print(f"Vyskytla sa chyba: {e}")

# zadefinovanie primarnej funkcie

def primarna_funkcia(argv: str):
    web_stranka, nazov_vystup_suboru = zadanie_vstupnych_argumentov(argv)
    vsetky_odkazy, pozicia_kodu = najdenie_kodu(web_stranka)
    druh_hlasu = udaje_o_volicoch_a_obalkach(vsetky_odkazy, pozicia_kodu)
    data_s_volbami_na_ulozenie = strany_a_hlasy(vsetky_odkazy, druh_hlasu)
    finalne_ulozenie_suboru(nazov_vystup_suboru, data_s_volbami_na_ulozenie)

if __name__ == "__main__":
    primarna_funkcia(sys.argv[1:])