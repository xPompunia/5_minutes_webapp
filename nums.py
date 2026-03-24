def generate_numbers(do_ilu=200):
    mianownik = {}
    dopelniacz = {}

    jednosci_mianownik = ["", "pierwszy", "drugi", "trzeci", "czwarty", "piąty", "szósty", "siódmy", "ósmy",
                          "dziewiąty"]
    jednosci_dopelniacz = ["", "pierwszego", "drugiego", "trzeciego", "czwartego", "piątego", "szóstego", "siódmego",
                           "ósmego", "dziewiątego"]

    nastki_mianownik = ["dziesiąty", "jedenasty", "dwunasty", "trzynasty", "czternasty", "piętnasty", "szesnasty",
                        "siedemnasty", "osiemnasty", "dziewiętnasty"]
    nastki_dopelniacz = ["dziesiątego", "jedenastego", "dwunastego", "trzynastego", "czternastego", "piętnastego",
                         "szesnastego", "siedemnastego", "osiemnastego", "dziewiętnastego"]

    dziesiatki_mianownik = ["", "", "dwudziesty", "trzydziesty", "czterdziesty", "pięćdziesiąty", "sześćdziesiąty",
                            "siedemdziesiąty", "osiemdziesiąty", "dziewięćdziesiąty"]
    dziesiatki_dopelniacz = ["", "", "dwudziestego", "trzydziestego", "czterdziestego", "pięćdziesiątego",
                             "sześćdziesiątego", "siedemdziesiątego", "osiemdziesiątego", "dziewięćdziesiątego"]

    for i in range(1, do_ilu + 1):
        if i < 10:
            m = jednosci_mianownik[i]
            d = jednosci_dopelniacz[i]
        elif 10 <= i < 20:
            m = nastki_mianownik[i - 10]
            d = nastki_dopelniacz[i - 10]
        elif 20 <= i < 100:
            dz = i // 10
            j = i % 10
            m = (dziesiatki_mianownik[dz] + " " + jednosci_mianownik[j]).strip()
            d = (dziesiatki_dopelniacz[dz] + " " + jednosci_dopelniacz[j]).strip()
        elif 100 <= i <= 200:
            reszta = i - 100
            if reszta == 0:
                m = "setny"
                d = "setnego"
            elif reszta < 10:
                m = "sto " + jednosci_mianownik[reszta]
                d = "sto " + jednosci_dopelniacz[reszta]
            elif 10 <= reszta < 20:
                m = "sto " + nastki_mianownik[reszta - 10]
                d = "sto " + nastki_dopelniacz[reszta - 10]
            elif reszta == 100:  # na wypadek liczby 200
                m = "dwusetny"
                d = "dwusetnego"
            else:
                dz = reszta // 10
                j = reszta % 10
                m = ("sto " + dziesiatki_mianownik[dz] + " " + jednosci_mianownik[j]).strip()
                d = ("sto " + dziesiatki_dopelniacz[dz] + " " + jednosci_dopelniacz[j]).strip()

        mianownik[str(i)] = m
        dopelniacz[str(i)] = d

    return mianownik, dopelniacz


# ready to import
ORDINAL_NOMINATIVE, ORDINAL_GENITIVE = generate_numbers(200)