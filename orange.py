import re
import json
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request

app = Flask(__name__)

# Remplacez 'path/to/your/firebase-config.json' par le chemin du fichier de configuration JSON
cred = credentials.Certificate('fpay.json')
firebase_admin.initialize_app(cred)

db = firestore.client()


def extract_information_from_text(text):
    montant = None
    nom = None
    numero = None
    solde = None
    ref = None
    raison = None
    frais = None

    if "Votre transfert " in text:
        montant_match = re.search(r"transfert de (\d+) Ar", text)
        numero_match = re.search(r"vers le (\d+)", text)
        frais_match = re.search(r"Frais : (\d+) Ar", text)
        solde_match = re.search(r"Nouveau solde: (\d+) Ar", text)
        ref_match = re.search(r"Trans id (\w+)", text)

        montant = int(montant_match.group(1)) if montant_match else None
        numero = numero_match.group(1) if numero_match else None
        frais = int(frais_match.group(1)) if frais_match else None
        solde = int(solde_match.group(1)) if solde_match else None
        ref = ref_match.group(1) if ref_match else None

    elif "recu un transfert " in text:
        montant_match = re.search(r"transfert de (\d+)Ar", text)
        numero_match = re.search(r"venant du (\d+)", text)
        solde_match = re.search(r"Nouveau Solde: (\d+)Ar", text)
        ref_match = re.search(r"Trans Id: (\w+)", text)

        montant = int(montant_match.group(1)) if montant_match else None
        numero = numero_match.group(1) if numero_match else None
        solde = int(solde_match.group(1)) if solde_match else None
        ref = ref_match.group(1) if ref_match else None

    return montant, nom, numero, solde, ref, raison, frais



def save_to_firestore(sms_data):
    doc_ref = db.collection('sms_data').document()
    doc_ref.set(sms_data)


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
        port = message.get('port')

        # Extraire les informations du texte du message
        montant, nom, numero, solde, ref, raison, frais = extract_information_from_text(text)

        # Classer le message en fonction du type de transaction
        if "Votre transfert " in text:
            transaction = "transfert"
        elif "recu un transfert " in text:
            transaction = "reception"
        else:
            transaction = "inconnu"

        # Créer un dictionnaire avec les informations du message
        sms_data = {
            "SMS ID": sms_id,
            "Timestamp": timestamp,
            "Montant": montant if montant is not None else "0",
            "Nom": nom if nom else "inconnue",
            "Numero": numero if numero else "Rien à afficher",
            "Solde": solde if solde is not None else "0",
            "Ref": ref if ref else "0",
            "Raison": raison if raison else "pas d'info",
            "Frais": frais if frais is not None else "0",
            "Transaction": transaction,
            "Port": port,
            "IMSI": message.get('imsi')
        }

        # Afficher les informations du message s'il y a des données à afficher
        if montant is None and nom is None and numero is None and solde is None and ref is None and raison is None and frais is None:
            continue

        print(json.dumps(sms_data, indent=4))

        # Enregistrer les données dans Firestore
        save_to_firestore(sms_data)

        # Vérifier et ajouter les données à la collection 'orange' si le port est 4 ou 5
        if str(port) in ['4', '5']:
            orange_data = {
                'port': port,
                'number': message.get('number'),
                'smsc': message.get('smsc'),
                'timestamp': timestamp,
                'balance': solde
            }

            db.collection('orange').add(orange_data)

    return 'Message processing completed'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3232, debug=True)

