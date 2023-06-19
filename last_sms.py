import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, jsonify

# Remplacez 'fpay.json' par le nom de votre fichier de configuration JSON
cred = credentials.Certificate('fpay.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)

@app.route('/', methods=['GET'])
def get_last_sms():
    # Nom de la collection est 'sms_data'
    collection_ref = db.collection('sms_data')

    # Triez les documents par 'Timestamp' en ordre descendant et prenez le premier
    query = collection_ref.order_by('Timestamp', direction=firestore.Query.DESCENDING).limit(1)
    docs = query.stream()

    for doc in docs:
        data = doc.to_dict()
        if 'Montant' in data and 'Numero' in data and 'Timestamp' in data:
            # Ajouter une condition pour vérifier si la transaction n'est pas nulle
            if data['Montant'] is not None:
                result = {
                    'Montant': data['Montant'],
                    'Numero': data['Numero'],
                    'Transaction': data['Transaction'],
                    'Timestamp': data['Timestamp']
                }
                return jsonify(result)
    return jsonify({"error": "No data found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=70)
