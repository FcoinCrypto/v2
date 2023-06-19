import requests
from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_post_request():
    data = request.get_json()  # Récupérer les données JSON de la requête
    print("Données reçues :", data)  # Afficher les données reçues

    # Traiter les données ou effectuer d'autres opérations

    # Vérifiez si le 'number' est 'MVola', 'OrangeMoney' ou 'AIRTEL'
    if 'sms' in data:
        number = data['sms'][0]['number']
        if number == 'MVola':
            other_script_url = "http://localhost:3434"
        elif number == 'OrangeMoney':
            other_script_url = "http://localhost:3232"
        elif number == 'AirtelMoney':
            other_script_url = "http://localhost:3333"
        else:
            return "Numéro non reconnu. Aucune donnée envoyée."

        try:
            response = requests.post(other_script_url, json=data)

            # Traiter la réponse de l'autre script si nécessaire
            if response.status_code == 200:
                return "Données envoyées avec succès à l'autre script."
            else:
                return "Une erreur s'est produite lors de l'envoi des données."
        except requests.exceptions.RequestException as e:
            return f"Une erreur s'est produite lors de l'envoi des données : {e}"
    else:
        return "Le numéro n'est pas présent. Aucune donnée envoyée."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5030)
