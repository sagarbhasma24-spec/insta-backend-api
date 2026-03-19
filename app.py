from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route('/api/download', methods=['GET'])
def get_media_link():
    url = request.args.get('url')
    if not url:
        return jsonify({"success": False, "error": "URL is required!"}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best', 
        'cookiefile': 'cookies.txt', # Aapka mast Identity Card
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            media_items = []
            title = info.get('title', 'No Title')
            platform = info.get('extractor_key', 'Unknown')

            # NAYA JADOO: Ye function kabhi Photo ko Video nahi manega!
            def check_is_video(media_info):
                ext = media_info.get('ext', '').lower()
                if ext in ['jpg', 'jpeg', 'png', 'webp']:
                    return False
                if media_info.get('vcodec') == 'none':
                    return False
                return True

            if 'entries' in info:
                for entry in info['entries']:
                    media_url = entry.get('url') or entry.get('thumbnail')
                    if media_url: 
                        media_items.append({
                            "url": media_url,
                            "thumbnail": entry.get('thumbnail') or media_url,
                            "is_video": check_is_video(entry) # Smart Checking
                        })
            else:
                media_url = info.get('url') or info.get('thumbnail')
                media_items.append({
                    "url": media_url,
                    "thumbnail": info.get('thumbnail') or media_url,
                    "is_video": check_is_video(info) # Smart Checking
                })

            return jsonify({
                "success": True,
                "platform": platform,
                "title": title,
                "data": media_items
            })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
