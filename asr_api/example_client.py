"""
Example usage of T-one ASR API

This script demonstrates how to use the API for speech recognition.
"""

import requests
import json
from pathlib import Path


def transcribe_file(audio_path: str, api_url: str = "http://localhost:8000"):
    """
    Transcribe speech from audio file (offline mode)
    
    Args:
        audio_path: Path to audio file
        api_url: API server URL
    """
    print(f"\n{'='*60}")
    print(f"Transcribing file: {audio_path}")
    print(f"{'='*60}")
    
    url = f"{api_url}/transcribe"
    
    with open(audio_path, "rb") as f:
        files = {"file": f}
        data = {"return_timestamps": True}
        
        response = requests.post(url, files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n✓ Successfully transcribed!")
        print(f"\nFull text:")
        print(f"  {result['full_text']}")
        print(f"\nDetails:")
        print(f"  Audio duration: {result['duration']:.2f} sec")
        print(f"  Processing time: {result['processing_time']:.2f} sec")
        print(f"  Number of phrases: {len(result['phrases'])}")
        
        if result['phrases']:
            print(f"\nPhrases with timestamps:")
            for i, phrase in enumerate(result['phrases'], 1):
                print(f"  {i}. [{phrase['start_time']:.2f}s - {phrase['end_time']:.2f}s] {phrase['text']}")
        
        return result
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"  {response.text}")
        return None


def streaming_example(chunk_files: list, api_url: str = "http://localhost:8000"):
    """
    Example of streaming mode usage
    
    Args:
        chunk_files: List of paths to audio chunks
        api_url: API server URL
    """
    print(f"\n{'='*60}")
    print(f"Streaming recognition ({len(chunk_files)} chunks)")
    print(f"{'='*60}")
    
    print("\n1. Starting streaming session...")
    response = requests.post(f"{api_url}/transcribe/streaming")
    
    if response.status_code != 200:
        print(f"✗ Error creating session: {response.status_code}")
        return None
    
    state_id = response.json()["state_id"]
    print(f"✓ Session created: {state_id[:8]}...")
    
    all_phrases = []
    
    print(f"\n2. Processing {len(chunk_files)} chunks...")
    for i, chunk_file in enumerate(chunk_files, 1):
        print(f"   Chunk {i}/{len(chunk_files)}: {Path(chunk_file).name}")
        
        with open(chunk_file, "rb") as f:
            files = {"file": f}
            data = {"state_id": state_id}
            
            response = requests.post(
                f"{api_url}/transcribe/streaming/chunk",
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            result = response.json()
            phrases = result["phrases"]
            all_phrases.extend(phrases)
            
            if phrases:
                print(f"     → Recognized {len(phrases)} new phrases:")
                for phrase in phrases:
                    print(f"       [{phrase['start_time']:.2f}s - {phrase['end_time']:.2f}s] {phrase['text']}")
            else:
                print(f"     → No new phrases yet")
        else:
            print(f"     ✗ Error: {response.status_code}")
            print(f"       {response.text}")
    
    print(f"\n3. Finalizing session...")
    response = requests.post(
        f"{api_url}/transcribe/streaming/finalize",
        data={"state_id": state_id}
    )
    
    if response.status_code == 200:
        result = response.json()
        final_phrases = result["phrases"]
        all_phrases.extend(final_phrases)
        
        if final_phrases:
            print(f"✓ Final phrases ({len(final_phrases)}):")
            for phrase in final_phrases:
                print(f"  [{phrase['start_time']:.2f}s - {phrase['end_time']:.2f}s] {phrase['text']}")
        
        print(f"\n✓ Streaming completed. Total {len(all_phrases)} phrases recognized.")
        
        full_text = " ".join([p["text"] for p in all_phrases])
        print(f"\nFull text:")
        print(f"  {full_text}")
        
        return all_phrases
    else:
        print(f"✗ Error finalizing: {response.status_code}")
        print(f"  {response.text}")
        return None


def check_api_health(api_url: str = "http://localhost:8000"):
    """Check API status"""
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API is running")
            print(f"  Status: {data['status']}")
            print(f"  Model loaded: {data['model_loaded']}")
            return True
        else:
            print(f"✗ API returned error: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ Failed to connect to API at {api_url}")
        print(f"  Make sure the server is running")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    print("T-one ASR API - Usage Example")
    print("="*60)
    
    print("\nChecking API availability...")
    if not check_api_health():
        print("\nStart the server with:")
        print("  make run")
        print("  or")
        print("  poetry run uvicorn asr_api.main:app --host 0.0.0.0 --port 8000")
        exit(1)
    
    # Example 1: Offline recognition
    # Uncomment and specify path to your audio file
    # transcribe_file("path/to/your/audio.wav")
    
    # Example 2: Streaming recognition
    # Uncomment and specify paths to chunks
    # chunk_files = ["chunk1.wav", "chunk2.wav", "chunk3.wav"]
    # streaming_example(chunk_files)
    
    print("\n" + "="*60)
    print("Examples are commented out. Uncomment the desired example")
    print("and specify paths to your audio files.")


