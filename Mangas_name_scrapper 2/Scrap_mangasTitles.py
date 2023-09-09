from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
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
a = ""
page = 1
datas = pd.DataFrame(columns=["name"]) # on crée un dataframe d'une colonne
new_list = [] # création d'une liste vide

print("\n Debut Scrapping ... \n")
while True:
    try:
        if starting_page == 1:
            url_start = f"https://scantrad-vf.co/manga/{a}?m_orderby=alphabet" # url page
        else:
            url_start = f"https://scantrad-vf.co/manga/page/{page}/?m_orderby=alphabet" # url page

        # Accès à la page avec Selenium
        driver.get(url_start)

        print(f"\n Page {starting_page} :")

        # on récupère tous les éléments correspondant à la classe 'h5'
        elements = driver.find_elements(By.CLASS_NAME, 'h5') 
        # Parcourir la liste des éléments de la classe h5
        for element in elements:
            link = element.find_element(By.TAG_NAME, 'a')
            # Récupérer la valeur de l'attribut "href" de l'élément <a>
            valeur_href = link.get_attribute('href')
            # Utiliser une expression régulière pour extraire uniquement le nom du manga 
            result = re.search(r'/manga/([^/]+)/', valeur_href)
            if result:
                manga_name = result.group(1)
                new_list.append({"name": manga_name})
                print(f"{manga_name} ajouté")
            else:
                print(f"Aucune valeur trouvée pour {valeur_href}. Page N°{starting_page}")
        starting_page += 1
        page += 1
    except:
        print("Fin Scrapping")
        break
        
print(f"\n{len(new_list)} Récupérés.")
# On ajoute le contenu de 'new_list' au dataframe 'datas'
datas = pd.concat([datas, pd.DataFrame(new_list)], ignore_index=True)

print(f"\nSauvegarde des datas ...")
# Sauvegarde des datas
datas.to_csv('/Users/charles-albert/Desktop/PandaScan/PandaScan/mangas.csv', index=False)                

print(f"\nFermeture navigateur.")
# Fermeture du navigateur
driver.quit()
