from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import re
import yaml

# ----- Configuration de Selenium pour utiliser Chrome -----
# Chemin vers le profil Chrome
chrome_profile_path = '/Users/charles-albert/Library/Application Support/Google/Chrome/Default'
options = webdriver.ChromeOptions()
options.add_argument('--user-data-dir=' + chrome_profile_path)
driver = webdriver.Chrome(options=options)
driver.maximize_window() # Ouvrir le navigateur en full size
# -----------------------------------------------------------

print("\n Importation et Creation des données ... \n")
# Ouvrir le fichier csv mangas
datas = pd.read_csv('/Users/charles-albert/Desktop/PandaScan/PandaScan/mangas.csv') # Parcourir les noms de mangas 
manga_chapters_dict = {} # création du dictionnaire qui contiendra les chapitres respectifs de chaque manga

print("\nDebut Scrapping ... ")
for manga_name in datas['name']:
    url_start = f'https://scantrad-vf.co/manga/{manga_name}/'
    try:
        # Accès à la page avec Selenium
        driver.get(url_start)
        print(f"\nManga : {manga_name}") # Indique dans quel manga nous sommes pour le scrapping des chapitres
        manga_chapters_dict[manga_name]=[] # Crée une clé de dictionnaire vide , avec le nom du manga qu'on explore.

        driver.implicitly_wait(2)   # Attendre que la page soit complètement chargée ( vous pouvez ajuster le délai selon vos besoins ( 2s par défaut ))

        # on récupère tous les éléments correspondant à la classe 'wp-manga-chapter  '
        elements = driver.find_elements(By.CLASS_NAME, 'wp-manga-chapter  ') 
        # Parcourir tous les éléments de la classe 'wp-manga-chapter  ' ( les chapitres du manga dans lequel on se trouve )
        for element in elements:
            link = element.find_element(By.TAG_NAME, 'a')
            # Récupérer la valeur de l'attribut "href" de l'élément <a>
            valeur_href = link.get_attribute('href')
            # Utiliser une expression régulière pour extraire la valeur
            result = re.search(rf'/{manga_name}/([^/]+)/', valeur_href)  # On récupère le chapitre
            if result:
                chapter = result.group(1)
                if chapter:
                    chapter_str = chapter.replace('-',' ')
                    manga_chapters_dict[manga_name].append(chapter_str)          # Ajouter le chapitre à 'manga_chapters_dict' avec sa clé correspondante   
                    print(f"{chapter_str} récupéré ")
                else:
                    print(f"Aucune valeur trouvée | {valeur_href} | chapter")
            else:
                print(f"Aucune valeur trouvée. | {manga_name} | result")     
    except:
        print(f"Erreur | try")

# Réinitialiser les index du dataframe
datas = datas.reset_index(drop=True)
# Convertir le dictionnaire en document YAML
yml_data = yaml.dump(manga_chapters_dict)

print(f"\nSauvegarde des datas ...")
# Sauvegarde des datas
datas.to_csv('/Users/charles-albert/Desktop/PandaScan/PandaScan/mangas.csv', index=False)

with open('/Users/charles-albert/Desktop/PandaScan/PandaScan/mangas_chapters.yml', 'w') as file:
    file.write(yml_data)

print(f"\nFin Scrapping.")
driver.quit()
