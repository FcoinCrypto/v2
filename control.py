import subprocess
import os
import psutil

# Chemin absolu du répertoire courant
repertoire_courant = os.path.dirname(os.path.abspath(__file__))

# Liste des scripts à contrôler
scripts = [
    {"nom": os.path.join(repertoire_courant, "balance.py"), "session": "balance"},
    {"nom": os.path.join(repertoire_courant, "last_sms.py"), "session": "last_sms"},
    {"nom": os.path.join(repertoire_courant, "proxy_webhook.py"), "session": "controle_proxy_webhook"},
    {"nom": os.path.join(repertoire_courant, "serveur_mobile_meney_achat.py"), "session": "serveur_mobile"},
    {"nom": os.path.join(repertoire_courant, "serverlance.py"), "session": "serverlance_api_web"},  # ajout du script "serverlance.py"
    {"nom": os.path.join(repertoire_courant, "recev_money_v2.py"), "session": "recev_money"},
    {"nom": os.path.join(repertoire_courant,"mvola.py"),"session": "serveur_mvola"},
    # ajoute serveur_orange.py
    {"nom": os.path.join(repertoire_courant,"orange.py"),"session": "serveur_orange"},
    # ajoute serveur_airtel.py
    {"nom": os.path.join(repertoire_courant,"airtel.py"),"session": "serveur_airtel"}
]

# Reste du code ...


# Vérifie l'état d'un script en utilisant le nom de session
def get_script_state(session_name):
    for proc in psutil.process_iter(['name', 'cmdline']):
        if 'screen' in proc.info['name']:
            if any(session_name in s for s in proc.info['cmdline']):
                return True
    return False

while True:
    # Affiche le menu principal
    print("\nMenu principal:")
    for index, script in enumerate(scripts):
        etat = "arrêté" if not get_script_state(script["session"]) else "en cours"
        print(f"{index+1}. {script['nom']} - État : {etat}")

    print("0. Quitter")

    choix = input("\nSélectionnez un script pour l'interagir (0 pour quitter) : ")

    if choix == "0":
        break

    try:
        index = int(choix) - 1
        script = scripts[index]

        if not get_script_state(script["session"]):
            # Redirige la sortie du script vers un fichier texte
            sortie_fichier = os.path.join(repertoire_courant, f"{script['session']}_sortie.txt")
            cmd = f"screen -dmS {script['session']} bash -c 'python3 {script['nom']} > {sortie_fichier} 2>&1'"
            subprocess.run(cmd, shell=True)

            print(f"Le script {script['nom']} a été lancé avec succès.")
        else:
            print(f"Le script {script['nom']} est déjà en cours d'exécution.")

        while True:
            # Affiche le sous-menu
            print("\nSous-menu :")
            print("1. Afficher la sortie du script")
            print("2. Arrêter le script")
            print("3. Revenir au menu principal")

            sous_choix = input("\nSélectionnez une option : ")

            if sous_choix == "1":
                # Affiche la sortie du script à partir du fichier texte
                sortie_fichier = os.path.join(repertoire_courant, f"{script['session']}_sortie.txt")
                if os.path.isfile(sortie_fichier):
                    with open(sortie_fichier, "r") as f:
                        contenu = f.read()
                        print(contenu)
                else:
                    print("Aucune sortie disponible.")

                input("\nAppuyez sur Entrée pour revenir au sous-menu : ")
            elif sous_choix == "2":
                # Arrête le script
                cmd = f"screen -S {script['session']} -X quit"
                subprocess.run(cmd, shell=True)
                print(f"Le script {script['nom']} a été arrêté.")
                break
            elif sous_choix == "3":
                break
            else:
                print("Choix invalide. Veuillez sélectionner une option valide.")

    except (ValueError, IndexError):
        print("Choix invalide. Veuillez sélectionner un numéro de script valide.")

print("Arrêt des scripts en cours...")

# Attends la fin de tous les processus en arrière-plan
for script in scripts:
    if get_script_state(script["session"]):
        cmd = f"screen -S {script['session']} -X quit"
        subprocess.run(cmd, shell=True)

print("Programme terminé.")
