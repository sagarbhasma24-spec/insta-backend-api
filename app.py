from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/api/download', methods=['GET'])
def get_media_link():
    url = request.args.get('url')
    if not url:
        return jsonify({"success": False, "error": "URL is required!"}), 400

    # All-in-One Universal Settings
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best', # Har platform se sabse best quality nikalega
        # WARNING: Instagram/Facebook ke liye cookies.txt hona zaroori hai
        'cookiefile': 'cookies.txt', 
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info bina download kiye
            info = ydl.extract_info(url, download=False)
            
            media_items = []
            title = info.get('title', 'No Title')
            platform = info.get('extractor_key', 'Unknown') # Batayega ki link kahan ka hai (Youtube, Instagram, etc.)

            # JADOO: Agar Instagram post mein 2-4 photos/videos ek sath hain (Carousel), ya YouTube Playlist hai
            if 'entries' in info:
                for entry in info['entries']:
                    is_video = entry.get('ext') in ['mp4', 'webm'] or entry.get('vcodec') != 'none'
                    media_url = entry.get('url') or entry.get('thumbnail')
                    if media_url: # Sirf valid links lenge
                        media_items.append({
                            "url": media_url,
                            "thumbnail": entry.get('thumbnail') or media_url,
                            "is_video": is_video
                        })
            else:
                # Single Video, Photo ya Reel
                is_video = info.get('ext') in ['mp4', 'webm'] or info.get('vcodec') != 'none'
                media_url = info.get('url') or info.get('thumbnail')
                media_items.append({
                    "url": media_url,
                    "thumbnail": info.get('thumbnail') or media_url,
                    "is_video": is_video
                })

            # Flutter app ko mast format mein data bhejna
            return jsonify({
                "success": True,
                "platform": platform, # App mein logo dikhane ke kaam aayega!
                "title": title,
                "data": media_items # Isme saari photos/videos ki list hogi
            })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    # Render cloud ke liye port binding
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
