import streamlit as st
import requests
import os
import re
from datetime import datetime

# Fonction pour obtenir le token d'authentification
def get_auth_token(email, password, base_url):
    url_auth = f"{base_url}/api/login"
    headers = {'Content-Type': 'application/json'}
    data_auth = {'email': email, 'password': password}

    response = requests.post(url_auth, json=data_auth, headers=headers)
    if response.status_code == 200:
        return response.json().get("token")
    else:
        return None

# Fonctions pour extraire les informations des fichiers
def extraire_date(contenu, pattern="S20.G00.05.005"):
    for ligne in contenu.splitlines():
        if pattern in ligne:
            match = re.search(r'\d{8}', ligne)
            if match:
                date_str = match.group(0)
                try:
                    return datetime.strptime(date_str, '%d%m%Y').strftime('%m%Y')
                except ValueError:
                    pass
    return None

def extraire_info_specifique(contenu, pattern="S21.G00.11.001"):
    for ligne in contenu.splitlines():
        if ligne.startswith(pattern):
            info_start_index = ligne.find(pattern) + len(pattern)
            return ligne[info_start_index:info_start_index + 5]
    return None

def lire_fichiers_et_verifier(fichiers):
    donnees_clients = []
    info_specifique_precedent = None
    erreur_detectee = False

    for fichier in fichiers:
        # Lire le contenu du fichier
        contenu = fichier.read().decode("utf-8")  # Utiliser read() ici

        if "erreur" in contenu.lower():  # Adaptez le critère d'erreur selon vos besoins
            st.error(f"Erreur détectée dans le fichier {fichier.name}. Arrêt de l'import.")
            erreur_detectee = True
            break

        date = extraire_date(contenu)
        info_specifique = extraire_info_specifique(contenu)

        if date and info_specifique:
            if info_specifique_precedent and info_specifique != info_specifique_precedent:
                nouveau_nic = st.text_input(f"Le NIC a changé dans le fichier {fichier.name}. Veuillez entrer le nouveau NIC pour continuer.", key=fichier.name)
                if not nouveau_nic:
                    st.warning("Import en attente de la mise à jour du NIC.")
                    break
            donnees_clients.append({'nom_fichier': fichier.name, 'date': date, 'info': info_specifique})
            info_specifique_precedent = info_specifique

    return donnees_clients, erreur_detectee

def trier_par_date(donnees_clients):
    return sorted(donnees_clients, key=lambda x: datetime.strptime(x['date'], '%m%Y'))

# Page d'authentification
# Page d'authentification
def page_authentification():
    st.title('Authentification')

    base_urls = {
        "prod": "https://app.listo.pro",
        "preprod": "https://preprod.listo.pro",
        "staging": "https://staging.listo.pro"
    }

    environment = st.sidebar.selectbox("Choisir l'environnement", list(base_urls.keys()))
    base_url = base_urls[environment]

    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Mot de Passe", type="password")

    if st.sidebar.button('Se connecter'):
        token = get_auth_token(email, password, base_url)
        if token:
            st.success('Connecté avec succès!')
            st.session_state['token'] = token
            st.session_state['environment'] = environment  # Stocker le nom de l'environnement
        else:
            st.error("Échec de l'authentification")

# Page d'import de fichiers
def page_import_fichiers():
    st.title('Import de Fichiers')

    # Afficher l'environnement actuel
    if 'environment' in st.session_state:
        st.sidebar.write(f"Connecté à l'environnement : {st.session_state['environment']}")

    # Vérifier si l'utilisateur est authentifié
    if 'token' in st.session_state:
        uploaded_files = st.file_uploader("Choisir les fichiers", accept_multiple_files=True, type=['txt'])
        if uploaded_files:
            donnees_clients, erreur_detectee = lire_fichiers_et_verifier(uploaded_files)
            if not erreur_detectee:
                donnees_clients_triees = trier_par_date(donnees_clients)
                for client in donnees_clients_triees:
                    st.text(f"{client['nom_fichier']} - {client['date']} - {client['info']}")
    else:
        st.warning("Veuillez vous authentifier pour accéder à cette page.")

# Fonction principale
def main():
    st.sidebar.title("Menu")
    choix_page = st.sidebar.radio("Choisir une page", ["Authentification", "Import de Fichiers"])

    if choix_page == "Authentification":
        page_authentification()
    elif choix_page == "Import de Fichiers":
        page_import_fichiers()

if __name__ == "__main__":
    main()
