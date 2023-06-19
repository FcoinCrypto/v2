import json
import requests

import time

def get_current_timestamp():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

# Liste des fichiers JSON à envoyer
json_files = [
    {
        'sn': 'db00-0050-8600-0133',
        'sms': [
            {
                'incoming_sms_id': 38,
                'port': 4,
                'number': 'OrangeMoney',
                'smsc': '+261323232707',
                'timestamp': '2023-05-19 04:05:06',
                'text': 'Votre transfert de 2000 Ar vers le 0325193231 est reussi. Frais : 50 Ar .Nouveau solde: 670 Ar. Trans id PP230519.0405.C62279. Orange Money vous remercie',
                'imsi': 646020163441202
            }
        ]
    },
    {
        'sn': 'db00-0050-8600-0133',
        'sms': [
            {
                'incoming_sms_id': 39,
                'port': 4,
                'number': 'OrangeMoney',
                'smsc': '+261323232707',
                'timestamp': '2023-05-19 04:06:59',
                'text': 'Vous avez recu un transfert de 500Ar venant du 0325193231 Nouveau Solde: 1170Ar.  Trans Id: PP230519.0406.C62281. Orange Money vous remercie.',
                'imsi': 646020163441202
            }
        ]
    }
]

# URL du serveur
url = 'http://localhost:3232'

# Envoi des fichiers JSON
for json_data in json_files:
    response = requests.post(url, json=json_data)
    if response.status_code == 200:
        print('Fichier JSON envoyé avec succès.')
    else:
        print('Échec de l\'envoi du fichier JSON. Statut de la requête :', response.status_code)
