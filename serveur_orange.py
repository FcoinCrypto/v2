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
    print("Données reçues :", data) 

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
    regex = r"Solde: (\d+)"  # Modification ici

    if "Solde:" in text:
        match = re.search(regex, text)
        if match:
            balance_str = match.group(1).strip()
    elif "Solde:" in second_text:
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

    if 'sms' in data:
        for sms in data['sms']:
            text = sms['text']

            if "recu" in text:
                montant = int(re.search(r" de (\d+)Ar", text).group(1))
                numero = re.search(r"du (\d+)", text).group(1)
                solde = int(re.search(r"Solde: (\d+)Ar", text).group(1))
                ref = re.search(r"Id: (\w+)", text).group(1)


                sms_data = {
                    'SMS ID': sms['incoming_sms_id'],
                    'Timestamp': sms['timestamp'],
                    'Montant': montant,
                    'Numero': numero,
                    'Solde': solde,
                    'Ref': ref,
                    'transaction': 'reception',
                    'Port': sms['port'],
                    'IMSI': sms['imsi'],
                }
                save_to_firestore(sms_data)
            elif "Votre transfert" in text:
                montant = int(re.search(r"Votre transfert de (\d+)", text).group(1))
                numero = re.search(r"vers (\d+)", text).group(1)
                frais = int(re.search(r"Frais: (\d+)", text).group(1))
                solde = int(re.search(r"Solde: (\d+)", text).group(1))
                ref = "REFERENCE"



                sms_data = {
                    'SMS ID': sms['incoming_sms_id'],
                    'Timestamp': sms['timestamp'],
                    'Montant': montant,
                    'Numero': numero,
                    'Frais': frais,
                    'Solde': solde,
                    'Ref': ref,
                    'transaction': 'transfert',
                    'Port': sms['port'],
                    'IMSI': sms['imsi'],
                }

                save_to_firestore(sms_data)
            else:
                print("Le texte du message ne contient pas les informations nécessaires.")
    
    return 'success', 200

    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3232, debug=True)
