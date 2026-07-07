---
name: "antigravity-google-chat"
description: "Habilidade para integrar a execução e as respostas das conversas do Antigravity com salas e webhooks do Google Chat."
---

# Diretrizes de Integração com Google Chat

Sua função é fornecer scripts estruturados usando o Antigravity SDK e requisições HTTP para ler mensagens recebidas no Google Chat e disparar as respostas processadas pelas outras skills do time.

## 1. Padrão de Webhook de Envio (Notificação)
Sempre que precisar enviar uma mensagem formatada de forma assíncrona do terminal ou do agente para o Google Chat, utilize a estrutura de Webhook de Entrada:

```python
import requests
import json

def enviar_para_google_chat(webhook_url, texto_mensagem):
    # Formata no padrão de mensagens do Google Chat
    payload = {"text": texto_mensagem}
    headers = {"Content-Type": "application/json; charset=UTF-8"}
    
    resposta = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
    return resposta.status_code == 200