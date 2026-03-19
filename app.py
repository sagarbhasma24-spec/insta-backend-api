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
        # Aapke cookies.txt ka use karke Instagram ko Insaan lagne ka jadoo
        cj = http.cookiejar.MozillaCookieJar('cookies.txt')
        cj.load(ignore_discard=True, ignore_expires=True)
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        
        # Ek Asli Browser hone ka natak (User-Agent)
        opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'),
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8')
        ]
        
        response = opener.open(url, timeout=15)
        html = response.read().decode('utf-8')
        
        # HTML coding me se direct HD photo (og:image) ka link chura lena
        match = re.search(r'<meta property="og:image" content="([^"]+)"', html)
        if match:
            img_url = match.group(1).replace('&amp;', '&')
            return img_url
    except Exception as e:
        print("Photo extraction failed:", e)
    return None


@app.route('/api/download', methods=['GET'])
def insta_downloader():
    url = request.args.get('url')
    
    # Check 1: Agar link khali hai ya Instagram ka nahi hai
    if not url or 'instagram.com' not in url:
        return jsonify({"success": False, "error": "Please provide a valid Instagram link!"}), 400

    # 🎥 ENGINE 1: Reels, Video, aur Story nikalne ke liye
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True, # Koi chota error aaye toh usko ignore karo
        'cookiefile': 'cookies.txt', # Aapka Identity Card
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Agar Engine 1 ko data mil jata hai (Reels/Video)
            if info and ('entries' in info or info.get('url') or info.get('vcodec') != 'none'):
                media_items = []
                
                # Agar ek sath bohot saari video/photo hain (Carousel)
                if 'entries' in info and info['entries']:
                    for entry in info['entries']:
                        if entry:
                            m_url = entry.get('url') or entry.get('thumbnail')
                            is_vid = entry.get('ext') == 'mp4' or entry.get('vcodec') != 'none'
                            if m_url:
                                media_items.append({"url": m_url, "thumbnail": entry.get('thumbnail') or m_url, "is_video": is_vid})
                
                # Agar single Reel ya Story hai
                else:
                    m_url = info.get('url') or info.get('thumbnail')
                    is_vid = info.get('ext') == 'mp4' or info.get('vcodec') != 'none'
                    if m_url:
                        media_items.append({"url": m_url, "thumbnail": info.get('thumbnail') or m_url, "is_video": is_vid})

                if media_items:
                    print("✅ ENGINE 1 SUCCESS: Video/Reel found!")
                    return jsonify({
                        "success": True,
                        "platform": "Instagram",
                        "data": media_items
                    })

    except Exception as e:
        print("Engine 1 failed, starting Engine 2...", e)

    # 📸 ENGINE 2 TRIGGER: Agar Engine 1 fail ho gaya (Kyunki wo Photo post thi)
    photo_url = get_instagram_photo(url)
    
    if photo_url:
        print("✅ ENGINE 2 SUCCESS: Photo Post found!")
        return jsonify({
            "success": True,
            "platform": "Instagram",
            "data": [{
                "url": photo_url,
                "thumbnail": photo_url,
                "is_video": False # Flutter app ko bata do ki ye photo hai
            }]
        })

    # Agar dono Engine fail ho jayein (Account private ho ya link galat ho)
    return jsonify({"success": False, "error": "Could not download media. Post might be from a Private Account."}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
