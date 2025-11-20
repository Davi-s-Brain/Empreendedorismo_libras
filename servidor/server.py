from flask import Flask, request, jsonify
from flask_cors import CORS
from yeelight import Bulb
import threading

app = Flask(__name__)
CORS(app) 

# CONFIGURAÇÃO DA LÂMPADA
BULB_IP = "192.168.1.X" # IP da lâmpada

# try:
#     bulb = Bulb(BULB_IP)
#     bulb.turn_on()
# except Exception as e:
#     print(f"Erro ao conectar na lâmpada: {e}")

# Mapeamento de Sinais para Cores (RGB)
# Exemplo: A = Vermelho, B = Azul, C = Verde
ACTIONS = {
    "L": (255, 0, 0),     # Vermelho
    "A": (0, 0, 255),     # Azul
    "C": (0, 255, 0),     # Verde
    "thumbs_up": "TOGGLE" # Liga/Desliga
}

def change_light(sign):
    """Função auxiliar para mudar a luz sem travar a requisição"""
    try:
        if sign in ACTIONS:
            action = ACTIONS[sign]
            
            if action == "TOGGLE":
                bulb.toggle()
            else:
                # Define a cor RGB
                bulb.set_rgb(action[0], action[1], action[2])
                
            print(f"Comando executado para sinal: {sign}")
        else:
            print(f"Sinal recebido sem ação configurada: {sign}")
    except Exception as e:
        print(f"Erro ao controlar lâmpada: {e}")

@app.route('/receive_sign', methods=['POST'])
def receive_sign():
    data = request.json
    sign = data.get('sign')
    
    if not sign:
        return jsonify({"error": "Sinal não fornecido"}), 400

    print(f"Sinal Recebido: {sign}")

    # Executa a mudança de luz em uma thread separada para responder rápido ao React
    threading.Thread(target=change_light, args=(sign,)).start()

    return jsonify({"status": "success", "sign": sign})

if __name__ == '__main__':
    # Roda o servidor na porta 5000
    app.run(host='0.0.0.0', port=5000, debug=True)