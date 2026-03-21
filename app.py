import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ==========================================
# 🚀 RAPID-API SETTINGS (Premium POST Engine)
# ==========================================
RAPIDAPI_HOST = "instagram120.p.rapidapi.com"

# 👉 NEECHE WALI LINE MEIN APNI SECRET KEY PASTE KAREIN:
RAPIDAPI_KEY = "4235a82a72msh13a79567a3dc3fap1010b5jsn82fdb958a826" 

# URL wahi sahi wala hai:
RAPIDAPI_URL = "https://instagram120.p.rapidapi.com/api/instagram/links" 

# 🧠 SMART JSON SCANNER
def extract_media(data):
    urls = []
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str) and value.startswith("http"):
                if ".mp4" in value or "video" in key.lower():
                    urls.append({"url": value, "is_video": True})
                elif ".jpg" in value or ".webp" in value or "thumbnail" in key.lower() or "image" in key.lower() or "cover" in key.lower():
                    urls.append({"url": value, "is_video": False})
            else:
                urls.extend(extract_media(value))
    elif isinstance(data, list):
        for item in data:
            urls.extend(extract_media(item))
    return urls

@app.route('/api/download', methods=['GET'])
def insta_downloader():
    insta_url = request.args.get('url')
    
    if not insta_url:
        return jsonify({"success": False, "error": "Instagram URL is required"}), 400

    # 👉 JADOO YAHAN HAI: Ab data ko POST (JSON) format mein bhej rahe hain
    payload = {"url": insta_url} 
    
    headers = {
        "x-rapidapi-host": RAPIDAPI_HOST,
        "x-rapidapi-key": RAPIDAPI_KEY,
        "Content-Type": "application/json" # API ko batana zaroori hai ki data JSON hai
    }

    try:
        # 👉 JADOO 2: requests.get() ko hata kar requests.post() kar diya hai
        response = requests.post(RAPIDAPI_URL, json=payload, headers=headers, timeout=15)
        api_data = response.json()
        
        media_list = extract_media(api_data)
        
        videos = [m for m in media_list if m['is_video']]
        images = [m for m in media_list if not m['is_video']]
        
        final_data = []
        
        if videos:
            print("✅ API SUCCESS: Asli MP4 Video Mil Gayi!")
            final_data.append({
                "url": videos[0]['url'],
                "thumbnail": images[0]['url'] if images else videos[0]['url'],
                "is_video": True
            })
        elif images:
            print("📸 API SUCCESS: Sirf Photo Mili!")
            final_data.append({
                "url": images[0]['url'],
                "thumbnail": images[0]['url'],
                "is_video": False
            })

        if final_data:
            return jsonify({
                "success": True,
                "platform": "Instagram",
                "data": final_data
            })
        else:
            return jsonify({
                "success": False, 
                "error": "Could not find video link in API response.",
                "raw_api_response": api_data
            }), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
