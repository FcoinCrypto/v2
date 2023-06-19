import os

def run_ngrok():
    command = "ngrok http --domain=smsmvola.ngrok.app 7000"
    result = os.system(command)
    print(result)

run_ngrok()
