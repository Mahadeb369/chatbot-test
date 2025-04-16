import os
import re
import yt_dlp

# Function to sanitize filenames
def sanitize_filename(filename):
    """Sanitize filename to remove or replace invalid characters."""
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)  # Remove invalid characters
    return filename[:255]  # Limit length to 255 characters

def get_video(url):
    try:
        # Ensure the 'video' folder exists
        video_folder = 'videos'
        if not os.path.exists(video_folder):
            os.makedirs(video_folder)
        
        # Set up yt_dlp options
        ydl_opts = {
            'format': 'best',  # Download the best quality video
            'outtmpl': '%(title)s.%(ext)s',  # Temporary title template
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract metadata without downloading to get title and uploader
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', 'unknown_title')
            video_author = info_dict.get('uploader', 'unknown_uploader')
            video_duration = info_dict.get('duration_string')

            # Sanitize the video title for the filename
            sanitized_title = sanitize_filename(video_title)
            ydl_opts['outtmpl'] = os.path.join(video_folder, f"{sanitized_title}.%(ext)s")

            # Re-run yt_dlp with updated outtmpl to download the video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            print(f"Video downloaded: {sanitized_title}.mp4")
            print(f"Video Title: {video_title}")
            print(f"Video Author: {video_author}")
            print(f"Video Duration: {video_duration}")

            # Return the path and metadata
            return os.path.join(video_folder, f"{sanitized_title}.mp4"), video_title, video_author, video_duration

    except yt_dlp.utils.DownloadError as e:
        print(f"Download error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return None, None, None, None