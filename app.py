from flask import Flask, request, jsonify
import yt_dlp
import os
import urllib.request
import http.cookiejar
import re

app = Flask(__name__)

# 📸 ENGINE 2: Sirf Instagram Photos ke liye Custom Scraper
def get_instagram_photo(url):
    try:
        cj = http.cookiejar.MozillaCookieJar('cookies.txt')
        cj.load(ignore_discard=True, ignore_expires=True)
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'),
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8')
        ]
        response = opener.open(url, timeout=15)
        html = response.read().decode('utf-8')
        match = re.search(r'<meta property="og:image" content="([^"]+)"', html)
        if match:
            return match.group(1).replace('&amp;', '&')
    except Exception as e:
        print("Photo extraction failed:", e)
    return None

@app.route('/api/download', methods=['GET'])
def insta_downloader():
    url = request.args.get('url')
    if not url or 'instagram.com' not in url:
        return jsonify({"success": False, "error": "Invalid Instagram URL"}), 400

    # 🎥 ENGINE 1: Reels aur Video ke liye (STRICT MODE)
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        # 👇 NAYA JADOO: Strict order de rahe hain ki Best Video hi chahiye
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', 
        'cookiefile': 'cookies.txt',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if info:
                media_items = []
                
                # Check karne ka naya, strict function
                def get_real_url(entry):
                    # 1. Pehle dekho kya direct video url hai (formats ke andar)
                    if 'formats' in entry:
                        for f in reversed(entry['formats']):
                            # Agar us format me video codec hai aur format mp4 ya aisi koi video format hai
                            if f.get('vcodec') != 'none' and f.get('ext') in ['mp4', 'webm', 'mov']:
                                return f.get('url'), True
                    
                    # 2. Agar formats me na mile, toh main url check karo
                    main_url = entry.get('url')
                    if main_url:
                        # Agar main url .jpg nahi hai toh wo video hai
                        if '.jpg' not in main_url and '.webp' not in main_url:
                             return main_url, True
                        
                    return None, False

                if 'entries' in info and info['entries']:
                    for entry in info['entries']:
                        if entry:
                            real_url, is_vid = get_real_url(entry)
                            if real_url:
                                media_items.append({
                                    "url": real_url, 
                                    "thumbnail": entry.get('thumbnail') or real_url, 
                                    "is_video": True # Hum strict ho gaye hain
                                })
                else:
                    real_url, is_vid = get_real_url(info)
                    if real_url:
                        media_items.append({
                            "url": real_url, 
                            "thumbnail": info.get('thumbnail') or real_url, 
                            "is_video": True
                        })

                if media_items:
                    print("✅ ENGINE 1 SUCCESS: Asli Video mili!")
                    return jsonify({"success": True, "platform": "Instagram", "data": media_items})
                else:
                     print("Engine 1 failed to find pure video url.")
    except Exception as e:
        print("Engine 1 Exception:", e)

    # 📸 ENGINE 2 TRIGGER: Agar yt-dlp sach me sirf photo wali post hai toh
    photo_url = get_instagram_photo(url)
    if photo_url:
        return jsonify({
            "success": True,
            "platform": "Instagram",
            "data": [{"url": photo_url, "thumbnail": photo_url, "is_video": False}]
        })

    return jsonify({"success": False, "error": "Media nahi mila. Ya toh account private hai, ya cookies expire ho gayi hain."}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
