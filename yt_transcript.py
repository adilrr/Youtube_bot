
import time
from typing import Optional
from urllib.parse import parse_qs, urlparse

import browser_cookie3
from youtube_transcript_api import YouTubeTranscriptApi

ALLOWED_SCHEMES = {"http", "https"}
ALLOWED_NETLOCS = {
    "youtu.be",
    "m.youtube.com",
    "youtube.com",
    "www.youtube.com",
    "www.youtube-nocookie.com",
    "vid.plus",
}

def parse_video_id(url: str)-> Optional[str]:
    """Parse a YouTube URL and return the video ID if valid, otherwise None."""
    parsed_url = urlparse(url)

    if parsed_url.scheme not in ALLOWED_SCHEMES:
        return None

    if parsed_url.netloc not in ALLOWED_NETLOCS:
        return None

    path = parsed_url.path

    if path.endswith("/watch"):
        query = parsed_url.query
        parsed_query = parse_qs(query)
        if "v" in parsed_query:
            ids = parsed_query["v"]
            video_id = ids if isinstance(ids, str) else ids[0]
        else:
            return None
    else:
        path = parsed_url.path.lstrip("/")
        video_id = path.split("/")[-1]

    if len(video_id) != 11:  # Video IDs are 11 characters long
        return None

    return video_id



def get_youtube_cookies(filename='youtube_cookies.txt'):
    try:
        cookies = browser_cookie3.chrome(domain_name='.youtube.com')
        with open(filename, 'w') as f:
            f.write("# Netscape HTTP Cookie File\n")  # Important header
            for cookie in cookies:
                secure = "TRUE" if cookie.secure else "FALSE"
                http_only = "TRUE" if cookie.has_nonstandard_attr('HttpOnly') else "FALSE"
                expires = int(cookie.expires) if cookie.expires else int(time.time() + 3600*24*365)
                f.write(f"{cookie.domain}\t{'TRUE' if cookie.domain.startswith('.') else 'FALSE'}\t{cookie.path}\t"
                        f"{secure}\t{expires}\t{cookie.name}\t{cookie.value}\n")
        return filename
    except Exception as e:
        print(f"Error getting YouTube cookies: {str(e)}")
        return None


def get_transcript_by_video_id(video_id):
    cookie_file = get_youtube_cookies()
    transcript_chunks = YouTubeTranscriptApi.get_transcript(
        video_id=video_id, 
        cookies=cookie_file,
        languages=("en", )
    )
    transcript = " ".join(
        map(
            lambda transcript_piece: transcript_piece["text"].strip(" "),
            transcript_chunks,
        )
    )
    return transcript


def get_transcript(url:str):
    video_id = parse_video_id(url)
    if not video_id:
        return None
        # raise Exception("Invalid URL or video ID")
    try:
        return get_transcript_by_video_id(video_id)
    except Exception as e:
        return None
        # raise Exception(f"Failed to load transcript from youtube")


if __name__ == "__main__":
    url = input("Enter the YouTube video URL: ")
    transcript = get_transcript(url)
    print(transcript)
    