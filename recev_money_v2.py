import requests
import firebase_admin
from firebase_admin import credentials, firestore
import time

# Initialisation de Firebase Admin SDK
cred = credentials.Certificate("fpay.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# URL de l'API à vérifier
url = "http://localhost:70/"

# Données actuelles de l'API
donnees_actuelles = {}

while True:
    try:
        # Envoyer une requête à l'API
        response = requests.get(url)
        
        # Convertir la réponse en un dictionnaire Python
        nouvelles_donnees = response.json()
        print(nouvelles_donnees)

        # Vérifier si les nouvelles données sont différentes des données actuelles
        if nouvelles_donnees != donnees_actuelles:
            # Ajouter une condition pour vérifier si la transaction est un "transfert"
          
                # Rechercher l'utilisateur dans la collection "Users"
                users_ref = db.collection("Users").where("phone_number", "==", nouvelles_donnees["Numero"])
                users = users_ref.get()

                for user in users:
                    # Mettre à jour le champ "wallet_balance" de l'utilisateur trouvé
                    user_ref = db.collection("Users").document(user.id)
                    wallet_balance = user.to_dict().get("wallet_balance", 0)
                    nouveau_solde = wallet_balance + nouvelles_donnees["Montant"]
                    user_ref.update({"wallet_balance": nouveau_solde})

                    # Récupérer l'email de l'utilisateur pour le champ sender_email
                    sender_email = user.to_dict().get("email")

                    # Ajouter un nouveau document dans la collection "wallet"
                    wallet_ref = db.collection("wallet").document()
                    wallet_data = {
                        "amount": nouvelles_donnees["Montant"],
                        "sender_email": sender_email,
                        "timestamp": nouvelles_donnees["Timestamp"],
                        "transaction": "Vente mobile money",
                        "user_email": sender_email,
                    }
                    wallet_ref.set(wallet_data)

                # Mettre à jour les données actuelles de l'API
                donnees_actuelles = nouvelles_donnees
        else:
                print('Pas de mise à jour')

    except requests.exceptions.RequestException as e:
        print(f"Une erreur s'est produite lors de la requête : {e}")

    # Attendre 4 secondes avant la prochaine vérification
    time.sleep(4)
