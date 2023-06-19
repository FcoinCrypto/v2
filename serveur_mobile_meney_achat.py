import requests
import json
from flask import Flask, request, jsonify
import time
import re
import requests

app = Flask(__name__)

API_URL = "http://192.168.88.253/api/send_sms"

def get_operator_url(operateur):
    if operateur.startswith('034') or operateur.startswith('038'):
        url = 'http://localhost:3000/mvola'
    elif operateur.startswith('032'):
        url = 'http://localhost:3000/orange'
    elif operateur.startswith('033'):
        url = 'http://localhost:3000/airtel'
    else:
        raise ValueError('Opérateur non pris en charge')
    
    return url

def get_operator_token(operateur):
    if operateur.startswith('034') or operateur.startswith('038'):
        token = 'mvola_token'
    elif operateur.startswith('032'):
        token = 'orange_token'
    elif operateur.startswith('033'):
        token = 'airtel_token'
    else:
        raise ValueError('Opérateur non pris en charge')
    
    return token


def send_credit_mvola(operateur, credit_amount, solde_disponible, port):
    balance, _ = get_operator_balance(operateur)
    if credit_amount > solde_disponible:
        return jsonify({'success': False, 'message': 'Opérateur non disponible veuillez réessayer ultérieurement'})
    elif credit_amount > balance:
        return jsonify({'success': False, 'message': 'Solde insuffisant'})
    
    headers = {'Authorization': 'Basic YWRtaW46YWRtaW4=', 'Content-Type': 'application/json'}

    def query_ussd_reply():
        query_ussd_reply_url = f'http://192.168.88.253/api/query_ussd_reply?port={port}'
        query_response = requests.get(query_ussd_reply_url, headers=headers)
        print(f"Query USSD Reply Response: {query_response}")
        print(f"Query USSD Reply Content: {query_response.json()}")

    # Effectuer les opérations pour envoyer du crédit via Mvola ici

    # 1. Envoyer la requête USSD pour l'opération d'envoi de crédit
    url = 'http://192.168.88.253/api/send_ussd'
    ussd_command = f"#111*1*3*{operateur}*{credit_amount}*2*FPAY#"  # Ajuster le code USSD pour l'envoi de crédit
    body = {"port": [port], "command": "send", "text": ussd_command}
    response = requests.post(url, headers=headers, data=json.dumps(body))

    print(f"Send USSD Response: {response}")
    print(credit_amount)
    time.sleep(3)
    query_ussd_reply()

    # Vérifier si la première requête a réussi
    if response.status_code != 200:
        return jsonify({'success': False, 'message': 'Erreur lors de l\'envoi de la requête USSD'})

    # 2. Valider l'envoi avec le code 3412
    body_validation = {"port": [port], "command": "send", "text": "3412"}
    response_validation = requests.post(url, headers=headers, data=json.dumps(body_validation))

    print(f"Validation Response: {response_validation}")
    time.sleep(3)
    query_ussd_reply()

    # Vérifier si la validation a réussi
    if response_validation.status_code != 200:
        return jsonify({'success': False, 'message': 'Erreur lors de la validation de l\'envoi'})

    # 3. Fermer le menu USSD
    body_cancel = {"port": [port], "command": "cancel", "text": ""}
    response_cancel = requests.post(url, headers=headers, data=json.dumps(body_cancel))

    print(f"Cancel USSD Menu Response: {response_cancel}")
    time.sleep(1)
    query_ussd_reply()

    # Vérifier si la fermeture du menu USSD a réussi
    if response_cancel.status_code != 200:
        return jsonify({'success': False, 'message': 'Opération réussie'})

    # Vérifier si la fermeture du menu USSD a réussi
    if response_cancel.status_code != 200:
        return jsonify({'success': False, 'message': 'Erreur lors de la fermeture du menu USSD'})

    # Renvoyer une réponse JSON indiquant si l'opération a réussi ou non
    return jsonify({'success': True, 'message': 'Opération réussie'})


def get_operator_balance(operateur):
    url = get_operator_url(operateur)
    token = get_operator_token(operateur)
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    print(f"URL: {url}")
    print(f"Token: {token}")
    print(f"Response: {response}")
    print(f"Data: {data}")
    
    if 'error' in data and ('orange' in data['error'] or 'airtel' in data['error']):
        return None, None
    
    if isinstance(data, list):
        max_balance = 0
        max_balance_port = None
        for account in data:
            if account.get('balance') is not None and account.get('port') is not None:
                if account['balance'] > max_balance:
                    max_balance = account['balance']
                    max_balance_port = account['port']
                  
        print(f"Max Balance: {max_balance}, Max Balance Port: {max_balance_port}")
        return max_balance, max_balance_port
    else:
        if data.get('balance') is not None and data.get('port') is not None:
            print(f"Balance: {data.get('balance')}, Port: {data.get('port')}")
            return data.get('balance'), data.get('port')
        else:
            return None, None



def send_money_mvola(email, operateur, montant_envoi, solde_disponible, port):
    balance, _ = get_operator_balance(operateur)
    if montant_envoi > solde_disponible:
        return jsonify({'success': False, 'message': 'Operateur non disponible veuillez réessayer ultérieurement'})
    elif montant_envoi > balance:
        return jsonify({'success': False, 'message': 'Solde insuffisant'})
    

    headers = {'Authorization': 'Basic YWRtaW46YWRtaW4=', 'Content-Type': 'application/json'}

    def query_ussd_reply():
        query_ussd_reply_url = f'http://192.168.88.253/api/query_ussd_reply?port={port}'
        query_response = requests.get(query_ussd_reply_url, headers=headers)
        print(f"Query USSD Reply Response: {query_response}")
        print(f"Query USSD Reply Content: {query_response.json()}")

    # Effectuer les opérations pour envoyer de l'argent via Mvola ici

    # 1. Envoyer la requête USSD pour l'opération d'envoi d'argent
    url = 'http://192.168.88.253/api/send_ussd'
    ussd_command = f"#111*1*2*{operateur}*{montant_envoi}*2*FPAY#"
    body = {"port": [port], "command": "send", "text": ussd_command}
    response = requests.post(url, headers=headers, data=json.dumps(body))

    print(f"Send USSD Response: {response}")
    print(montant_envoi)
    time.sleep(3)
    query_ussd_reply()
      # Ajout d'un délai de 2 secondes

    # Vérifier si la première requête a réussi
    if response.status_code != 200:
        return jsonify({'success': False, 'message': 'Erreur lors de l\'envoi de la requête USSD'})

    # 2. Valider l'envoi avec le code 3412
    body_validation = {"port": [port], "command": "send", "text": "3412"}
    response_validation = requests.post(url, headers=headers, data=json.dumps(body_validation))

    print(f"Validation Response: {response_validation}")
    time.sleep(3)
    query_ussd_reply()
      # Ajout d'un délai de 2 secondes

    # Vérifier si la validation a réussi
    if response_validation.status_code != 200:
        return jsonify({'success': False, 'message': 'Erreur lors de la validation de l\'envoi'})

    # 3. Fermer le menu USSD
    body_cancel = {"port": [port], "command": "cancel", "text": ""}
    response_cancel = requests.post(url, headers=headers, data=json.dumps(body_cancel))

    print(f"Cancel USSD Menu Response: {response_cancel}")
    time.sleep(1)
    query_ussd_reply()
      # Ajout d'un délai de 2 secondes

    # Vérifier si la fermeture du menu USSD a réussi
    if response_cancel.status_code != 200:
        return jsonify({'success': False, 'message': 'Erreur lors de la fermeture du menu USSD'})

    # Renvoyer une réponse JSON indiquant si l'opération a réussi ou non
    return jsonify({'success': True, 'messages': 'Opération réussie'})

def send_money_orange(email, operateur, montant_envoi, solde_disponible, port):
    balance, _ = get_operator_balance(operateur)
    if montant_envoi > solde_disponible:
        return jsonify({'success': False, 'message': 'Operateur non disponible veuillez réessayer ultérieurement'})
    elif montant_envoi > balance:
        return jsonify({'success': False, 'message': 'Solde insuffisant'})

    headers = {'Authorization': 'Basic YWRtaW46YWRtaW4=', 'Content-Type': 'application/json'}

    def query_ussd_reply():
        query_ussd_reply_url = f'http://192.168.88.253/api/query_ussd_reply?port={port}'
        query_response = requests.get(query_ussd_reply_url, headers=headers)
        print(f"Query USSD Reply Response: {query_response}")
        print(f"Query USSD Reply Content: {query_response.json()}")

    # 1. Envoyer la requête USSD pour l'opération d'envoi d'argent
    url = 'http://192.168.88.253/api/send_ussd'
    ussd_command = f"#144*1*1*{operateur}*{operateur}*{montant_envoi}*2*1256#"
    body = {"port": [port], "command": "send", "text": ussd_command}
    response = requests.post(url, headers=headers, data=json.dumps(body))
    time.sleep(2)
    query_ussd_reply()
    # 6. Entrer le code PIN
    body_pin = {"port": [port], "command": "send", "text": "1"}  # Remplacer par le PIN réel
    response_pin = requests.post(url, headers=headers, data=json.dumps(body_pin))
    time.sleep(2)
    query_ussd_reply()


    # Vérifier si l'opération a réussi
    if response_pin.status_code != 200:
        return jsonify({'success': False, 'message': 'Erreur lors de l\'envoi de l\'argent'})

    # 7. Fermer le menu USSD
    body_cancel = {"port": [port], "command": "cancel", "text": ""}
    response_cancel = requests.post(url, headers=headers, data=json.dumps(body_cancel))
    time.sleep(1)
    query_ussd_reply()

    # Vérifier si la fermeture du menu USSD a réussi
    if response_cancel.status_code != 200:
        return jsonify({'success': False, 'message': 'Erreur lors de la fermeture du menu USSD'})

    # Renvoyer une réponse JSON indiquant si l'opération a réussi ou non
    return jsonify({'success': True, 'message': 'Opération réussie'})


def send_money_airtel(email, operateur, montant_envoi, solde_disponible, port):
    balance, _ = get_operator_balance(operateur)
    if montant_envoi > solde_disponible:
        return jsonify({'success': False, 'message': 'Operateur non disponible veuillez réessayer ultérieurement'})
    elif montant_envoi > balance:
        return jsonify({'success': False, 'message': 'Solde insuffisant'})

    headers = {'Authorization': 'Basic YWRtaW46YWRtaW4=', 'Content-Type': 'application/json'}

    def query_ussd_reply():
        query_ussd_reply_url = f'http://192.168.88.253/api/query_ussd_reply?port={port}'
        query_response = requests.get(query_ussd_reply_url, headers=headers)
        print(f"Query USSD Reply Response: {query_response}")
        print(f"Query USSD Reply Content: {query_response.json()}")


    

    # 1. Envoyer la requête USSD pour l'opération d'envoi d'argent
    url = 'http://192.168.88.253/api/send_ussd'
    ussd_command = "*121*2*1#"
    body = {"port": [port], "command": "send", "text": ussd_command}
    response = requests.post(url, headers=headers, data=json.dumps(body))
    time.sleep(1)
    query_ussd_reply()

    # 2. Entrer l'opérateur
    body_operator = {"port": [port], "command": "send", "text": "2"}
    response_operator = requests.post(url, headers=headers, data=json.dumps(body_operator))
    time.sleep(1)
    query_ussd_reply()

    # 3. Continuer avec le processus
    body_continue = {"port": [port], "command": "send", "text": "1"}
    response_continue = requests.post(url, headers=headers, data=json.dumps(body_continue))
    time.sleep(1)
    query_ussd_reply()

    # 4. Continuer avec le processus
    body_continue = {"port": [port], "command": "send", "text": "1"}
    response_continue = requests.post(url, headers=headers, data=json.dumps(body_continue))
    time.sleep(2)
    query_ussd_reply()

    # 5. Entrer le numéro de l'opérateur
    body_operator_number = {"port": [port], "command": "send", "text": str(operateur)}
    response_operator_number = requests.post(url, headers=headers, data=json.dumps(body_operator_number))
    time.sleep(1)
    query_ussd_reply()

    # 6. Confirmer le numéro de l'opérateur
    body_operator_confirm = {"port": [port], "command": "send", "text": str(operateur)}
    response_operator_confirm = requests.post(url, headers=headers, data=json.dumps(body_operator_confirm))
    time.sleep(1)
    query_ussd_reply()

    # 7. Entrer le montant à envoyer
    body_amount = {"port": [port], "command": "send", "text": str(montant_envoi)}
    response_amount = requests.post(url, headers=headers, data=json.dumps(body_amount))
    time.sleep(1)
    query_ussd_reply()

    # 8. Entrer le code PIN
    body_pin = {"port": [port], "command": "send", "text": "1983"}  
    response_pin = requests.post(url, headers=headers, data=json.dumps(body_pin))
    time.sleep(1)
    query_ussd_reply()

    # 9. Confirmer le code PIN
    body_pin_confirm = {"port": [port], "command": "send", "text": "1983"}
    response_pin_confirm = requests.post(url, headers=headers, data=json.dumps(body_pin_confirm))
    time.sleep(2)
    query_ussd_reply()

    # 10. Finaliser l'opération
    body_finalize = {"port": [port], "command": "send", "text": "2"}
    response_finalize = requests.post(url, headers=headers, data=json.dumps(body_finalize))
    time.sleep(1)
    query_ussd_reply()

    # 11. Fermer le menu USSD
    body_close_menu =  {"port": [port], "command": "cancel", "text": ""}
    response_close_menu = requests.post(url, headers=headers, data=json.dumps(body_close_menu))
    time.sleep(1)
    query_ussd_reply()

    return jsonify({'success': True, 'message': 'Transfert effectué avec succès'})





@app.route('/send_money', methods=['POST'])
def send_money():
    data = request.get_json()
    email = data.get('email')
    operateur = data.get('operateur')
    montant_envoi = data.get('montant_envoi')
    wallet_balance = data.get('wallet_balance')
    
    # Vérifier si l'opérateur est pris en charge
    if not (operateur.startswith('034') or operateur.startswith('038') or operateur.startswith('032') or operateur.startswith('033')):
        return jsonify({'success': False, 'message': 'Opérateur non pris en charge'}), 400
    
    solde_disponible, port = get_operator_balance(operateur)
    
    if not email:
        return jsonify({'success': False, 'message': 'E-mail manquant'}), 400

    if solde_disponible is None:
        return jsonify({'success': False, 'message': 'Réseau indisponible'})

    print(f"email: {email}, operateur: {operateur}, montant_envoi: {montant_envoi}, solde_disponible: {solde_disponible}, wallet_balance: {wallet_balance}, port: {port}")

    if montant_envoi > solde_disponible or montant_envoi > wallet_balance:
        return jsonify({'success': False, 'message': 'Operateur non disponible veuillez réessayer ultérieurement'}), 400
    
    response = None
    if operateur.startswith('034') or operateur.startswith('038'):
        response = send_money_mvola(email, operateur, montant_envoi, solde_disponible, port)
    elif operateur.startswith('032'):
        response = send_money_orange(email, operateur, montant_envoi, solde_disponible, port)
    elif operateur.startswith('033'):
        response = send_money_airtel(email, operateur, montant_envoi, solde_disponible, port)
    
    if response is None:
        return jsonify({'success': False, 'message': 'Erreur inconnue'}), 400
    return response




@app.route("/send_sms", methods=["POST"])
def send_sms():
    number = request.json.get("number")
    text_param = request.json.get("text_param")
    geosms = request.json.get("geosms")

    if not number or not text_param or not geosms:
        return jsonify({"error": "Les paramètres 'number', 'text_param' et 'geosms' sont requis"}), 400

    match = re.match(r'LatLng\(lat:(.*), lng:(.*)\)', geosms)
    if not match:
        return jsonify({"error": "Format incorrect pour 'geosms'. Le format attendu est 'LatLng(lat:<latitude>, lng:<longitude>)'"}), 400

    lat, lng = match.groups()
    google_maps_link = f"https://www.google.com/maps?q={lat},{lng}"

    # Convertir text_param en liste si nécessaire
    if isinstance(text_param, str):
        text_param = [text_param]

    text_param.append("SOS")
    text_param.append(google_maps_link)

    # Concatenate all elements of text_param into a single string
    text_param_str = ' '.join(text_param)

    payload = {
        "text": "#param#",
        "port": [2],
        "param": [
            {
                "number": number,
                "text_param": [text_param_str],
                "user_id": 1,
            }
        ],
    }

    headers = {'Authorization': 'Basic YWRtaW46YWRtaW4=', 'Content-Type': 'application/json'}

    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Erreur lors de l'appel à l'API : {e}"}), 500

    return jsonify({"message": "SMS envoyé avec succès"}), 200


#envoi de credit
@app.route('/send_creditmobile', methods=['POST'])
def send_credit_mobile():
    data = request.get_json()
    operateur = data.get('operateur')
    credit_amount = data.get('credit_amount')
    wallet_balance = data.get('wallet_balance')

    # Vérifier si l'opérateur est pris en charge
    if not (operateur.startswith('034') or operateur.startswith('038') or operateur.startswith('032') or operateur.startswith('033')):
        return jsonify({'success': False, 'message': 'Opérateur non pris en charge'}), 400

    solde_disponible, port = get_operator_balance(operateur)

    if solde_disponible is None:
        return jsonify({'success': False, 'message': 'Réseau indisponible'})

    print(f"operateur: {operateur}, credit_amount: {credit_amount}, solde_disponible: {solde_disponible}, wallet_balance: {wallet_balance}, port: {port}")

    if credit_amount > solde_disponible or credit_amount > wallet_balance:
        return jsonify({'success': False, 'message': 'Opérateur non disponible veuillez réessayer ultérieurement'}), 400

    response = None
    if operateur.startswith('034') or operateur.startswith('038'):
        response = send_credit_mvola(operateur, credit_amount, solde_disponible, port)
    elif operateur.startswith('032'):
        response = send_credit_orange(operateur, credit_amount, solde_disponible, port)
    elif operateur.startswith('033'):
        response = send_credit_airtel(operateur, credit_amount, solde_disponible, port)

    if response is None:
        return jsonify({'success': False, 'message': 'Erreur inconnue'}), 400

    return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7000)