from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import re

# ----- Configuration de Selenium pour utiliser Chrome -----
# Chemin vers le profil Chrome
chrome_profile_path = '/Users/charles-albert/Library/Application Support/Google/Chrome/Default'
options = webdriver.ChromeOptions()
options.add_argument('--user-data-dir=' + chrome_profile_path)
driver = webdriver.Chrome(options=options)
driver.maximize_window() # Ouvrir le navigateur en full size
# -----------------------------------------------------------

starting_page = 1
datas = pd.DataFrame(columns=["name"]) # on crée un dataframe d'une colonne
new_list = [] # création d'une liste vide 

print("\n Debut Scrapping ... \n")
while starting_page <= 270:
    url_start = f'https://www.japscan.lol/mangas/{starting_page}' # url page
    # Accès à la page avec Selenium
    driver.get(url_start)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    print(f"\n Page {starting_page} :")

    for i in range(1,31):
        balise = str(f'//*[@id="main"]/div/div[3]/div[{i}]/a')
        try:
            element = driver.find_element_by_xpath(balise) # chemin vers la balise du nom du 1er manga
            # Récupérer la valeur de l'attribut "href" de l'élément <a>
            valeur_href = element.get_attribute('href')
            # Utiliser une expression régulière pour extraire la valeur
            result = re.search(r'/([^/]+)/$', valeur_href) # on récupère uniquement le nom du manga  
            if result:
                manga_name = result.group(1)
                new_list.append({"name": manga_name})

                print(f"{manga_name} ajouté")

            else:
                print(f"Aucune valeur trouvée à {i}. Page N°{starting_page}")
        except:
            print("Erreur, aucune information trouvée")
    starting_page += 1

print(f"\n{len(new_list)} Récupérés.")
# On ajoute le contenu de 'new_list' au dataframe 'datas'
datas = pd.concat([datas, pd.DataFrame(new_list)], ignore_index=True)

print(f"\nSauvegarde des datas ...")
#sauvegarde des datas
datas.to_csv('/Users/charles-albert/Desktop/Manga Downloader/mangas.csv', index=False)

print(f"\nFin Scrapping.")
# Fermeture du navigateur
driver.quit()
