from flask import Flask
from pyngrok import ngrok
from decouple import config
from src.Routes.route import routes

# Crear aplicación Flask
app = Flask(__name__)

# Registrar rutas
app.register_blueprint(routes)

if __name__ == '__main__':
    try:
        # Leer token de ngrok desde .env
        ngrok_token = config('NGROK_TOKEN')

        # Configurar ngrok
        if ngrok_token and ngrok_token != 'TU_TOKEN_AQUI':
            ngrok.set_auth_token(ngrok_token)
            public_url = ngrok.connect(5000)
            print(f'\n * ngrok tunnel: {public_url}\n')
        else:
            print('\n * NGROK_TOKEN no configurado. La app solo estará disponible localmente.\n')

    except Exception as e:
        print(f'\n * No se pudo iniciar ngrok: {e}\n')
        print(' * La app solo estará disponible localmente.\n')

    # Iniciar servidor Flask
    print(' * Starting Flask app...')
    app.run(debug=False, port=5000)
