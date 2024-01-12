import streamlit as st
import requests

def get_auth_token(email, password, base_url):
    url_auth = f"{base_url}/api/authenticate"  # Assurez-vous que le chemin d'accès à l'API est correct
    data_auth = {'email': email, 'password': password}
    response = requests.post(url_auth, data=data_auth)
    if response.status_code == 200:
        return response.json().get("token")
    else:
        return None

def main():
    st.title('Authentification')

    # Sélecteur pour l'environnement
    environment = st.sidebar.selectbox(
        "Choisir l'environnement",
        ("prod", "preprod", "staging")
    )

    # URL de base selon l'environnement
    base_urls = {
        "prod": "https://app.listo.pro",
        "preprod": "https://preprod.listo.pro",
        "staging": "https://staging.listo.pro"
    }
    base_url = base_urls[environment]

    # Champs de saisie pour l'email et le mot de passe
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Mot de Passe", type="password")

    if st.sidebar.button('Se connecter'):
        token = get_auth_token(email, password, base_url)
        if token:
            st.success('Connecté avec succès!')

            # Votre logique de traitement ici
            # ...
        else:
            st.error("Échec de l'authentification")

if __name__ == "__main__":
    main()
