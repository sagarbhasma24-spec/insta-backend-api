import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ==========================================
# 🚀 RAPID-API SETTINGS (Yahan Apni Details Dalein)
# ==========================================
RAPIDAPI_HOST = "instagram120.p.rapidapi.com"

# 👉 NEECHE WALI LINE MEIN APNI SECRET KEY PASTE KAREIN:
RAPIDAPI_KEY = "4235a82a72msh13a79567a3dc3fap1010b5jsn82fdb958a826" 

# RapidAPI dashboard ke "Code Snippet" se exact URL check kar lein, mostly yahi hota hai:
RAPIDAPI_URL = f"https://{RAPIDAPI_HOST}/api/instagram/links" 


# 🧠 SMART JSON SCANNER (API ke data mein se video dhoondhne ke liye)
def extract_media(data):
    urls = []
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str) and value.startswith("http"):
                # Agar link mein .mp4 hai ya key ka naam video hai
                if ".mp4" in value or "video" in key.lower():
                    urls.append({"url": value, "is_video": True})
                # Agar link photo ka hai
                elif ".jpg" in value or ".webp" in value or "thumbnail" in key.lower() or "image" in key.lower():
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

    # API ko request bhejenge (Kuch APIs parameter ka naam 'url' leti hain, kuch 'ig')
    querystring = {"url": insta_url} 
    
    headers = {
        "x-rapidapi-host": RAPIDAPI_HOST,
        "x-rapidapi-key": RAPIDAPI_KEY
    }

    try:
        # RapidAPI server ko hit karna
        response = requests.get(RAPIDAPI_URL, headers=headers, params=querystring, timeout=15)
        api_data = response.json()
        
        # Smart Scanner ko chalana
        media_list = extract_media(api_data)
        
        # Videos aur Photos ko alag karna
        videos = [m for m in media_list if m['is_video']]
        images = [m for m in media_list if not m['is_video']]
        
        final_data = []
        
        if videos:
            print("✅ API SUCCESS: Asli Video Mil Gayi!")
            final_data.append({
                "url": videos[0]['url'],
                "thumbnail": images[0]['url'] if images else videos[0]['url'],
                "is_video": True
            })
        elif images:
            print("📸 API SUCCESS: Photo Mil Gayi!")
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
                "error": "API did not return a valid video. Ensure the RapidAPI URL is correct.",
                "raw_api_response": api_data
            }), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
