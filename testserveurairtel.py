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
                'incoming_sms_id': 40,
                'port': 7,
                'number': 'AIRTEL',
                'smsc': '+261331110068',
                'timestamp': get_current_timestamp(),
                'text': 'Votre numero est 261333884146 et votre solde 0 Ar, modular 0.00 Ar,bonus: 0.00 Ar,0 min 0 sec,0 sms et 0.00 MB.Merci',
                'imsi': 646010411172166
            }
        ]
    },
    {
        'sn': 'db00-0050-8600-0133',
        'sms': [
            {
                'incoming_sms_id': 41,
                'port': 7,
                'number': 'AirtelMoney',
                'smsc': '+261331110068',
                'timestamp': get_current_timestamp(),
                'text': "Naharay Ar 500 avy @ 336868624 ho an'ny Services. Ny toe-bolanao dia Ar 3840 . Trans ID: PP230519.0507.C27573",
                'imsi': 646010411172166
            }
        ]
    },
    {
        'sn': 'db00-0050-8600-0133',
        'sms': [
            {
                'incoming_sms_id': 43,
                'port': 7,
                'number': 'AirtelMoney',
                'smsc': '+261331110068',
                'timestamp': get_current_timestamp(),
                'text': "Tontosa ny fandefasanao Ar 300 @  336868624 ho an'ny 1983.Toe bola Ar 3990. Sarany : Ar 50. Trans ID: PP230519.0511.D24964",
                'imsi': 646010411172166
            }
        ]
    }
]

# URL du serveur
url = 'http://localhost:3333'

# Envoi des fichiers JSON
for json_data in json_files:
    response = requests.post(url, json=json_data)
    if response.status_code == 200:
        print('Fichier JSON envoyé avec succès.')
    else:
        print('Échec de l\'envoi du fichier JSON. Statut de la requête :', response.status_code)
