from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/api/download', methods=['GET'])
def download():
    url = request.args.get('url')
    if not url:
        return jsonify({"success": False, "error": "URL is required"}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Agar post mein ek se zyada photos/videos (Carousel) hain
            if 'entries' in info:
                info = info['entries'][0] # Abhi ke liye pehla photo/video lenge
            
            # Smart Check: Ye video hai ya photo?
            is_video = True
            if info.get('ext') in ['jpg', 'jpeg', 'png', 'webp'] or info.get('vcodec') == 'none':
                is_video = False

            # Asli HD link nikalna
            media_url = info.get('url')
            if not media_url and not is_video:
                media_url = info.get('thumbnail')

            return jsonify({
                "success": True,
                "data": {
                    "video_url": media_url, # Link isme aayega
                    "thumbnail": info.get('thumbnail') or media_url,
                    "is_video": is_video # Flutter app ko batayega ki photo hai ya video
                }
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
