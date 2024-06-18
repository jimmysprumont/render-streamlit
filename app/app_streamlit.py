import streamlit as st
import pandas as pd
import time
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from bs4 import BeautifulSoup
import requests
import json
from streamlit_star_rating import st_star_rating
from time import sleep
import datetime

blason_url = "https://media.discordapp.net/attachments/1241363551508234371/1245348085866041374/LE_MARCHOIS-removebg-preview_5.png?ex=66586c49&is=66571ac9&hm=cd8aea092007f31ec960b89444b39577e5c28f652854f7935bff7d05b327d8c4&=&format=webp&quality=lossless&width=450&height=395"
st.set_page_config(page_title="Cinéma le Marchois", page_icon=blason_url,layout='wide')

@st.cache_data
def load_data_sets():
    df_fusion_explode = pd.read_csv(r"/Users/sprumontjimmy/Documents/Data_analyst/Projet 2/Streamlit/df_fusion_explode_2.csv",
                           low_memory = False)

    df_ml =  pd.read_csv(r"/Users/sprumontjimmy/Documents/Data_analyst/Projet 2/Streamlit/df_ML.csv",
                         low_memory = False)
    
    
   # df_fusion_explode = pd.read_csv(r"C:\WCS\Projet_2\df_fusion_explode_2.csv",
  #                        low_memory = False)
#
   # df_ml =  pd.read_csv(r"C:\Users\phili\Downloads\df_ML.csv",
   #                  low_memory = False)

    return df_fusion_explode, df_ml
# data_load_state = st.text('Loading data...')
df_fusion_explode,df_ml = load_data_sets()

df_clients = pd.read_csv(r"/Users/sprumontjimmy/Documents/Data_analyst/Projet 2/Streamlit/keys.csv")

# entraînement ML
X = df_ml.drop(columns = "tconst")

scaler = StandardScaler().fit(X)
scaled_X = scaler.transform(X)

genre_weight = 2
year_weight = 2
scaled_X[:,6:] = scaled_X[:,6:]*genre_weight
scaled_X[:,3] = scaled_X[:,3]*year_weight

KNN_model = NearestNeighbors(n_neighbors = 5).fit(scaled_X)

# ANIMATION NEIGE 
# st.snow()

if "user_id" not in st.session_state:
    st.session_state.user_id = -1

#fonctions

def afficher_films(liste_films):
    try:
        if not liste_films.empty: # Lorsque l'input est ok
            base_url = "https://image.tmdb.org/t/p/original/"
            image_width = 300  # Largeur souhaitée pour les images

            # Convertir les valeurs de poster_path en chaînes de caractères et filtrer les valeurs manquantes
            liste_films['poster_path'] = liste_films['poster_path'].astype(str)
            liste_films = liste_films.drop_duplicates(subset=['poster_path'])

            images = [base_url + row['poster_path'] for index, row in liste_films.iterrows()]
            synopses = [row['overview'] for index, row in liste_films.iterrows()]
            dates_de_sortie = [row['year'] for index, row in liste_films.iterrows()] 
            titles = [row['title'] for index, row in liste_films.iterrows()]
            directors = [row['directors'] for index, row in liste_films.iterrows()]
            liste_tconsts =[row['tconst'] for index, row in liste_films.iterrows()]
            notes =[row['best_vote_avg'] for index, row in liste_films.iterrows()]
            # Afficher les images et les synopsis côte à côte
            placeholder = st.empty()
            with placeholder.container():
                for image, synopsis, date_de_sortie, title, director, note, tconst in zip(images, synopses, dates_de_sortie, titles, directors, notes, liste_tconsts):
                    videG,col1, col2,videD = st.columns([.5,1, 2,.5])
                    with col1:
                        st.image(image, use_column_width = "always")
                    with col2:
                        st.text(title)
                        st.text('Synopsis :')
                        st.markdown(f"<div style='word-wrap: break-word;'>{synopsis}</div>", unsafe_allow_html=True)
                        st.text(" ")
                        st.text("Date de sortie : " + str(date_de_sortie))
                        st.text("Réalisateur : " + str(director))
                        # st.text("Note : " + str(note)+"/10")
                        try : 
                            st_star_rating("", maxValue=5, defaultValue=( note/ 2), read_only=True, size=20)
                        except:
                            st.text("Pas de note")
                        video_popover = st.popover("Bande Annonce")
                            # st.write(tconst)
                        video_popover.video(play_teaser(tconst)) 
                            # st.button("CHOISIR")
                            # benj = st.button("Reset", key = tconst)
                            # if benj :
                                # select_input = df_fusion_explode[df_fusion_explode.tconst == tconst]

                                    #Vérifie que le titre est présent dans le DF
                                # afficher_films(select_input)

                        # # else:
                        #     st.write("Goodbye")
                    
                                           
        else:
            left_col, cent_col,last_col = st.columns(3) # je créé des col pour pouvoir centrer le GIF mais c'est pe bof bof
            with cent_col:
            # gif_url = "https://gifdb.com/images/high/game-of-thrones-my-watch-has-ended-1p6o7pkjxvoipcsy.webp"
                gif_url = "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExc21qMnpoMzFua2x1cnI3eTVmNWEwMHNrN3IycjVmbDRuZ2ptbHl3eSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/M9peqcoAM1w2tiNRZB/source.gif"
                st.text("   ")
                st.text(" ")
                st.text(" ")
                st.markdown(f'<img src="{gif_url}" alt="GIF" width="500">', unsafe_allow_html=True)
    except:
        pass
    
# FONCTION POUR LES BANDES ANNONCES 
navigator = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'

def play_teaser(id_film):
    
    try :
        #l'url de la page requêtée en fonction de l'id film
        url_page = "https://www.imdb.com/title/" + id_film + "/"
        
        #je requête la page
        html = requests.get(url_page, headers={'User-Agent': navigator})
        
        #je rends le code html compréhensible apr python
        soup = BeautifulSoup(html.text, 'html.parser')
        
        # premier filtre
        soup_teaser = soup.find_all("script",{"id":"__NEXT_DATA__"})
        
        # je trouve l'url
        url_teaser = json.loads(soup_teaser[0].text)\
            ["props"]["pageProps"]['aboveTheFoldData']\
            ['primaryVideos']["edges"][0]['node']['playbackURLs'][0]["url"]
            
        #que je retourne en résultat
        return url_teaser

    except :
        return "https://www.youtube.com/watch?v=o-YBDTqX_ZU"



# DEFITION DU CSS POUR LE SITE 

#[class="st-emotion-cache-ocqkz7 e1f1d6gn5"]{
#background:rgba(0,0,0,.9)
#}
#[data-testid="stExpander"]{
#background:rgba(100,0100,0100,.9)
#}

css = """
<style>

@import url('https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&display=swap');

[data-testid="StyledFullScreenButton"],
[data-testid="StyledFullScreenButton"] *{
display: none;}
body {
    font-family: 'Lato', serif;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Lato', serif;
}
img {
    border-radius: 25px;
    transition : transform .1s;
}
    div.example2:nth-child(2){background-color:green;}
[data-testid="stAppViewBlockContainer"]{
padding-top:2%;
}
[id="tabs-bui3-tabpanel-0"] img:hover{
    -ms-transform: scale(1.5); /* IE 9 */
    -webkit-transform: scale(1.5); /* Safari 3-8 */
    transform: scale(1.12);
}

[data-testid="stMarkdownContainer"] {
    font-family : "Roboto", sans-serif !important;
}
[data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size:1.5vw;
    text-align: center;
}
[id="tabs-bui3-tabpanel-1"] [data-testid="stHeading"]{
    font-size:1.5vw;
    text-align: center;
}
[data-baseweb="tab-list"]{
justify-content: space-evenly;
}

[data-baseweb="popover"]:has(video){
width:50%;
position: absolute;
top: 25%;
left: 50%;
transform: translate(-50%, 25%);}
}
</style>
"""


def la_fete():
    st.balloons()

# Insérer le CSS dans l'application Streamlit
st.markdown(css, unsafe_allow_html=True)
videG,colM,blason,colD,videD = st.columns([.5,1,.40,1,.5])
with blason :
    with st.empty():
        st.image(blason_url, use_column_width = 'always')
with colM :
    st.markdown("<h1 style='text-align: center; font-size: 3rem; color: white;'>CINEMA LE MARCHOIS</h1>", unsafe_allow_html=True)
with colD :
    st.markdown("<h1 style='text-align: center; font-size: 3rem; color: white;'>LE CHOIX DU CINEMA</h1>", unsafe_allow_html=True)

#st.markdown("<h1 style='text-align: center; color: black;'>Cinéma le Marchois</h1>", unsafe_allow_html=True)   

a,z,e = st.columns([2,1,2])
with z :
    st.button(label="Recommandations : VIP",
                on_click=la_fete,
                use_container_width = True)
tab1, tab2, tab3, tab4 = st.tabs(["Accueil", "Recommandations","Infos Pratiques","Mon Compte"])


# PAGE D'ACCEUIL  
with tab1:
    if st.session_state.user_id == -1 :
        liste_genre = ['Drama', 'Family', 'Comedy', 'Adventure', 'Romance']
    else :
        liste_genre = df_clients.selection_genres.values[0].split("*&$")
        if len(liste_genre) < 5 :
            for n in range(5-len(liste_genre)):
                liste_genre += [[genre] for genre in ['Drama', 'Family', 'Comedy', 'Adventure', 'Romance'] if genre not in df_clients.selection_genres.values[0].split("*&$")][n]
        
    # choisir_genres = st.selectbox('Choisissez un genre', df_fusion_explode['genres'].unique())
    for genre in liste_genre:
        st.header(genre, divider=True)

        affichage = df_fusion_explode[df_fusion_explode['genres'] == genre ]
        affichage = affichage[df_fusion_explode['best_vote_count'] > 35000.0]
        # affichage = affichage.sort_values(by = "best_vote_count", ascending=False).drop_duplicates(subset='title')
        affichage = affichage.drop_duplicates(subset='title').sample(frac=1).reset_index(drop=True)
        base_url = "https://image.tmdb.org/t/p/original/"
        affichage['poster_path'] = affichage['poster_path'].astype(str)
        images_x = [base_url + row['poster_path'] for index, row in affichage.iterrows()]
        synopses_a = [row['overview'] for index, row in affichage.iterrows()]
        image_width = 170
        # for index, row in affichage.iterrows():
        # st.image(row['poster_path'], width=200)
        num_columns = 5
        columns = st.columns(num_columns, gap="medium")
                    # Afficher les images et les synopsis côte à côte
        for i, (image, syn) in enumerate(zip(images_x, synopses_a)):
            if i < num_columns :
                with columns[i % num_columns]:
                    st.image(image) 
                    with st.popover("Résumé", use_container_width = True):
                        # st.text(syn)
                        st.markdown(f"<div style='word-wrap: break-word;'>{syn}</div>", unsafe_allow_html=True) 
    
    # st.text("Family")
    
    # aff2 = df_fusion_explode[df_fusion_explode['genres'] == "Family"]
    # aff2 = aff2.sort_values(by = "best_vote_count", ascending=False)
    # base_url = "https://image.tmdb.org/t/p/original/"
    # aff2['poster_path'] = aff2['poster_path'].astype(str)
    # images_x = [base_url + row['poster_path'] for index, row in aff2.iterrows()]
    # image_width = 200
    # # for index, row in aff2.iterrows():
    # # st.image(row['poster_path'], width=200)
    # num_columns = 5
    # columns = st.columns(num_columns)
    #             # Afficher les images et les synopsis côte à côte
    # for i, image in enumerate(images_x):
    #     if i <= 4 :
    #         with columns[i % num_columns]:
    #             st.image(image, width=image_width)   
    


with tab2:

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # recommandations
    a,col_cent,c = st.columns([1,2,1])
    with col_cent:
        classic,vip = st.tabs(["Trouvez un film similaire", "Carré VIP"])

        with classic :

            def recommandation(id_film) :

                index_film = df_ml[df_ml.tconst == id_film].index[0]

                film_into_X_format = scaled_X[index_film].reshape(1, -1)

                recommandation_KNN = KNN_model.kneighbors(film_into_X_format)

                return list(recommandation_KNN[1][0])
            

            film_name_year =st.selectbox("Entrez le titre d'un film, on vous recommandera des films similaires : ", 
                                (df_fusion_explode[["title","year"]].apply(lambda col : col[0] + " (" + str(col[1]) + ")",  axis = 1).unique()), 
                                index=None, 
                                placeholder="Ici, l'aventure au bout du clavier !")
            

            def afficher_recom(film_nam_yea):
                try:
                    film_name = film_nam_yea[:-7]
                    year = film_nam_yea[-5:-1]
                    select_input = df_fusion_explode[(df_fusion_explode['title'].str.contains(film_name, na=False))
                                                    & (df_fusion_explode["year"] == int(year))] #Vérifie que le titre est présent dans le DF
                    # st.write(select_input.tconst.values[0])
                    
                    list_id_recommandation = recommandation(select_input.tconst.values[0])
                    # st.write(list_id_recommandation)
                    liste_tconst_recommandation = df_ml.iloc[list_id_recommandation[1:],:].tconst.values
                    st.subheader("Vous avez aimé : ")
                    st.text("")
                    afficher_films(df_fusion_explode[df_fusion_explode.tconst == select_input.tconst.values[0]])
                    st.text("")
                    st.subheader("Vous aimerez aussi... ")
                    st.text("")
                    afficher_films(df_fusion_explode[df_fusion_explode.tconst.isin(liste_tconst_recommandation)])
                    
                except: # ICI c'est juste pour par que ce affiche le début du df avant l'input
                    pass 


            if film_name_year:  # Vérifie si l'entrée de l'utilisateur n'est pas vide
                afficher_recom(film_name_year)

        with vip :
            #Si un utilisateur est connecté
            if st.session_state.user_id != -1 :
                st.button("Actualiser votre recommandation")
                def get_user_gouts():
                    res = []
                    gouts = ["selection_genres","selection_decennies","films_favoris"]
                    for gout in gouts:
                        try :
                            res.append(df_clients.loc[df_clients.index == st.session_state.user_id,gout].values[0].split("*&$"))
                        except :
                            res.append([])
                    return res[0],res[1],res[2]
                
                ses_genres, ses_decennies, ses_films = get_user_gouts()
                #decennies = [an[2] for an in ses_decennies]

                #st.markdown(f"<h1 style='color: white; font-size: 1.1rem;text-decoration: underline;'>{df_clients.iloc[st.session_state.user_id].prenom}, ne manquez pas nos recommandations, rien que pour vous !:</h1>",
                #       unsafe_allow_html=True)
                #
                #if len(ses_films) == 0 :
                #    
                #    film_for_user = df_fusion_explode[df_fusion_explode['genres'].isin(ses_genres)]
                ##    film_for_user = film_for_user[df_fusion_explode['best_vote_count'] > 35000.0]
                #    #film_for_user = film_for_user[df_fusion_explode['year'].to_string()[2] in decennies]
            #     film_for_user = film_for_user.drop_duplicates(subset='title').sample(n=5)
                #    afficher_films(df_fusion_explode[df_fusion_explode.tconst.isin(film_for_user.tconst.values)])

                #Les films appréciés par l'utilisateur liste des tconst
                user_pos_tconst = df_fusion_explode[(df_fusion_explode.year.isin([int(year[-5:-1]) for year in ses_films]))
                                            &(df_fusion_explode.title.isin([film[:-7] for film in ses_films]))].tconst.unique()

                #récupérons les index correspondant dans le df_ml (et donc dans le scaled_X)
                user_pos_index = df_ml[df_ml.tconst.isin(user_pos_tconst)].index

                #on convertis les films favoris au format scaled :
                user_pos__X_format = scaled_X[user_pos_index][0]

                for row in scaled_X[user_pos_index][1:]:
                    user_pos__X_format += row

                user_pos__X_format /= len(scaled_X[user_pos_index])

                recommandation_KNN = KNN_model.kneighbors(user_pos__X_format.reshape(1, -1))

                res = list(recommandation_KNN[1][0])

                liste_tconst_recommandation = df_ml.iloc[res,:].tconst.values

                afficher_films(df_fusion_explode[df_fusion_explode.tconst.isin(liste_tconst_recommandation)
                                                & (~df_fusion_explode.tconst.isin(user_pos_tconst))])



with tab3:
    
    
    col_11111, col_22222,col_33333  = st.columns([2, 5, 2])
    with col_22222:


        st.header("Contact :", divider=True)
        col_1111, col_2222,  = st.columns([1, 1])

        with col_1111:
            
            st.markdown("<h1 style='text-align: center; color: white; font-size: 15px;'>Tel :   05 55 66 78 76</h1>", unsafe_allow_html=True)
            #st.markdown("<br><br>", unsafe_allow_html=True)
            
            st.markdown("<h1 style='text-align: center; color: white; font-size: 15px;'>Email :   mairiedelacourtine@orange.fr</h1>", unsafe_allow_html=True)
            #st.markdown("<br><br>", unsafe_allow_html=True)
            
            st.markdown("<h1 style='text-align: center; color: white; font-size: 15px;'>Adesse :   17 Rue des Deux Frères, 23100 La Courtine</h1>", unsafe_allow_html=True)
            st.markdown("<br><br>", unsafe_allow_html=True)
        
        with col_2222:
            image = "https://lacourtine.fr/pages/68.jpg"
            st.markdown(f'<img src="{image}" alt="GIF" width="300">', unsafe_allow_html=True)
    
        # Créer les données sous forme de dictionnaire pour les horaires
        data_horaires = {
            'Lundi': ['9:00 - 12:00 et 14:00 - 16:30'],
            'Mardi': ['9:00 - 12:00 et 14:00 - 16:30'],
            'Mercredi': ['9:00 - 12:00 et 14:00 - 16:30'],
            'Jeudi': ['9:00 - 12:00 et 14:00 - 16:30'],
            'Vendredi': ['9:00 - 12:00 et 14:00 - 16:30']
        }
        

        # Créer un DataFrame d'horaires
        df_horaires = pd.DataFrame(data_horaires, index=['Horaires d’ouverture'])
        

        st.header("Horaires d’ouverture de la mairie :", divider=True)
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: white; font-size: 18px;'>N'hésitez pas à vous rendre à la mairie pendant les horaires d'ouverture pour obtenir des renseignements sur le cinéma situé à la mairie.</h1>", unsafe_allow_html=True)

        
        # Afficher le dataframe avec Streamlit
        # Définition des colonnes pour centrer les dataframes
        col_1, col_2, col_3 = st.columns([1, 20, 1])
        with col_2 : 
            st.dataframe(df_horaires, use_container_width=True)
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        st.header("Horaire de séance :", divider=True)
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        st.markdown("<h1 style='text-align: center; color: white;; font-size: 20px'>Trois séances avec deux films différents vous sont proposées les :</h1>", unsafe_allow_html=True)
    
        # Créer les données sous forme de dictionnaire pour les séances
        data = {
            'Jeudi': ['20:30'],
            'Vendredi': ['20:30'],
            'Samedi': ['17:00']
        }

        # Créer un DataFrame de séances
        df = pd.DataFrame(data, index=['Heure'])

        # Définition des colonnes pour centrer les dataframes
        col_11, col_22, col_33 = st.columns([1, 2, 1])

        # Afficher le dtatframe avec Streamlit
        with col_22 :
            st.dataframe(df, use_container_width= True)
        st.markdown("<br><br>", unsafe_allow_html=True)

        
        # Créer les données sous forme de dictionnaire pour les tarifs
        data_tarif = {
            'Adulte': ['5 euros'],
            'Adulte en groupe': ['3 euros'],
            'étudiant': ['4 euros'],
        }


        # Créer un DataFrame des tarifs
        data_tarif = pd.DataFrame(data_tarif, index=['Tarifs'])


        st.header("Tarifs :", divider=True)
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        st.markdown("<h1 style='text-align: center; color: white;; font-size: 20px'>Les tarifs sont très attrayants !</h1>", unsafe_allow_html=True)
        
        # Afficher le dataframe avec Streamlit
        # Définition des colonnes pour centrer les dataframes
        col_111, col_222, col_333 = st.columns([1, 2, 1])
        with col_222:
            st.dataframe(data_tarif,use_container_width=True)


with tab4:


    etape = st.empty()

    @st.experimental_fragment
    def compte_tab():
        
        etape.empty()
        sleep(0.1)


        if "user_id" not in st.session_state:
            st.session_state.user_id = -1

        if "user_email" in st.session_state :
            verify_login(st.session_state.user_email,st.session_state.user_mdp)
        
        
        if "new_user_email" in st.session_state :
            verify_login(st.session_state.new_user_email,st.session_state.new_user_mdp)


        if st.session_state.user_id == -1:
            etape.empty()
            sleep(0.1)
            with etape.container() :
                st.write("")
                st.write("")
                col_g, col_login, col_d = st.columns([1,1,1])
                with col_login :
                    login_tab, create_tab = st.tabs(["Connectez-vous","Inscrivez-vous"])
                    with login_tab :
                        with st.form(key="login_form"):
                            st.text_input("Email",
                                          key = "user_email")
                            st.text_input("Mot de passe",
                                          key = "user_mdp",
                                          type="password")
                            st.form_submit_button("Se connecter",
                                                    use_container_width = True)

                    with create_tab :
                        with st.form(key="create_form"):

                            #----identité------#
                            st.markdown(f"<h1 style='color: white; font-size: 1.3rem;text-decoration: underline;'>Identité :</h1>",
                                    unsafe_allow_html=True)
                            new_nom = st.text_input("Nom*",
                                          key = "new_user_nom")
                            new_prenom = st.text_input("Prénom*",
                                          key = "new_user_prenon")
                            new_date_naiss = st.date_input("Date de naissance",
                                                           format="DD/MM/YYYY",
                                                           min_value = datetime.date(1900, 1, 1),
                                                           key = "new_user_date_naiss")
                            
                            
                            #----Coordonnées------#
                            st.markdown(f"<h1 style='color: white; font-size: 1.3rem;text-decoration: underline;'>Coordonnées :</h1>",
                                    unsafe_allow_html=True)
                            new_mail = st.text_input("Email*",
                                          key = "new_user_mail")
                            new_tel = st.text_input("Tél",
                                          key = "new_user_tel")
                            new_code_postal = st.number_input("Code postal (actuel)",
                                                              step = 1,
                                                              min_value = 0,
                                                              max_value = 99999,
                                                              key = "new_user_code_postal")
                            
                            #----Mot de passe------#
                            st.markdown(f"<h1 style='color: white; font-size: 1.3rem;text-decoration: underline;'>Mot de passe :</h1>",
                                    unsafe_allow_html=True)
                            new_mdp = st.text_input("Mot de passe*",
                                          key = "new_user_mdp",
                                          type="password")
                            new_mdp_conf = st.text_input("Confirmez votre mot de passe*",
                                          key = "new_user_mdp_conf",
                                          type="password")
                            
                            #----Traitement des données------#
                            st.markdown(f"<h1 style='color: white; font-size: 1.3rem;text-decoration: underline;'>Traitement des données :</h1>",
                                    unsafe_allow_html=True)
                            new_accor_recom = st.toggle("J'accepte que mes données soient utilisées pour me faire des recommandations de films plus pertinentes.*",
                                                    value= False,
                                                    key = "new_accor_recom")
                            new_accor_mail = st.toggle("Je souhaite recevoir les mails d'informations et d'offres.",
                                                    value= False,
                                                    key = "new_accor_mail")
                            
                            st.write("*: Champs obligatoires.")

                            #----soumission du formulaire------#
                            sub = st.form_submit_button("Créer mon compte",
                                                  use_container_width = True,
                                                  )

                        if sub :
                            creer_compte(new_nom,
                                         new_prenom,
                                         new_date_naiss,
                                         new_mail,
                                         new_tel,
                                         new_code_postal,
                                         new_mdp,
                                         new_mdp_conf,
                                         new_accor_recom,
                                         new_accor_mail)
                            st.session_state.user_id = df_clients[df_clients["email"] == new_mail].first_valid_index()
                            page_client()
        else :
            page_client() 

        #Parfait pour débugger !!!!
        #st.write(st.session_state)                  
    
    def verify_login(user_mail,user_pass):
        if user_mail in df_clients["email"].values and df_clients[df_clients["email"] == user_mail].password.values[0] == user_pass :
                st.session_state.user_id = df_clients[df_clients["email"] == user_mail].first_valid_index()


    def logout():
        for key in st.session_state.keys():
            del st.session_state[key]


    def creer_compte(nom, prenom,
                     date_naiss,
                     mail, tel, code_postal,
                     mdp, mdp_conf,
                     accor_recom, accor_mail):
        global df_clients

        mandatory_inputs = [nom,prenom,mail,mdp,mdp_conf]
        
        #----CHAMPS OBLIGATOIRES REMPLIS----------#
        if sum([input != None for input in mandatory_inputs]) == 5 :

            if not 0 in [len(input) for input in mandatory_inputs]:

                if mail not in df_clients.email.values:

                    if accor_recom :

                        new_user = {
                                    'nom': [nom],
                                    'prenom': [prenom],
                                    'date_naiss' : [date_naiss],
                                    'tel' : [tel],
                                    'code_postal' : [code_postal],
                                    'password': [mdp],
                                    'email': [mail],
                                    'accor_recom': [accor_recom],
                                    'accor_mail': [accor_mail]
                                    }
                        df_clients = pd.concat([df_clients, pd.DataFrame.from_dict(new_user, orient = "columns")])
                        df_clients.to_csv(r"/Users/sprumontjimmy/Documents/Data_analyst/Projet 2/Streamlit/keys.csv", index=False)
                        df_clients = pd.read_csv(r"/Users/sprumontjimmy/Documents/Data_analyst/Projet 2/Streamlit/keys.csv")

                        st.session_state.user_id = len(df_clients.index)

    
    def page_client():
        etape.empty()
        sleep(0.1)
        
        global df_clients
        df_clients = pd.read_csv(r"/Users/sprumontjimmy/Documents/Data_analyst/Projet 2/Streamlit/keys.csv")

        with etape.container() :
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='text-align: center; color: white; font-size: 2rem;text-decoration: underline overline #FFFFFF;'>Heureux de vous voir {df_clients.iloc[st.session_state.user_id].prenom} !</h1>",
                        unsafe_allow_html=True)
            
            c_1,c_2,c_3 = st.columns([4,1,4])
            
            #------DECONNEXION-----#
            with c_2 :
                st.button("Déconnexion",
                          on_click = logout,
                          use_container_width = True,
                          key ="deco_but")
                
            st.write("")            
            col_01, col_milieu, col_03 = st.columns([1,2,1])
            with col_milieu :
                profil, preferences = st.tabs(["Mon Profil","Mes Préférences"])
                with profil :
                    vg,col_g, col_d,vd = st.columns([.15,1,1,.15])
                    with col_g :
                        
                        st.markdown(f"<h1 style='color: white; font-size: 1.5rem;text-decoration: underline;'>Votre identité :</h1>",
                                    unsafe_allow_html=True)
                        st.write(f"Nom : {df_clients.iloc[st.session_state.user_id].nom}")
                        st.write(f"Prénom : {df_clients.iloc[st.session_state.user_id].prenom}")
                        st.write(f"Date de naissance : {df_clients.iloc[st.session_state.user_id].date_naiss}")


                    with col_d :

                        st.markdown(f"<h1 style='color: white; font-size: 1.5rem;text-decoration: underline;'>Vos coordonnées :</h1>",
                                    unsafe_allow_html=True)
                        st.write(f"Email : {df_clients.iloc[st.session_state.user_id].email}")
                        st.write(f"Tél : {df_clients.iloc[st.session_state.user_id].tel}")
                        st.write(f"Code postal : {df_clients.iloc[st.session_state.user_id].code_postal}")
                
                    vg,col_g, col_d,vd = st.columns([.15,1,1,.15])
                    with col_g :                        
                        st.write(f"J'accorde l'usage de mes données pour des recommandations de films plus pertinentes : {'Oui' if df_clients.iloc[st.session_state.user_id].accor_recom else 'Non'}")

                    with col_d :                        
                        st.write(f"Je souhaite recevoir les mails d'informations et d'offres : {'Oui' if df_clients.iloc[st.session_state.user_id].accor_mail else 'Non'}")
                
                    c_01,c_02,c_03 = st.columns([1,3,1])
                    with c_02 :
                        
                        st.markdown(f"<h1 style='text-align: center; color: white; font-size: 1.2rem;text-decoration: underline overline;'>Supprimer mon Compte.</h1>",
                                    unsafe_allow_html=True)
                        st.write("")
                        nuke_it = st.text_input(label = "nuke_it",
                                                key = "big_boy",
                                                on_change= nuke_that_account,
                                                placeholder = "Pour supprimer votre compte, entrez 'supprimer'",
                                                label_visibility = "collapsed")
                        st.markdown(f"<h1 style='text-align: center; color: white;font-size: 1rem;'>(Attention, vos données seront définitivement supprimées.)</h1>",
                                    unsafe_allow_html=True)


                with preferences :
                        with st.form(key="user_pref"):

                            #----identité------#
                            st.markdown(f"<h1 style='color: white; font-size: 1.3rem;text-decoration: underline;'>Aidez nous à vous aidez !</h1>",
                                    unsafe_allow_html=True)
                            
                            st.write()

                            def get_user_preferences(selec):
                                try :
                                    return df_clients.loc[df_clients.index == st.session_state.user_id,selec].values[0].split("*&$")
                                except :
                                    return []
                                
                            list_genres = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy',
                                           'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy', 'Film-Noir',
                                           'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance',
                                           'ScienceFiction', 'Sport', 'Thriller', 'War', 'Western']
                            
                            selection_genres = st.multiselect("Quels sont vos genres favoris ?",
                                                              list_genres,
                                                              placeholder = "Un peu, beaucoup, passionnément... à vous de voir, nos propositions s'adapteront !",
                                                              key = "selection_genres",
                                                              default = get_user_preferences("selection_genres")
                                                              )
                            
                            
                            list_decennies = [str(1950+10*nb) for nb in range(8)]

                            selection_decennies = [] #st.multiselect("Selon vous, où se situe l'âge d'or du cinéma ?",
                                                         #     list_decennies,
                                                          #    placeholder = "A remplir seul. Sous peine de débat cinématiques endiablés...",
                                                          #    key ="selection_decennies",
                                                           #   default = get_user_preferences("selection_decennies")
                                                            #  )
                            
                            films_favoris = st.multiselect('Saisissez vos films préférés : ',
                                                           (df_fusion_explode[["title","year"]].apply(lambda col : col[0] + " (" + str(col[1]) + ")",
                                                                    axis = 1).unique()),
                                                            placeholder = "Dans le doute, pensez aux derniers films que vous avez vu.",
                                                            key = "films_favoris",
                                                              default = get_user_preferences("films_favoris")
                                                              )


                            #----soumission des cgoix------#
                            user_choices = st.form_submit_button("Enregistrer mes préférences",
                                                  use_container_width = True)

                        if user_choices:
                            df_clients.loc[df_clients.index == st.session_state.user_id,"selection_genres"] = "*&$".join(selection_genres)
                            df_clients.loc[df_clients.index == st.session_state.user_id,"selection_decennies"] = "*&$".join(selection_decennies)
                            df_clients.loc[df_clients.index == st.session_state.user_id,"films_favoris"] = "*&$".join(films_favoris)
                            df_clients.to_csv(r"/Users/sprumontjimmy/Documents/Data_analyst/Projet 2/Streamlit/keys.csv", index=False)
                            df_clients = pd.read_csv(r"/Users/sprumontjimmy/Documents/Data_analyst/Projet 2/Streamlit/keys.csv")
                

    def nuke_that_account():
        if st.session_state.big_boy == "supprimer":
            global df_clients
            index= st.session_state.user_id
            logout()
            df_clients.drop(index= index, inplace= True)
            df_clients.to_csv(r"/Users/sprumontjimmy/Documents/Data_analyst/Projet 2/Streamlit/keys.csv", index=False)
            df_clients = pd.read_csv(r"/Users/sprumontjimmy/Documents/Data_analyst/Projet 2/Streamlit/keys.csv")

    compte_tab()
