from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import re

# Trouver le nombre de chapitres d'un manga ( définir une fonction qui affichera le nombre de chapitres d'un manga)

# ----- Configuration de Selenium pour utiliser Chrome -----
# Chemin vers le profil Chrome
chrome_profile_path = '/Users/charles-albert/Library/Application Support/Google/Chrome/Default'
options = webdriver.ChromeOptions()
options.add_argument('--user-data-dir=' + chrome_profile_path)
driver = webdriver.Chrome(options=options,executable_path='/Users/charles-albert/Desktop/chromedriver_mac_arm64/chromedriver') # Chemin vers l'exécutable chromedriver
driver.maximize_window() # Ouvrir le navigateur en full size
# -----------------------------------------------------------

print("\n Importation et Creation des données ... \n")
# ouvrir le fichier csv mangas
datas = pd.read_csv('/Users/charles-albert/Desktop/Manga Downloader/mangas.csv') # créer 2 colonnes dans le dataframe ( chapter = bool & nb_chapters = )

# créer les listes contenant les nombres de chapitres respectifs et le fait qu'ils soient des volumes ou des chapitres simples
is_chapter = [] 
nb_chapters_list = [] 

print("\n Debut Scrapping ... \n")
for manga_name in datas['name']:

    url_start = f'https://www.japscan.lol/manga/{manga_name}/' # url page => manga
    # Accès à la page avec Selenium
    driver.get(url_start)
    soup = BeautifulSoup(driver.page_source, 'html.parser') # Analyser toute la page html

    balise = str('//*[@id="collapse-1"]/div[1]/a') # Récupérer l'élément qui contient le dernier chapitre / volume
    try:
        element = driver.find_element_by_xpath(balise) # chemin vers la balise contenant le dernier chapitre disponible
        valeur_href = element.get_attribute('href') # Récupérer la valeur de l'attribut "href" de l'élément <a>
        # Utiliser une expression régulière pour extraire la valeur
        result = re.search(r'/([^/]+)/$', valeur_href) # on récupère uniquement le nom du manga

        if result:
            final_chapter = result.group(1)

            try: # le format est uniquement le numéro d'un chapitre
                nb_chapters = int(final_chapter)
                nb_chapters_list.append({"nb_chapters": nb_chapters})          # ajouter le numero du chapitre final à 'nb_chapters_list'
                is_chapter.append({"is_chapter": True})
                print(f"chapitres disponibles : {nb_chapters} / Manga : {manga_name}")

            except: # le format est f'volume-{nb_chapters}'
                # Extraction du chiffre dans la chaîne de caractères
                result_2 = re.search(r"\d+", final_chapter)

                if result_2:
                    nb_chapters = int(result_2.group())
                    nb_chapters_list.append({"nb_chapters": nb_chapters})      # ajouter le numero du volume final à 'nb_chapters_list'
                    is_chapter.append({"is_chapter": False})
                    print(f"volumes disponibles : {nb_chapters} / Manga : {manga_name}")

                else:
                    nb_chapters = None
                    print(f"Aucune valeur trouvée | result_2")
        else:
            print(f"Aucune valeur trouvée. | result")
    except:
        print(f"Aucun chemin trouvé. | try")

print(f"\n{len(nb_chapters_list)} données récupérés.")

# On ajoute le contenu de 'nb_chapters' au dataframe 'datas'
datas = pd.concat([datas, pd.DataFrame(nb_chapters_list)], ignore_index=True)
# On ajoute le contenu de 'chapter' au dataframe 'datas'
datas = pd.concat([datas, pd.DataFrame(is_chapter)], ignore_index=True)

print(f"\nSauvegarde des datas ...")
#sauvegarde des datas
datas.to_csv('/Users/charles-albert/Desktop/Manga Downloader/mangas.csv', index=False)

print(f"\nFin Scrapping.")
driver.quit()