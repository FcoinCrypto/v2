import re
import json
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

cred = credentials.Certificate('fpay.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

def save_to_firestore(sms_data):
    logging.debug("Sauvegarde des données dans Firestore...")
    doc_ref = db.collection('sms_data').document()
    doc_ref.set(sms_data)
    logging.debug("Sauvegarde terminée.")

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    print(data)
    if data is None:
        return 'No JSON data received'

    messages = data.get('sms', [])

    if len(messages) == 0:
        return 'No messages found'

    for message in messages:
        sms_id = message.get('incoming_sms_id')
        timestamp = message.get('timestamp')
        text = message.get('text')

        # Extraire les informations du texte du message
        montant, nom, numero, solde, ref, raison, frais = extract_information_from_text(text)

        # Classer le message en fonction du type de transaction
        if "recu de" in text:
            transaction = "reception-mobile money"
        elif "envoye a" in text:
            transaction = "transfert-mobile money"
        else:
            transaction = "inconnu"

        # Créer un dictionnaire avec les informations du message
        sms_data = {
            "SMS ID": sms_id,
            "Timestamp": timestamp,
            "Montant": montant if montant is not None else "Null",
            "Nom": nom if nom else "Rien à afficher",
            "Numero": numero if numero else "Rien à afficher",
            "Solde": solde if solde is not None else "Null",
            "Ref": ref if ref else "Rien à afficher",
            "Raison": raison if raison else "Rien à afficher",
            "Frais": frais if frais is not None else "Null",
            "Transaction": transaction,
            "Port": message.get('port'),
            "IMSI": message.get('imsi')
        }

        # Afficher les informations du message s'il y a des données à afficher
        if montant is None and nom is None and numero is None and solde is None and ref is None and raison is None and frais is None:
            continue

        print(json.dumps(sms_data, indent=4))

        # Enregistrer les données dans Firestore
        save_to_firestore(sms_data)

        # Vérifier et ajouter les données à la collection 'simbox' si nécessaire
        balance_info = message.get('balance')
        if balance_info is not None or balance_info == "0":
            port = message.get('port')
            number = message.get('number')
            smsc = message.get('smsc')
            balance_data = {
                'port': port,
                'number': number,
                'smsc': smsc,
                'timestamp': timestamp,
                'balance': solde
            }
            collection_name = 'mvola' if str(port) in ['0', '1', '2', '3'] else 'simbox'
            db.collection(collection_name).add(balance_data)

    return 'Message processing completed'



