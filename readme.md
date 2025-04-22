# 📊 YouTube Likes Extractor

Un script Python qui permet d'extraire automatiquement le **nombre de likes** des vidéos YouTube **dont vous êtes propriétaire**, à partir d'un fichier Excel contenant les liens vers les vidéos.

---

## 🚀 Fonctionnalités

- Lecture d'un fichier Excel avec les liens des vidéos YouTube
- Authentification sécurisée via OAuth2 (Google)
- Extraction du **titre** et du **nombre de likes** actuels
- Génération d’un fichier Excel de résultats avec :
  - ✅ Classement par nombre de likes
  - 🕒 Timestamp de génération
  - 📄 Feuille d’information (date, source, nombre de vidéos)

---

## 📁 Structure attendue du fichier Excel

Le fichier Excel source (dans le dossier `data/`) doit contenir une colonne :

| Titre                         | Lien                                      |
|------------------------------|-------------------------------------------|
| INCROYABLE VIDEO YOUTUBE ... | https://www.youtube.com/watch?v=xxxxxxx   |
| AUTRE INCROYABLE VIDEO Y...  | https://www.youtube.com/watch?v=yyyyyyy   |

- La colonne contenant les URL **doit être nommée `Lien` (case sensitive)**
- Le titre peut être présent ou non, il n'est pas utilisé (optionnel)

---

## ⚙️ Prérequis

- Python 3.8+
- Un compte Google avec une chaîne YouTube et des vidéos publiées
- Un projet Google Cloud avec l'API **YouTube Data API v3** activée
- Un fichier `client_secret.json` dans le dossier `credentials/` (fourni par Google Cloud Console)

### 📦 Installation des dépendances

```bash
pip install -r requirements.txt
