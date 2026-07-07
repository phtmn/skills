import os
import subprocess
import threading
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# CREDENCIAIS DO PASSO 1 (Cole as suas aqui)
WHATSAPP_TOKEN = "EAAMtNsaSWR4BR2riLHgfZAhLEWZA6XJpDkzEb26OAp5nmlZBgskQF6svEWyxjViIWcIpjnUqpdz5TdtxytpqWFIC0xvX1GZATr2qUk5hfOuOcaWIZBbHPSNlAUEZCvVc5vqGLi4pu9PbtsMkzZCZAFpcc4XhphH5l1H9dN8qC8hWFTeZA3Y2X1V8qx2Hv9XxZBABDEi3xkIuWJyl7nlw3ZBLAcRikRwY4HvILRZCZAO4JEDXvm2xRoqfyOQrIa5Wr0Oq66kxrZBVv8EUU12V7fSA0JCa0ErH0ossE8z4xpRw0aMQZDZD"
BUSINESS_PHONE_ID = "1166285783245768"
URL_ENVIO_META = f"https://graph.facebook.com/v17.0/{BUSINESS_PHONE_ID}/messages"

def enviar_mensagem_whatsapp(numero_destino, texto):
    """Função utilitária que faz o POST oficial para a API da Meta"""
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": numero_destino,
        "type": "text",
        "text": {"body": texto}
    }
    requests.post(URL_ENVIO_META, json=payload, headers=headers)

def rodar_antigravity_async(numero_usuario, texto_usuario):
    """Executa a IA local e envia o resultado de volta para o celular"""
    try:
        # Executa o Arquiteto Sênior do Antigravity
        comando = ["npx", "antigravity", "run", "--skill", "apps-script-architect", texto_usuario]
        resultado = subprocess.run(comando, capture_output=True, text=True, encoding='utf-8', shell=True)
        resposta_do_senior = resultado.stdout.strip()
        
        if not resposta_do_senior:
            resposta_do_senior = "O agente processou a demanda, mas não gerou saída de texto."
            
        # Envia o resultado final para o seu WhatsApp
        enviar_mensagem_whatsapp(numero_usuario, resposta_do_senior)

    except Exception as e:
        enviar_mensagem_whatsapp(numero_usuario, f"❌ *Erro de execução:* {str(e)}")

@app.route('/whatsapp-webhook', methods=['POST'])
def whatsapp_event():
    dados = request.get_json()
    
    # Estrutura de leitura de mensagens padrão do JSON da Meta
    try:
        valores = dados['entry'][0]['changes'][0]['value']
        if 'messages' in valores:
            mensagem_objeto = valores['messages'][0]
            numero_usuario = mensagem_objeto['from']
            texto_usuario = mensagem_objeto['text']['body']
            
            # Responde na hora pelo WhatsApp para não dar erro de conexão
            enviar_mensagem_whatsapp(numero_usuario, "⚙️ _O Arquiteto Sênior está estruturando o seu projeto..._")
            
            # Processa o Antigravity em paralelo
            threading.Thread(target=rodar_antigravity_async, args=(numero_usuario, texto_usuario)).start()
    except Exception:
        pass
        
    return jsonify({"status": "recebido"}), 200

@app.route('/whatsapp-webhook', methods=['GET'])
def verificar_webhook():
    """Validação obrigatória que a Meta faz ao cadastrar a URL"""
    verify_token = "token_customizado_antigravity"  # Você pode inventar qualquer palavra aqui
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode and token == verify_token:
        return challenge, 200
    return "Falha na verificação", 403

if __name__ == '__main__':
    app.run(port=5000, debug=True)