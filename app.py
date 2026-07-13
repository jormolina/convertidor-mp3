import os
import glob
import yt_dlp
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)

CARPETA_MUSICA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "musica")
os.makedirs(CARPETA_MUSICA, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/musica/<path:filename>')
def serve_musica(filename):
    return send_from_directory(CARPETA_MUSICA, filename)

@app.route('/convertir', methods=['POST'])
def convertir():
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'Ingresa una URL'}), 400
    
    try:
        archivos_antes = set(glob.glob(os.path.join(CARPETA_MUSICA, "*.mp3")))
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(CARPETA_MUSICA, '%(title)s.%(ext)s'),
            'js_runtimes': {'node': {}},
            'ignoreerrors': True,
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if info is None:
                return jsonify({'error': 'No se pudo obtener información del video'}), 400
            
            es_playlist = 'entries' in info
            
            if es_playlist:
                entries = list(info['entries'])
                total = len(entries)
                
                ydl.download([url])
                
                archivos_despues = set(glob.glob(os.path.join(CARPETA_MUSICA, "*.mp3")))
                archivos_nuevos = sorted(archivos_despues - archivos_antes)
                
                primer_archivo = None
                if archivos_nuevos:
                    primer_archivo = os.path.basename(archivos_nuevos[0])
                
                return jsonify({
                    'success': True,
                    'es_playlist': True,
                    'total': total,
                    'mensaje': f'{total} archivos MP3 guardados',
                    'primer_archivo': primer_archivo
                })
            else:
                titulo = info.get('title', 'audio')
                
                ydl.download([url])
                
                archivo = f"{titulo}.mp3"
                
                return jsonify({
                    'success': True,
                    'es_playlist': False,
                    'titulo': titulo,
                    'mensaje': f'Guardado: {titulo}.mp3',
                    'archivo': archivo
                })
    
    except Exception as e:
        return jsonify({'error': str(e)[:200]}), 500

@app.route('/archivos')
def listar_archivos():
    archivos = glob.glob(os.path.join(CARPETA_MUSICA, "*.mp3"))
    archivos.sort(key=os.path.getmtime, reverse=True)
    return jsonify([os.path.basename(a) for a in archivos])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
