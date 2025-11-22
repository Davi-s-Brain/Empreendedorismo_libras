from flask import Flask, request, jsonify
from flask_cors import CORS
from yeelight import Bulb, BulbException
import threading
import time

app = Flask(__name__)
CORS(app)

BULB_IP = "192.168.0.25" 

# Variáveis Globais
bulb = None
bulb_lock = threading.Lock()
last_sign = None

def connect_bulb():
    """Conecta na lâmpada (se já não estiver conectada)"""
    global bulb
    try:
        if bulb is None:
            print(f"Tentando conectar em {BULB_IP}...")
            bulb = Bulb(BULB_IP, effect="sudden")
            bulb.turn_on()
            print("Lâmpada Conectada com Sucesso!")
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        bulb = None

# Tenta conectar ao iniciar o script
connect_bulb()

ACTIONS = {
    "L": (255, 0, 0),     # Vermelho
    "A": (0, 0, 255),     # Azul
    "C": (0, 255, 0),     # Verde
    "B": (255, 255, 0),   # Amarelo (Exemplo)
    "thumbs_up": "TOGGLE"
}

def execute_action(sign):
    global last_sign, bulb
    
    if sign == last_sign:
        print(f"Sinal repetido '{sign}' ignorado.")
        return
    
    with bulb_lock:
        try:
            # Reconecta se necessário
            if bulb is None:
                connect_bulb()
                if bulb is None: return # Se falhar, desiste

            if sign in ACTIONS:
                action = ACTIONS[sign]
                print(f"---> Executando: {sign}")
                
                if action == "TOGGLE":
                    bulb.toggle()
                else:
                    # R, G, B
                    bulb.set_rgb(action[0], action[1], action[2])
                
                # Atualiza o último sinal SÓ se deu certo
                last_sign = sign
            else:
                print(f"Sinal '{sign}' não configurado.")

        except (BulbException, Exception) as e:
            print(f"Erro de comunicação com a lâmpada: {e}")
            bulb = None # Força reconexão na próxima vez
            last_sign = None # Reseta para permitir tentar de novo

@app.route('/receive_sign', methods=['POST'])
def receive_sign():
    data = request.json
    sign = data.get('sign')
    
    if not sign:
        return jsonify({"error": "Sinal ausente"}), 400

    # Roda em thread separada para não travar o vídeo do React
    threading.Thread(target=execute_action, args=(sign,)).start()

    return jsonify({"status": "received", "sign": sign})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
