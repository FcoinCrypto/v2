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
                'incoming_sms_id': 32,
                'port': 3,
                'number': 'MVola',
                'smsc': '+261340010000',
                'timestamp': get_current_timestamp(),
                'text': "1/2 Avec MVola Epargne, profitez d'un taux d'interet de 4 pourcent/an. Faites un depot des 100 Ar et epargnez jusqu'a 100 000 000 Ar. Tapez le #111*1*3*1#",
                'imsi': 646040239937673
            }
        ]
    },
    {
        'sn': 'db00-0050-8600-0133',
        'sms': [
            {
                'incoming_sms_id': 26,
                'port': 1,
                'number': 'MVola',
                'smsc': '+261340010000',
                'timestamp': get_current_timestamp(),
                'text': '2/2 1 100 Ar envoye a Narindra Franco Danhy (0383989016) le 19/05/23 a 01:36. Frais: 50 Ar. Raison: tredg. Solde : 150 Ar. Ref: 593563836',
                'imsi': 646040239937674
            }
        ]
    }
]

# URL du serveur
url = 'http://localhost:3434'

# Envoi des fichiers JSON
for json_data in json_files:
    response = requests.post(url, json=json_data)
    if response.status_code == 200:
        print('Fichier JSON envoyé avec succès.')
    else:
        print('Échec de l\'envoi du fichier JSON. Statut de la requête :', response.status_code)
