import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import pyplot as plt
import seaborn as sns
from langdetect import detect
import dash
import pytz
from datetime import datetime


# Chargement du dataset
df= pd.read_excel('2022_07_01_fr_Channels_TOTAL_WIZDEO.xlsx')

# Filtrage des colonnes nécessaires pour notre analyse de survie d'une chaîne 

df_filter= df.filter(['display_name','subscribers','created','category','content_owner_id','videos_views','videos','comments','likes','dislikes','Derniere Video','Date de publication', "nbVidSince_2021-06-30"])


# On supprime toutes les catégories 'musique' car non pertinantes pour nos analyses 
# Comme expliqué dans le mémoire elles peuvent être biaisante par rapport au ratio de vues/vidéos
df_filter=df_filter[(df_filter['category'] != 'musique')]

# On supprime les chaînes ayant aucune vidéo car pouvant être des bots/fake channel
df_filter=df_filter[(df_filter['Derniere Video']!='Pas de video')]


# On supprime les chaines en doubles
# doublons = df_filter[df_filter['display_name'].duplicated(keep=False)]


# On supprime les chaines n'ayant pas d'abonnées
df_filter = df_filter.dropna(subset=['subscribers'])



# On regarde la médiane dans une premier temps du nombre d'abonnés de toutes les chaînes 
# Puis on ne sélectionne, dans df_top, que les chaînes supérieures à cette médiane
df_filter['subscribers'].median()
df_top= df_filter[(df_filter['subscribers']>df_filter['subscribers'].median())]

#df_filter_500 = df_filter.head(500)

# SAUVEGARDE DE df_filter 
df_filter.to_excel('df_filter.xlsx', index=False)

#df_filter_500.to_excel('df_filter_500.xlsx', index=False)





# Remarque du doctorant 
# Dans la category people et blogs -> on observe des chanteurs voici les partenaires que j'ai trouvé avec l'appelation music
df_top = df_top[~df_top['content_owner_id'].isin(['Believe Music','Because Music','Musicast','Emotional Music Channel','The Orchard Music','Djo Music','Aqua Music','Menta Music','WM Music Distribution','TheGoodMusic Within'])]



# Détermination des chaînes actives 
Actif_list = []

for i in df_top['Derniere Video'].tolist():
    try:
        langue = detect(i)
        Titre = i
    except:
        langue = 'Pas detecter'
        Titre = i
    # Ajoutez les données à une liste
    Actif_list.append({'Derniere Video': Titre, 'Langue': langue})

# Convertir la liste en DataFrame
Actif = pd.DataFrame(Actif_list)
    
# Affichage des chaînes actives 
#Actif

# Détermine les chaînes les plus actives 
top_channel = pd.merge(df_top, Actif, on='Derniere Video',how='outer')

# Comptage des langues comprises dans les chaînes des gros youtubeurs
#top_channel['Langue'].value_counts()

# Supression des grosses chaînes ayant la langue arabe 
# Remarque: Possibilité de suppression d'autres langues 
top_channel = top_channel[top_channel['Langue'] != 'ar']

top_channel['Date derniere video'] = pd.to_datetime(top_channel['Date de publication'])

# Convertir la colonne 'created' en datetime, en ignorant les erreurs et en retirant les fuseaux horaires
top_channel['created'] = pd.to_datetime(top_channel['created'], errors='coerce').dt.tz_localize(None)


# Pour chaque colonne dans le DataFrame
for col in top_channel.columns:
    # Si le type de la colonne est 'datetime64[ns, UTC]' ou similaire
    #if pd.api.types.is_datetime64tz_dtype(top_channel[col]):
    if isinstance(top_channel[col].dtype, pd.DatetimeTZDtype):
        # Retirez le fuseau horaire
        top_channel[col] = top_channel[col].dt.tz_localize(None)


#df_top_channel_500 = top_channel.head(500)

# SAUVEGARDE DE top_channel 
top_channel.to_excel('top_channel.xlsx', index=False)

#df_top_channel_500.to_excel('top_channel_500.xlsx', index=False)





top_channel2=top_channel
now = datetime.now().replace(tzinfo=None)

top_channel2['Date derniere video'] = top_channel2['Date derniere video'].dt.tz_localize(None)
# Soustraire la date et l'heure actuelles à la colonne
top_channel2['Temps depuis dernière vidéo (jours)'] = (now - top_channel2['Date derniere video']).dt.days.astype(int)

moyenne_category = top_channel2.groupby('category')['Temps depuis dernière vidéo (jours)'].mean()

df_moyenne_category = pd.DataFrame({'category': moyenne_category.index, 'moyenne': moyenne_category.values})




# Joindre top_channel2 avec df_median_category sur la colonne 'category'
top_channel3 = top_channel2.join(df_moyenne_category.set_index('category'), on='category')

# Créer une colonne 'Actif' avec des valeurs booléennes en fonction de la différence entre 'Temps depuis dernière vidéo (jours)' et 'mediane'
top_channel3['Actif'] = top_channel3['Temps depuis dernière vidéo (jours)'] < top_channel3['moyenne']

# Convertir les valeurs booléennes en 'Actif' et 'Inactif'
top_channel3['Actif'] = np.where(top_channel3['Actif'], 'Actif', 'Inactif')


# Comparaison du nombre de Chaines actives/ inactives
#top_channel3['Actif'].value_counts()


# Chaîne active
actif = top_channel3[(top_channel3['Actif']=='Actif')]
#actif
#df_actif_500 = actif.head(500)
# SAUVEGARDE DE actif
actif.to_excel('actif.xlsx', index=False)

#df_actif_500.to_excel('actif_500.xlsx', index=False)


# Chaînes Inactives 
inactif = top_channel3[(top_channel3['Actif']=='Inactif')]
#inactif
#df_inactif_500 = inactif.head(500)
# SAUVEGARDE DE inactif
inactif.to_excel('inactif.xlsx', index=False)

#df_inactif_500.to_excel('inactif_500.xlsx', index=False)

inactif = top_channel3[top_channel3['Actif'] == 'Inactif'].copy()




#df_yt.set_index('Year',inplace=True)
# Assurez-vous que 'Date derniere video' et 'created' sont au format datetime sans fuseau horaire
inactif['Date derniere video'] = pd.to_datetime(inactif['Date derniere video'], errors='coerce').dt.tz_localize(None)
inactif['created'] = pd.to_datetime(inactif['created'], errors='coerce').dt.tz_localize(None)

inactif.loc[:,"Année de fin de vie"] = inactif["Date derniere video"].dt.year
inactif.loc[:, "Année de début de vie"] = inactif["created"].dt.year



inactif.loc[:, 'Durée de vie de la chaine'] = (inactif['Date derniere video'] - inactif['created']).dt.days

inactif1=inactif.groupby(by=["Année de fin de vie","category"]).size().reset_index()
inactif1=pd.DataFrame(inactif1)

inactif1=inactif1.rename(columns={0:'Chaine'})
inactif1=inactif1.sort_values('Chaine',ascending=False)


""" inactif.loc[:,'created'] = pd.to_datetime(top_channel['created'])

inactif.loc[:,"Année de début de vie"] = inactif["created"].dt.year

inactif.loc[:,'Durée de vie de la chaine'] = (inactif['Date derniere video'].dt.date - inactif['created'].dt.date).dt.days
 """
inactif = inactif.loc[inactif['Année de début de vie'] != 1970]


# Grouper les données par année et calculer la moyenne de durée de vie
df_grouped = inactif.groupby('Année de fin de vie')['Durée de vie de la chaine'].mean().reset_index()
df_grouped = df_grouped.rename(columns={'Durée de vie de la chaine': 'Moyenne de vie'})

# Calculer les gains moyens en jours par rapport à l'année précédente
df_grouped['Gains moyens en jours'] = df_grouped['Moyenne de vie'].diff()


# Grouper les données par année et calculer la moyenne de durée de vie
df_grouped2 = inactif.groupby('Année de début de vie')['Durée de vie de la chaine'].mean().reset_index()
df_grouped2 = df_grouped2.rename(columns={'Durée de vie de la chaine': 'Moyenne de vie'})

# Calculer les gains moyens en jours par rapport à l'année précédente
df_grouped2['Gains moyens en jours (N-1)'] = df_grouped2['Moyenne de vie'].diff()


top_channel3.loc[:,'created'] = pd.to_datetime(top_channel3['created'])

top_channel3.loc[:,'year debut'] = top_channel3['created'].dt.year