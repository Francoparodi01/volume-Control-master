from flask import Flask, jsonify, request
from flask_cors import CORS
from ctypes import cast, POINTER, windll
from comtypes import CLSCTX_ALL, CoInitialize  
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

app = Flask(__name__)
CORS(app)  

def get_audio_sessions():
    # Inicializa COM
    CoInitialize()  

    # Obtiene todas las sesiones de audio
    sessions = AudioUtilities.GetAllSessions()
    session_data = []
    for session in sessions:
        if session.Process:
            volume = session.SimpleAudioVolume.GetMasterVolume()
            session_data.append({
                'name': session.Process.name(),
                'volume': volume
            })
    return session_data

@app.route('/volume', methods=['GET'])
def get_volumes():
    sessions = get_audio_sessions()
    return jsonify(sessions)

@app.route('/volume', methods=['POST'])
def set_volume():
    data = request.json
    app_name = data.get('name')
    volume_level = data.get('volume')

    # Encuentra la aplicación por nombre y ajusta su volumen
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.Process.name() == app_name:
            session.SimpleAudioVolume.SetMasterVolume(volume_level, None)
            return jsonify({'status': 'success', 'message': f'Volume for {app_name} set to {volume_level}'})
    return jsonify({'status': 'error', 'message': 'Application not found'}), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
