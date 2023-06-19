from flask import Flask, jsonify, request
from collections import defaultdict
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# Remplacez 'back.json' par le chemin du fichier de configuration JSON
cred = credentials.Certificate('fpay.json')
firebase_admin.initialize_app(cred)

db = firestore.client()




@app.route('/mvola', methods=['GET'])

def get_mvola_data():
    # Vérifier si la collection mvola existe
    mvola_collection = db.collection('mvola')
    if not mvola_collection.get():
        return jsonify({'error': 'mvola collection not found'})

    # Récupérer tous les documents avec une balance supérieure ou égale à 0
    simbox_collection = mvola_collection.where('balance', '>=', 0)
    docs = simbox_collection.stream()

    port_balances = {0: {}, 1: {}, 2: {}, 3: {}}
    for doc in docs:
        doc_data = doc.to_dict()
        doc_data['id'] = doc.id

        port = doc_data['port']
        if port in port_balances and (not port_balances[port] or doc_data['timestamp'] > port_balances[port]['timestamp']):
            port_balances[port] = doc_data

    results = list(port_balances.values())
    print(results)
    return jsonify(results)





@app.route('/orange', methods=['GET'])
def get_orange_data():
    # Vérifier si la collection orange existe
    orange_collection = db.collection('orange')
    if not orange_collection.get():
        return jsonify({'error': 'orange collection not found'})

    # Récupérer tous les documents avec une balance supérieure ou égale à 0
    simbox_collection = orange_collection.where('balance', '>=', 0)
    docs = simbox_collection.stream()

    port_balances = {4: {}, 5: {}}
    for doc in docs:
        doc_data = doc.to_dict()
        doc_data['id'] = doc.id

        port = doc_data['port']
        if port in port_balances and (not port_balances[port] or doc_data['timestamp'] > port_balances[port]['timestamp']):
            port_balances[port] = doc_data

    results = list(port_balances.values())
    print(results)
    return jsonify(results)



@app.route('/airtel', methods=['GET'])

@app.route('/airtel', methods=['GET'])
def get_airtel_data():
    # Vérifier si la collection airtel existe
    airtel_collection = db.collection('airtel')
    if not airtel_collection.get():
        return jsonify({'error': 'airtel collection not found'})

    # Récupérer tous les documents avec une balance supérieure ou égale à 0
    simbox_collection = airtel_collection.where('balance', '>=', 0)
    docs = simbox_collection.stream()

    port_balances = {6: {}, 7: {}}
    for doc in docs:
        doc_data = doc.to_dict()
        doc_data['id'] = doc.id

        port = doc_data['port']
        if port in port_balances and (not port_balances[port] or doc_data['timestamp'] > port_balances[port]['timestamp']):
            port_balances[port] = doc_data

    results = list(port_balances.values())
    print(results)
    return jsonify(results)






if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

