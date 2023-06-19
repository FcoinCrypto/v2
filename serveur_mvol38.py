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

def save_to_firestore(sms_data):
    doc_ref = db.collection('sms_data').document()
    doc_ref.set(sms_data)

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()

    if 'sms' in data:
        i = 0
        while i < len(data['sms']):
            sms = data['sms'][i]
            text = sms['text']

            if text.startswith("1/2") and i + 1 < len(data['sms']) and data['sms'][i + 1]['text'].startswith("2/2"):
                text += data['sms'][i + 1]['text'][4:]
                i += 1

            if "recu" in text:
                montant = int(text.split(" Ar")[0].split("recu")[1].replace(" ", ""))
                match = re.search(r'(\w+\s+\w+ \(\d{10}\))', text)
                if match:
                    nom = match.group(1).split("(")[0].strip()
                    numero = match.group(1).split("(")[1].split(")")[0]
                else:
                    nom = "Inconnu"
                    numero = "Inconnu"
                solde_and_ref = text.split("solde est de ")[1].split(" Ar. ")[0]
                solde = int(solde_and_ref.split(" Ref: ")[0].replace(" ", ""))
                ref = re.search(r'Ref: (\d{9})', text).group(1)
                raison = text.split("Raison: ")[1].split(". ")[0]

                sms_data = {
                    'SMS ID': sms['incoming_sms_id'],
                    'Timestamp': sms['timestamp'],
                    'Montant': montant,
                    'Nom': nom,
                    'Numero': numero,
                    'Solde': solde,
                    'Ref': ref,
                    'Raison': raison,
                    'transaction': 'reception',
                    'Port': sms['port'],
                    'IMSI': sms['imsi'],
                }
                save_to_firestore(sms_data)
            elif "transfere" in text:
                montant = int(text.split("transfere ")[1].split(" Ar")[0].replace(" ", ""))
                match = re.search(r'(\w+\s+\w+ \(\d{10}\))', text)
                if match:
                    nom = match.group(1).split("(")[0].strip()
                else:
                    nom = "Inconnu"
                numero = re.search(r'\((\d{10})\)', text).group(1)
                solde_match = re.search(r"solde est de\s+([\d\s]+)Ar", text)
                if solde_match:
                    solde = int("".join(solde_match.group(1).split()))
                else:
                    solde = int(text.split("solde est de ")[1].split(" Ar. ")[0].replace(" ", ""))
                ref_match = re.search(r'Ref: (\d{9})', text)
                ref = ref_match.group(1) if ref_match else None
                raison = text.split("Raison: ")[1].split(". ")[0]
                frais = text.split("Frais: ")[1].split(" Ar. ")[0]

                sms_data = {
                    'SMS ID': sms['incoming_sms_id'],
                    'Timestamp': sms['timestamp'],
                    'Montant': montant,
                    'Nom': nom,
                    'Numero': numero,
                    'Solde': solde,
                    'Ref': ref,
                    'Raison': raison,
                    'transaction': 'transfert',
                    'Port': sms['port'],
                    'IMSI': sms['imsi'],
                }

                if "Frais: " in text:
                    frais = int(text.split("Frais: ")[1].split(" Ar. ")[0].replace(" ", ""))
                    sms_data['Frais'] = frais

                save_to_firestore(sms_data)
            else:
                print("Le texte du message ne contient pas les informations nécessaires.")
            i += 1

    # Extraire les informations souhaitées
    port = data['sms'][0]['port']
    number = data['sms'][0]['number']
    smsc = data['sms'][0]['smsc']
    timestamp = data['sms'][0]['timestamp']
    text = data['sms'][0]['text']

    # Extraire les informations du second message si disponible
    if len(data['sms']) > 1:
        second_text = data['sms'][1]['text']
    else:
        second_text = ""

    # Extraire le solde à partir du texte et le convertir en entier
    balance_info = None
    balance_str = ""
    regex = r"Votre solde est de(.*?)Ar"

    if "Votre solde est de" in text:
        match = re.search(regex, text)
        if match:
            balance_str = match.group(1).strip()
    elif "Votre solde est de" in second_text:
        match = re.search(regex, second_text)
        if match:
            balance_str = match.group(1).strip()

    if balance_str:
        try:
            # Supprimer les espaces et convertir en entier
            balance_info = int("".join(balance_str.split()))
        except ValueError:
            print("Erreur lors de la conversion du solde en entier")

    # Ajouter les données à la collection correspondante en fonction du port
    if balance_info is not None or balance_str == "0":
        simbox_data = {
            'port': port,
            'number': number,
            'smsc': smsc,
            'timestamp': timestamp,
            'balance': balance_info
        }
        
        # Définir le dictionnaire qui associe chaque port à la collection correspondante
        port_collection = {
            '0': 'mvola',
            '1': 'mvola',
            '2': 'mvola',
            '3': 'mvola',
            '4': 'orange',
            '5': 'orange',
            '6': 'airtel',
            '7': 'airtel'
        }

        # Ajouter les données à la collection correspondante en fonction du port
        collection_name = port_collection.get(str(port), 'simbox')
        db.collection(collection_name).add(simbox_data)            

    return 'success'

if __name__ == '__main__':
    app.run(host='0.0.0.0',port='3438', debug=True)

