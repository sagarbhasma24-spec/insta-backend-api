from flask import Flask, request, jsonify
import yt_dlp
import os
import urllib.request
import http.cookiejar
import re

app = Flask(__name__)

# 🚀 ENGINE 3: DIRECT VIDEO SCRAPER (The Brahmastra - Instagram ko bypass karne ke liye)
def get_direct_video(url):
    try:
        cj = http.cookiejar.MozillaCookieJar('cookies.txt')
        try:
            cj.load(ignore_discard=True, ignore_expires=True)
        except:
            pass # Agar cookies nahi hain toh bhi try karega
        
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'),
        ]
        response = opener.open(url, timeout=15)
        html = response.read().decode('utf-8')
        
        # HTML ke andar chhupa hua direct MP4 link nikalna
        match = re.search(r'<meta property="og:video" content="([^"]+)"', html)
        if match:
            return match.group(1).replace('&amp;', '&')
    except Exception as e:
        print("Direct Video Scraper Failed:", e)
    return None

# 📸 ENGINE 2: DIRECT PHOTO SCRAPER
def get_instagram_photo(url):
    try:
        cj = http.cookiejar.MozillaCookieJar('cookies.txt')
        try:
            cj.load(ignore_discard=True, ignore_expires=True)
        except:
            pass
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'),
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

    # Check karna ki user ne Reel/Video bheji hai ya kuch aur
    is_reel_url = '/reel/' in url or '/tv/' in url or '/v/' in url

    # 🚀 STEP 1: Agar Reel hai, toh pehle Direct Scraper (Brahmastra) chalao
    if is_reel_url:
        direct_vid_url = get_direct_video(url)
        if direct_vid_url and '.mp4' in direct_vid_url:
            print("✅ ENGINE 3 SUCCESS: Asli MP4 Reel Mil Gayi!")
            return jsonify({
                "success": True, 
                "platform": "Instagram", 
                "data": [{"url": direct_vid_url, "thumbnail": direct_vid_url, "is_video": True}]
            })

    # 🎥 STEP 2: Agar Direct Scraper fail ho jaye, tab yt-dlp use karo
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', 
        'cookiefile': 'cookies.txt',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if info:
                extracted_url = info.get('url')
                if extracted_url:
                    # STRICT CHECK: Agar yt-dlp photo (.jpg) de raha hai aur link reel ka hai, toh REJECT karo!
                    if ('.jpg' in extracted_url or '.webp' in extracted_url) and is_reel_url:
                        print("❌ yt-dlp trying to fake video with image. Rejecting!")
                    else:
                        is_vid = info.get('ext') == 'mp4' or info.get('vcodec') != 'none' or '.mp4' in extracted_url
                        if is_vid:
                            return jsonify({
                                "success": True, 
                                "platform": "Instagram", 
                                "data": [{"url": extracted_url, "thumbnail": info.get('thumbnail') or extracted_url, "is_video": True}]
                            })
    except Exception as e:
        print("yt-dlp Exception:", e)

    # 📸 STEP 3: Agar link kisi Photo post ka hai, toh photo nikal lo
    photo_url = get_instagram_photo(url)
    if photo_url:
        return jsonify({
            "success": True,
            "platform": "Instagram",
            "data": [{"url": photo_url, "thumbnail": photo_url, "is_video": False}]
        })

    # Agar teeno engine fail ho jayein
    return jsonify({"success": False, "error": "Could not extract video. Account might be private."}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
