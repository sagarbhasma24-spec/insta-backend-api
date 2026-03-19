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
        'ignoreerrors': True,              # 👈 JADOO 1: Koi bhi error aaye, ignore karo!
        'ignore_no_formats_error': True,   # 👈 JADOO 2: Video na mile toh photo utha lo!
        'cookiefile': 'cookies.txt', 
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Agar data bilkul na mile
            if not info:
                return jsonify({"success": False, "error": "Could not fetch data. Private account or no media."}), 400
            
            media_items = []
            title = info.get('title', 'No Title')
            platform = info.get('extractor_key', 'Unknown')

            # Video aur Photo pehchanne ka engine
            def check_is_video(media_info):
                ext = media_info.get('ext', '').lower()
                if ext in ['jpg', 'jpeg', 'png', 'webp']:
                    return False
                if media_info.get('vcodec') == 'none':
                    return False
                return True

            # Agar bohot saari photos hain (Carousel)
            if 'entries' in info and info['entries']:
                for entry in info['entries']:
                    if entry: # Agar entry khali nahi hai
                        media_url = entry.get('url') or entry.get('thumbnail')
                        if media_url: 
                            media_items.append({
                                "url": media_url,
                                "thumbnail": entry.get('thumbnail') or media_url,
                                "is_video": check_is_video(entry)
                            })
            else:
                # Agar single photo ya video hai
                media_url = info.get('url') or info.get('thumbnail')
                if media_url:
                    media_items.append({
                        "url": media_url,
                        "thumbnail": info.get('thumbnail') or media_url,
                        "is_video": check_is_video(info)
                    })

            # Agar fir bhi kuch na mile
            if not media_items:
                return jsonify({"success": False, "error": "No media found in the link."}), 400

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
