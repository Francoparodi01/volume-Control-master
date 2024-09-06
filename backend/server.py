from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from ctypes import cast, POINTER, windll
from comtypes import CLSCTX_ALL, CoInitialize  
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from PIL import Image
import win32api
import win32gui
import win32con
import io
import os
import psutil

app = Flask(__name__)
CORS(app)

def get_audio_sessions():
    try:
        CoInitialize()
        sessions = AudioUtilities.GetAllSessions()
        session_data = []
        for session in sessions:
            if session.Process:
                volume = session.SimpleAudioVolume.GetMasterVolume()
                exe_path = session.Process.exe()  # Obtiene la ruta del ejecutable del proceso
                icon = get_icon_from_exe(exe_path)
                session_data.append({
                    'name': session.Process.name(),
                    'volume': volume,
                    'icon': icon
                })
        return session_data
    except Exception as e:
        print(f"Error getting audio sessions: {e}")
        return []

def get_icon_from_exe(exe_path):
    try:
        large, _ = win32gui.ExtractIconEx(exe_path, 0)
        if large:
            hicon = large[0]
            hdc = win32gui.CreateCompatibleDC(0)
            hbmp = win32gui.CreateCompatibleBitmap(hdc, 32, 32)
            hbm_old = win32gui.SelectObject(hdc, hbmp)

            win32gui.DrawIconEx(hdc, 0, 0, hicon, 32, 32, 0, None, win32con.DI_NORMAL)

            bmpinfo = win32gui.GetObject(hbmp)
            bmpstr = win32gui.GetBitmapBits(hbmp, True)

            img = Image.frombuffer('RGB', (bmpinfo.bmWidth, bmpinfo.bmHeight), bmpstr, 'raw', 'BGRX', 0, 1)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)

            win32gui.SelectObject(hdc, hbm_old)
            win32gui.DeleteObject(hbmp)
            win32gui.DeleteDC(hdc)
            win32gui.DestroyIcon(hicon)

            return img_byte_arr.getvalue().hex()  # Retorna el ícono como una cadena hexadecimal
    except Exception as e:
        print(f"Error getting icon: {e}")
        return None

@app.route('/volume', methods=['GET'])
def get_volumes():
    sessions = get_audio_sessions()
    return jsonify(sessions)

@app.route('/volume', methods=['POST'])
def set_volume():
    data = request.json
    app_name = data.get('name')
    volume_level = data.get('volume')

    if app_name is None or volume_level is None:
        return jsonify({'status': 'error', 'message': 'Invalid input data'}), 400

    try:
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and session.Process.name() == app_name:
                session.SimpleAudioVolume.SetMasterVolume(volume_level, None)
                return jsonify({'status': 'success', 'message': f'Volume for {app_name} set to {volume_level}'})
        return jsonify({'status': 'error', 'message': 'Application not found'}), 404
    except Exception as e:
        print(f"Error setting volume: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to set volume'}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
