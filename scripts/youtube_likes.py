import re
import pandas as pd
import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scope mis à jour pour accéder aux statistiques YouTube
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

#extracts the video id from a youtube URL
def extract_video_id(url):
    # Works for URLs like: youtu.be/ID or youtube.com/watch?v=ID
    patterns = [
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'v=([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

#extracts the video url from an excel file
#the column containing the url must be named "Lien" (case sensitive)
def process_excel(file_path):
    ids = []
    df = pd.read_excel(file_path)
    for index, row in df.iterrows():
        url = str(row['Lien'])
        video_id = extract_video_id(url)
        if video_id:
            ids.append(video_id)
        else:
            print(f"⚠️ Could not extract video ID from: {url}")
    print("Nombre de vidéos:", len(ids))
    return ids

#use google OAuth
def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials/client_secret.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

#send request and print data
def get_video_data(video_ids, creds):
    data = []
    
    #si la liste d'id est vide
    if (len(video_ids) < 1):
        print("Aucun id de vidéo n'a été trouvé, votre excel est-il correctement formatté ?")
        return data # liste vide
    else:
        for video_id in video_ids:
            youtube = build('youtube', 'v3', credentials=creds)
            response = youtube.videos().list(
                part='statistics,snippet',
                id=video_id
            ).execute()

            item = response['items'][0]
            title = item['snippet']['title']
            stats = item['statistics']
            like_count = stats.get('likeCount', 'Not available')
            
            #ajouter les données de la vidéo
            data.append({"title": title, "likes": int(like_count), "id": video_id})

            print(f"🎬 \"{title}\" – https://youtu.be/{video_id}")
            print(f"👍 Likes: {like_count}")
            
        return data

#ecrit les résultats dans nouveau ficher excel
#column 0 : rank, column 1 : likes, column 2 : video name, column 3 : video link
def output_results(entry_file_name, video_data):
    
    #si la liste de données est vide
    if len(video_data) < 1:
        print("Aucune donnée sur les vidéos n'a été trouvée, votre excel est-il correctement formatté ?")
    else:
        #trier video_data par nombre de likes décroissant
        sorted_data = sorted(video_data, key=lambda x: x['likes'], reverse=True)
        
        #pour chaque vidéo, écrire les données dans le excel, avec un lien de la forme "https://youtu.be/{video_id}"
        #Construire le DataFrame avec les colonnes demandées
        output_rows = []
        for rank, video in enumerate(sorted_data, start=1):
            output_rows.append({
                "Rang": rank,
                "Likes": video['likes'] if video['likes'] != -1 else "Non disponible",
                "Titre": video['title'],
                "Lien": f"https://youtu.be/{video['id']}"
            })

        df_output = pd.DataFrame(output_rows)
        
        # -------- Données de comptage faisant foi -------- #
        # Générer le timestamp actuel
        timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        timestamp_filename = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
        timestamp_dir = datetime.now().strftime('%d-%m-%Y')
        
        # Feuille d'information
        df_info = pd.DataFrame({
            "Clé": ["Date de génération", "Fichier source", "Nombre de vidéos"],
            "Valeur": [timestamp, f"{entry_file_name}.xlsx", len(video_data)]
        })
        
        # Créer le dossier "results" s'il n'existe pas
        results_dir = "results"
        os.makedirs(results_dir, exist_ok=True)
        
        #Créer le dossier du jour s'il n'existe pas
        file_dir = f'{results_dir}/{timestamp_dir}'
        os.makedirs(file_dir, exist_ok=True)

        # Écriture dans un fichier Excel avec deux feuilles
        output_file = os.path.join(file_dir, f"results_{entry_file_name}_{timestamp_filename}.xlsx")
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df_output.to_excel(writer, sheet_name='Résultats', index=False)
            df_info.to_excel(writer, sheet_name='Infos', index=False)
    

#entry point
if __name__ == '__main__':
    creds = authenticate()
    excel_name = input("Depuis quel fichier excel (obligatoirement situé dans le dossier data) voulez-vous récupérer les vidéos ?\nAttention: marquer uniquement le nom du ficher => video pour video.xlsx\n")
    video_ids = process_excel(f'data/{excel_name}.xlsx')
    video_data = get_video_data(video_ids, creds)
    output_results(excel_name, video_data)
