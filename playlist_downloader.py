import os
import yt_dlp
import re
import streamlit as st
from time import sleep


def sanitize_filename(title):
    """Remove invalid characters from filename"""
    return re.sub(r'[<>:"/\\|?*]', '', title)


def download_playlist(playlist_url, progress_bar, status_text):
    # Validate URL format
    if not playlist_url.startswith('https://www.youtube.com/playlist?list='):
        st.error("Error: Invalid playlist URL format. Please use a URL like: https://www.youtube.com/playlist?list=PLAYLIST_ID")
        return

    with st.spinner('Fetching playlist information...'):
        try:
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'best[ext=mp4]',  # Best quality MP4
                'outtmpl': '%(playlist_title)s/%(title)s.%(ext)s',  # Output template
                'ignoreerrors': True,  # Skip unavailable videos
                'no_warnings': True,
                'quiet': True,
                'extract_flat': True,  # Don't download, just get info first
            }

            # First, get playlist info
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                playlist_info = ydl.extract_info(playlist_url, download=False)
                
                if not playlist_info.get('entries'):
                    st.error("Error: No videos found in playlist or playlist is private/unavailable")
                    return

                playlist_title = sanitize_filename(playlist_info.get('title', 'YouTube_Playlist'))
                videos = playlist_info['entries']
                
                st.info(f"Playlist: {playlist_title}")
                st.info(f"Total videos: {len(videos)}")

                # Configure for actual download
                progress_count = 0
                
                def progress_hook(d):
                    nonlocal progress_count
                    if d['status'] == 'finished':
                        progress_count += 1
                        progress = progress_count / len(videos)
                        progress_bar.progress(progress)
                        status_text.markdown(f"""
                            📥 **Downloading: {progress_count}/{len(videos)} videos**  
                            ✅ Progress: {progress:.1%}
                        """)

                ydl_opts.update({
                    'extract_flat': False,
                    'progress_hooks': [progress_hook],
                })

                # Before starting download, update spinner message
                with st.spinner('Downloading videos...'):
                    # Download videos
                    ydl.download([playlist_url])

            st.success(f"Download completed! Videos saved in: {playlist_title}/")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")


def main():
    st.title("YouTube Playlist Downloader")
    st.write("Enter a YouTube playlist URL to download all videos.")

    # Create input field for playlist URL
    playlist_url = st.text_input("Playlist URL", placeholder="https://www.youtube.com/playlist?list=...")

    if st.button("Download Playlist"):
        if playlist_url:
            progress_bar = st.progress(0)
            status_text = st.empty()
            download_playlist(playlist_url, progress_bar, status_text)
        else:
            st.warning("Please enter a playlist URL")
    
    # Add Buy Me a Coffee button in a small container
    with st.container():
        st.markdown("""
            <div style='text-align: center; padding: 10px;'>
                <a href='https://www.buymeacoffee.com/YourUsername' target='_blank'>
                    <img src='https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png' 
                         alt='Buy Me A Coffee' 
                         style='height: 40px; width: auto;'>
                </a>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
