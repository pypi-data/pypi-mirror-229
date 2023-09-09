import subprocess
import platform


FOOD_STORES = {
    "Campus Kitchen One": "https://www.campus-kitchen-one.de/en/",
    "Filmuni Mensa": "https://www.studentenwerk-potsdam.de/essen/unsere-mensen/detailinfos/mensa-filmuniversitaet",
    "Mensa Griebnitzsee": "https://www.studentenwerk-potsdam.de/essen/unsere-mensen/detailinfos/mensa-griebnitzsee",
}


def main():
    open_cmd = "open" if platform.system() == "Darwin" else "xdg-open"

    for place, menu in FOOD_STORES.items():
        try:
            subprocess.run([open_cmd, menu])
        except Exception:
            print(f"{place} not available today!")


if __name__ == "__main__":
    main()
