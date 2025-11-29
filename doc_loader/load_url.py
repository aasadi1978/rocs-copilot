import logging
import time
import random
from pathlib import Path
from typing import List, Union

import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders import YoutubeLoader
from langchain_core.documents import Document


# Handle URLs separately
def transcribe_url(file_path: Union[str, Path]) -> List[Document]:

    if isinstance(file_path, str) and file_path.lower().startswith("http"):
        # Check if it's a YouTube URL
        if "youtube.com" in file_path.lower() or "youtu.be" in file_path.lower():
            # Add delay to avoid rate limiting (YouTube blocks IPs that make too many requests)
            delay = random.uniform(2, 5)  # Random delay between 2-5 seconds
            logging.info(f"Waiting {delay:.1f}s before YouTube request (rate limit protection)...")
            time.sleep(delay)
            
            # Try multiple strategies to load YouTube content
            # Note: add_video_info=True often causes HTTP 400 errors, so we avoid it
            strategies = [
                # Strategy 1: Standard approach without video info
                lambda: YoutubeLoader.from_youtube_url(
                    file_path,
                    add_video_info=False,
                    language=["en", "en-US"],
                ),
                # Strategy 2: Try with single language code
                lambda: YoutubeLoader.from_youtube_url(
                    file_path,
                    add_video_info=False,
                    language=["en"],
                ),
                # Strategy 3: Minimal config
                lambda: YoutubeLoader.from_youtube_url(
                    file_path,
                    add_video_info=False,
                ),
            ]
            
            for i, strategy in enumerate(strategies, 1):
                try:
                    logging.info(f"Trying YouTube loading strategy {i}...")
                    loader = strategy()
                    documents = loader.load()
                    if documents and documents[0].page_content.strip():
                        logging.info(f"✓ YouTube video loaded successfully: {len(documents[0].page_content)} characters")
                        return documents
                    else:
                        logging.warning(f"Strategy {i} returned empty content")
                except Exception as e:
                    logging.warning(f"Strategy {i} failed: {type(e).__name__}: {e}")
                    if i < len(strategies):
                        # Add small delay between retry attempts
                        time.sleep(1)
                    if i == len(strategies):
                        # Check if it's a rate limiting error
                        error_str = str(e).lower()
                        if "429" in str(e) or "too many requests" in error_str or "blocked" in error_str or "ip" in error_str:
                            logging.error(f"⚠️  YouTube has blocked your IP due to rate limiting")
                            logging.error("Solutions:")
                            logging.error("  1. Wait 15-30 minutes before trying again")
                            logging.error("  2. Use a VPN or switch to a different network")
                            logging.error("  3. Restart your router to get a new IP address")
                            logging.error("  4. Reduce the number of YouTube videos you're loading at once")
                        else:
                            logging.error(f"All strategies failed for YouTube video {file_path}")
                            logging.error(f"Last error: {e}")
                            logging.info("Troubleshooting tips:")
                            logging.info("  1. Ensure yt-dlp is up to date: pip install -U yt-dlp")
                            logging.info("  2. Check if the video has captions/subtitles enabled")
                            logging.info("  3. Try a different video or verify the URL is correct")
                            logging.info("  4. Some videos may have restrictions preventing transcript access")
            return []
        # Regular web page
        else:
            try:
                # Use direct requests instead of WebBaseLoader to avoid Flask context issues
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                }
                
                logging.info(f"Loading web page: {file_path}")
                response = requests.get(file_path, headers=headers, timeout=30)
                response.raise_for_status()
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try to extract main content
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Try common article selectors
                content = None
                selectors = [
                    'article',
                    '[class*="article"]',
                    '[class*="content"]',
                    '[class*="post"]',
                    'main',
                    '[role="main"]',
                ]
                
                for selector in selectors:
                    elements = soup.select(selector)
                    if elements:
                        content = elements[0].get_text(separator='\n', strip=True)
                        if len(content) > 500:  # Found substantial content
                            break
                
                # Fallback to body if no good content found
                if not content or len(content) < 500:
                    content = soup.get_text(separator='\n', strip=True)
                
                # Clean up excessive whitespace
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                content = '\n'.join(lines)
                
                if len(content) < 100:
                    logging.warning(f"Very little content extracted from {file_path}")
                    return []
                
                # Create Document object
                document = Document(
                    page_content=content,
                    metadata={"source": file_path, "title": soup.title.string if soup.title else ""}
                )
                
                logging.info(f"✓ Web page loaded: {len(content)} characters")
                return [document]
                
            except requests.exceptions.RequestException as e:
                logging.error(f"Error loading {file_path}: {e}")
                logging.info("Tip: The website may be blocking automated requests or is unreachable")
                return []
            except Exception as e:
                logging.error(f"Error parsing {file_path}: {e}")
                return []