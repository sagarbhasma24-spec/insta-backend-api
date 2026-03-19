from flask import Flask, request, jsonify
import yt_dlp
import os
import urllib.request
import http.cookiejar
import re

app = Flask(__name__)

# 🚀 THE MASTERSTROKE FALLBACK ENGINE FOR INSTAGRAM PHOTOS
def get_insta_photo_fallback(url):
    try:
        # Aapke cookies.txt ka use karke Instagram ko Insaan lagne ka jadoo
        cj = http.cookiejar.MozillaCookieJar('cookies.txt')
        cj.load(ignore_discard=True, ignore_expires=True)
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        # Mobile ka bhes badalna (User-Agent)
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1')]
        
        response = opener.open(url, timeout=10)
        html = response.read().decode('utf-8')
        
        # HTML coding me se direct HD photo ka link chura lena
        match = re.search(r'<meta property="og:image" content="([^"]+)"', html)
        if match:
            img_url = match.group(1).replace('&amp;', '&')
            return img_url
    except Exception as e:
        print("Fallback Error:", e)
        pass
    return None

@app.route('/api/download', methods=['GET'])
def get_media_link():
    url = request.args.get('url')
    if not url:
        return jsonify({"success": False, "error": "URL is required!"}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'cookiefile': 'cookies.txt', 
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if not info:
                raise Exception("Empty data from yt-dlp")
                
            media_items = []
            title = info.get('title', 'No Title')
            platform = info.get('extractor_key', 'Unknown')

            def check_is_video(media_info):
                ext = media_info.get('ext', '').lower()
                if ext in ['jpg', 'jpeg', 'png', 'webp']:
                    return False
                if media_info.get('vcodec') == 'none':
                    return False
                return True

            if 'entries' in info and info['entries']:
                for entry in info['entries']:
                    if entry:
                        media_url = entry.get('url') or entry.get('thumbnail')
                        if media_url: 
                            media_items.append({
                                "url": media_url,
                                "thumbnail": entry.get('thumbnail') or media_url,
                                "is_video": check_is_video(entry)
                            })
            else:
                media_url = info.get('url') or info.get('thumbnail')
                if media_url:
                    media_items.append({
                        "url": media_url,
                        "thumbnail": info.get('thumbnail') or media_url,
                        "is_video": check_is_video(info)
                    })

            if not media_items:
                raise Exception("No media found in the link.")

            return jsonify({
                "success": True,
                "platform": platform,
                "title": title,
                "data": media_items
            })

    except Exception as e:
        error_msg = str(e)
        
        # JADOO: Agar yt-dlp Instagram Photo par fail ho jaye, toh apna Fallback Engine chalana!
        if "No video formats found" in error_msg or "Instagram" in error_msg:
            fallback_img_url = get_insta_photo_fallback(url)
            
            if fallback_img_url:
                print("✅ FALLBACK ENGINE SUCCESS: Photo Extracted!")
                return jsonify({
                    "success": True,
                    "platform": "Instagram",
                    "title": "Instagram Photo",
                    "data": [{
                        "url": fallback_img_url,
                        "thumbnail": fallback_img_url,
                        "is_video": False # App ko bata do ki ye video nahi, Photo hai
                    }]
                })

        # Agar fallback bhi fail ho jaye
        return jsonify({"success": False, "error": error_msg}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
