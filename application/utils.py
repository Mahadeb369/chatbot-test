import regex as re
from typing import Dict, List
import time
import os
from urllib.error import HTTPError
from pytubefix import YouTube
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
from moviepy.editor import VideoFileClip
from flask import current_app as app

# Extract youtube video id from url
def extract_youtube_id(url):
    pattern = r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    
    match = re.search(pattern, url)
    
    if match:
        return match.group(1)
    return None

def get_transcript(video_id, max_retries=3):
    transcript = None
    language = None

    for attempt in range(max_retries):
        try:
            # Fetch available transcripts
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            for transcript in transcript_list:
                fetched_transcript = transcript.fetch()
                language = transcript.language

                # Format the transcript for further use
                formatted_transcript = []
                for i, entry in enumerate(fetched_transcript):
                    start_time = entry['start']
                    text = entry['text']

                    # If it's not the last entry, set end time as the start time of the next entry
                    if i < len(fetched_transcript) - 1:
                        end_time = fetched_transcript[i + 1]['start']
                    else:
                        end_time = start_time + entry.get('duration', 0)

                    formatted_entry = {
                        'start': start_time,
                        'end': end_time,
                        'text': text
                    }
                    formatted_transcript.append(formatted_entry)

                return formatted_transcript, language  

        except (NoTranscriptFound, TranscriptsDisabled) as e:
            print(f"Attempt {attempt + 1}: No transcript found for video ID {video_id}, retrying...")
            time.sleep(1)  # Optional: Small delay between retries

    # If after retries no transcript was found
    print(f"No transcript found for video ID {video_id} after {max_retries} attempts.")
    return None, None


# Download video from youtube
def get_video(url):
    yt = YouTube(url)
    ys = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    ys.download('videos/')
    return 'videos/' + ys.default_filename, yt.title, yt.author

# Compile reels from the video
def compile_reels(title, video_path, highlights):
    reel_timestamps = []
    reels_output_paths = []
    reels_output_filenames = []
    reel_output_titles = []
    reel_output_captions = []
    reel_output_escores =[]
    # Choose highlights longer than 15 seconds
    for reel in highlights:
        if float(reel['End Time']) - float(reel['Start Time']) > 15:
            reel_timestamps.append((float(reel['Start Time']), float(reel['End Time'])))
            reel_output_titles.append(reel['Title'])
            reel_output_captions.append(reel['Caption'])
            reel_output_escores.append(reel['Engagement Score'])

    for i, (start, end) in enumerate(reel_timestamps):
        if end > VideoFileClip(video_path).duration:
            end = VideoFileClip(video_path).duration
        reel = VideoFileClip(video_path).subclip(start, end).fadein(0.5).fadeout(0.5).audio_fadein(0.1).audio_fadeout(0.1)
        reel_output_filename = title + f'_reel{i}.mp4'
        reel.write_videofile(app.config['OUTPUT_REELS_FOLDER'] + reel_output_filename, codec='libx264', threads=8, fps=24)
        reels_output_paths.append(app.config['OUTPUT_REELS_FOLDER'] + reel_output_filename)
        reels_output_filenames.append(reel_output_filename)
        reel.close()
    
    return reels_output_paths, reels_output_filenames, reel_output_titles, reel_output_captions, reel_output_escores

def format_transcript_to_paragraph(transcript: List[Dict]) -> str:
    """
    Convert a list of transcript segments into a single paragraph string.

    Args:
        transcript (List[Dict]): A list of dictionaries with 'start', 'end', and 'text' keys.

    Returns:
        str: A single string of text formatted as a paragraph.
    """
    # Join all text segments into a single string with spaces
    paragraph = ' '.join([segment['text'].replace('\n', ' ') for segment in transcript])
    # Clean up extra spaces caused by line breaks
    paragraph = re.sub(r'\s+', ' ', paragraph).strip()
    return paragraph