from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/api/download', methods=['GET'])
def download_video():
    # 1. Flutter app se URL lena
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({"success": False, "error": "URL is missing"}), 400

    # 2. yt-dlp ki settings (Sirf link nikalna hai, download nahi karna)
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best', # HD quality ke liye
    }

    try:
        # 3. Instagram se data nikalna
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Agar list format mein aaye
            if 'entries' in info:
                info = info['entries'][0]
            
            video_link = info.get('url', '')
            thumbnail = info.get('thumbnail', '')

            if video_link:
                return jsonify({
                    "success": True,
                    "data": {
                        "video_url": video_link,
                        "thumbnail": thumbnail
                    }
                })
            else:
                return jsonify({"success": False, "error": "Video link nahi mila"}), 404
                
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Server ko port 5000 par run karna
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)