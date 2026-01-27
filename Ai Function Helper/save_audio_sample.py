import httpx
import base64
import os

def save_audio():
    url = "http://127.0.0.1:9696/learn"
    payload = {"word": "Working"}
    
    print(f"Requesting {url}...")
    try:
        response = httpx.post(url, json=payload, timeout=30.0)
        response.raise_for_status()
        
        data = response.json()
        audio_b64 = data.get("pronunciation_audio")
        
        if not audio_b64:
            print("No audio found in response!")
            return

        audio_bytes = base64.b64decode(audio_b64)
        filename = "debug_output.wav"
        
        with open(filename, "wb") as f:
            f.write(audio_bytes)
            
        print(f"Success! Audio saved to: {os.path.abspath(filename)}")
        print("You can listen to it using a media player or command line tools like 'aplay'.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    save_audio()
