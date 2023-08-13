# Importation des bibliothèques
from bs4 import BeautifulSoup
from selenium import webdriver
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
datas = pd.read_csv('/Users/charles-albert/Desktop/Manga Downloader/mangas.csv') # Parcourir les noms de mangas | créer une nouvelle colonne pour les mangas supprimés

# Création des liste et dictionnaires 
manga_chapters_dict = {} # création du dictionnaire qui contiendra les chapitres respectifs de chaque manga
mangas_w_dfts = [] # création de la liste qui contiendra les mangas supprimés de la liste d'origine

print("\nSuppression du manga 'rengokuno-ash' ...")
mangas_w_dfts.append({"dropped": 'rengokuno-ash'}) # Ajouter le manga avec defaut dans une liste
datas = datas.drop(datas[datas['name'] == 'rengokuno-ash'].index)

print("\nDebut Scrapping ... ")
for manga_name in datas['name']:

    url_start = f'https://www.japscan.lol/manga/{manga_name}/'
    # Accès à la page avec Selenium
    driver.get(url_start)
    soup = BeautifulSoup(driver.page_source, 'html.parser') # Analyser toute la page html

    balise_0 = str('//*[@id="chapters_list"]/h4/span') # Récupérer l'élément qui contient le fait que ce soit un webtoon / non si c'est le premier élément de la page
    balise_00 = str('//*[@id="chapters_list"]/h4[1]/span/') # Récupérer l'élément qui contient le fait que ce soit un webtoon / non si ce n'est pas le premier élément de la page
    balise_000 = str('//*[@id="collapse-1"]/div[1]/span') # Récupérer l'élément qui contient la date de dernière publication d'un chapitre/volume du manga
    
    try:
        # Suppression des mangas présentant des défauts
        try:
            element_0 = driver.find_element(By.XPATH,balise_0).text # valeur qui indique si c'est un webtoon
        except:
            element_0 = driver.find_element(By.XPATH,balise_00).text # valeur qui indique si c'est un webtoon ( option 2 )

        element_000 = driver.find_element(By.XPATH,balise_000).text # valeur qui indique la date de dernière publication d'un chapitre/volume du manga
        last_update = int(re.search(r'\d{4}', element_000).group(0)) # on récupère le nombre correspondant à l'année de dernière publication
        
        if element_0.lower() == 'webtoon' or last_update <= 2020: # Si le manga est un webtoon ou sa dernière update remonte à 2020 ou moins => suppression
            mangas_w_dfts.append({"dropped": manga_name}) # Ajouter le nom du manga supprimé à la liste 'mangas_w_dfts'
            datas = datas.drop(datas[datas['name'] == manga_name].index) # Supprimer le nom du manga en question de la colonne 'name'

        else:
            i = 1
            i_2 = 1
            print(f"\nManga : {manga_name}") # Indique dans quel manga nous sommes pour le scrapping des chapitres
            manga_chapters_dict[manga_name]=[] # Crée une clé de dictionnaire vide , avec le nom du manga qu'on explore.
            while True:
                try:
                    balise_1 = str(f'//*[@id="collapse-{i_2}"]/div[{i}]/a')  # Récupérer l'élément qui contient le dernier chapitre / volume ( format string )
                    element_1 = driver.find_element(By.XPATH,balise_1) # Chemin vers la balise contenant le chapitre {i} ou le volume {i} disponible
                    while True:
                        try:
                            balise_1 = str(f'//*[@id="collapse-{i_2}"]/div[{i}]/a')
                            element_1 = driver.find_element(By.XPATH,balise_1) 
                            valeur_href_1 = element_1.get_attribute('href') # Récupérer la valeur de l'attribut "href" de l'élément <a>
                            # Utiliser une expression régulière pour extraire la valeur
                            result_1 = re.search(r'/([^/]+)/$', valeur_href_1)  # On récupère uniquement le nom du manga

                            if result_1:
                                chapter = result_1.group(1)
                                if chapter:
                                    try: # Le format est uniquement le numéro d'un chapitre
                                        chapter_float = float(chapter)
                                        if chapter_float.is_integer():
                                            chapter_int = int(chapter_float)
                                            chapter_str = 'chapitre'+' '+str(chapter_int)
                                        else:
                                            chapter_str = 'chapitre'+' '+str(chapter_float)
                                        manga_chapters_dict[manga_name].append(chapter_str)          # Ajouter le chapitre à 'manga_chapters_dict' avec sa clé correspondante   
                                        print(f"{chapter_str} récupéré ")
                                        i += 1
                                    except: # Le format est f'volume-{nb_chapters}'
                                        volume_str = str(chapter.replace('-', ' '))
                                        manga_chapters_dict[manga_name].append(volume_str)          # Ajouter le volume à 'manga_chapters_dict' avec sa clé correspondante      
                                        print(f"{volume_str} récupéré ")
                                        i += 1
                                else:
                                    print(f"Aucune valeur trouvée | result")
                            else:
                                print(f"Aucune valeur trouvée. | result_1")
                        except:
                            i = 1
                            i_2 += 1
                            break 
                except:
                    break         
    except:
        print(f"Aucun chemin trouvé. | try 0")

print(f"{len(mangas_w_dfts)} mangas défectueux.")

# Réinitialiser les index du dataframe
datas = datas.reset_index(drop=True)
# On ajoute le contenu de 'mangas_w_dfts' au dataframe 'datas' sous une autre colonne, les colonnes du dictionnaire sont automatiquement détectées
datas = pd.concat([datas, pd.DataFrame(mangas_w_dfts, dtype=str)], axis=1)
# Convertir le dictionnaire en document YAML
yml_data = yaml.dump(manga_chapters_dict)

print(f"\nSauvegarde des datas ...")
# Sauvegarde des datas
datas.to_csv('/Users/charles-albert/Desktop/Manga Downloader/mangas.csv', index=False)

with open('/Users/charles-albert/Desktop/Manga Downloader/mangas_chapters.yml', 'w') as file:
    file.write(yml_data)

print(f"\nFin Scrapping.")
driver.quit()
