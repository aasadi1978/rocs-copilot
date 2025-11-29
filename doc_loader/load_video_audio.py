import logging
from pathlib import Path
from typing import List

from langchain_core.documents import Document


def transcribe_audio(file_path: Path) -> List[Document]:
    """
    This function loads audio/video files and transcribes them using OpenAI Whisper.
    """
    try:
        import subprocess
        import os
        import tempfile
        
        # Add FFmpeg to PATH if it's installed in the common location
        ffmpeg_path = r"C:\ffmpeg\bin"
        if os.path.exists(ffmpeg_path) and ffmpeg_path not in os.environ["PATH"]:
            os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ["PATH"]
        
        # Check if ffmpeg is available
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True, text=True)
            logging.info("FFmpeg found and working")
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            logging.warning(f"Skipping {file_path.name}: FFmpeg not found in PATH. Error: {e}")
            print(f"Note: Add C:\\ffmpeg\\bin to your system PATH environment variable")
            return []
        
        logging.info(f"Transcribing audio/video file: {file_path.name}...")
        
        # Extract audio from video if needed (MP4, AVI, MOV)
        temp_audio = None
        audio_file_path = file_path
        
        if file_path.suffix.lower() in [".mp4", ".avi", ".mov"]:
            # First, check if video has audio stream
            probe_result = subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", 
                    "stream=codec_type", "-of", "default=nw=1:nk=1", str(file_path)],
                capture_output=True,
                text=True
            )
            
            if not probe_result.stdout.strip():
                logging.warning(f"Skipping {file_path.name}: Video has no audio stream")
                return []
            
            # Create temporary audio file
            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_audio.close()
            
            logging.info(f"Extracting audio from video: {file_path.name}")
            # Extract audio using FFmpeg
            result = subprocess.run(
                ["ffmpeg", "-i", str(file_path), "-vn", "-acodec", "libmp3lame", "-y", temp_audio.name],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg audio extraction failed: {result.stderr}")
            
            audio_file_path = Path(temp_audio.name)
            logging.info(f"Audio extracted to temporary file: {audio_file_path}")
        
        # Use OpenAI Whisper API
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        with open(audio_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        # Clean up temporary file
        if temp_audio:
            try:
                os.unlink(audio_file_path)
            except:
                pass
        
        # Create Document manually
        doc = Document(
            page_content=transcript.text,
            metadata={
                "source": str(file_path),
                "file_name": file_path.name
            }
        )
        documents = [doc]
        
        print(f"Transcription complete: {len(transcript.text)} characters")
        logging.info(f"Successfully transcribed {file_path.name}")

        return documents
            
    except Exception as e:
        # Clean up temp file on error
        if 'temp_audio' in locals() and temp_audio:
            try:
                os.unlink(temp_audio.name)
            except:
                pass
                
        logging.error(f"Error transcribing {file_path}: {e}")
        import traceback
        logging.debug(traceback.format_exc())
        logging.info(f"Note: Audio/video transcription requires:")
        logging.info(f"  1. OPENAI_API_KEY environment variable")
        logging.info(f"  2. FFmpeg in system PATH (C:\\ffmpeg\\bin)")
        logging.info(f"  3. openai package: pip install openai")
        logging.info(f"  Error details: {type(e).__name__}: {e}")
        logging.info(f"  2. FFmpeg in system PATH (C:\\ffmpeg\\bin)")

        return []
