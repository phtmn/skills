import subprocess
import threading
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# URL DO SEU WEBHOOK (Pegue na aba "Configuração" ou "Webhooks" da sala do Google Chat)
# Se você estiver em um chat privado (1:1), use a própria URL do evento se disponível,
# ou crie um espaço/sala de testes e gere uma URL de Webhook lá.
URL_WEBHOOK_GOOGLE_CHAT = "COLE_AQUI_A_URL_DO_WEBHOOK_DA_SALA"

def processar_antigravity_em_segundo_plano(texto_usuario):
    """Roda o Antigravity sem pressa e envia o resultado via Webhook"""
    try:
        comando = ["npx", "antigravity", "run", "--skill", "apps-script-architect", texto_usuario]
        resultado = subprocess.run(comando, capture_output=True, text=True, encoding='utf-8', shell=True)
        resposta_do_senior = resultado.stdout.strip()
        
        if not resposta_do_senior:
            resposta_do_senior = "O agente processou a demanda, mas não gerou saída de texto."
            
        # Dispara a resposta real para a sala usando a função da sua skill
        payload = {"text": resposta_do_senior}
        headers = {"Content-Type": "application/json; charset=UTF-8"}
        requests.post(URL_WEBHOOK_GOOGLE_CHAT, json=payload, headers=headers)

    except Exception as e:
        erro_msg = {"text": f"❌ *Erro de execução:* {str(e)}"}
        requests.post(URL_WEBHOOK_GOOGLE_CHAT, json=erro_msg)

@app.route('/google-chat-bot', methods=['POST'])
def google_chat_event():
    evento = request.get_json()
    
    if evento.get('type') == 'MESSAGE':
        texto_usuario = evento['message']['text']
        
        # Cria uma Thread para rodar o Antigravity em paralelo sem travar o Flask
        threading.Thread(target=processar_antigravity_em_segundo_plano, args=(texto_usuario,)).start()
        
        # RESPONDE IMEDIATAMENTE PRO GOOGLE NÃO DAR TIMEOUT!
        # Dizemos para o chat que recebemos e estamos trabalhando nisso.
        return jsonify({"text": "⚙️ _O Arquiteto Sênior está estruturando o seu projeto..._"})
        
    return jsonify({"text": ""})

if __name__ == '__main__':
    app.run(port=5000, debug=True)