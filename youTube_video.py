import re
import re
import streamlit as st
import yt_dlp as youtube_dl
import os
import time

# Function to download YouTube video with retry logic
def download_video(url, output_path, retries=3):
    for attempt in range(retries):
        try:
            # Attempt to download the video
            video_title = None
            progress_bar = st.progress(0)
            progress_text = st.empty()
            final_path = None

            def progress_hook(d):
                nonlocal video_title, final_path
                if d['status'] == 'downloading':
                    if not video_title:
                        video_title = d.get('info_dict', {}).get('title', 'Unknown title')
                    percent_str = re.sub(r'\x1b\[.*?m', '', d['_percent_str']).strip()
                    percent = float(percent_str.strip('%'))
                    progress_bar.progress(int(percent))
                    progress_text.text(f"🎥 Downloading '{video_title}': {percent:.2f}%")
                elif d['status'] == 'finished':
                    final_path = d['info_dict']['_filename']
                    progress_text.text(f"✅ Download completed for '{video_title}'")
                    progress_bar.progress(100)

            ydl_opts = {
                'progress_hooks': [progress_hook],
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            if final_path:
                st.success(f"🎉 Downloaded video saved to: {final_path}")
            break  # Exit the loop if successful

        except BrokenPipeError:
            if attempt < retries - 1:
                st.warning(f"⚠️ Download interrupted (Broken pipe error). Retrying... ({attempt + 1}/{retries})")
                time.sleep(1)  # Wait before retrying
            else:
                st.error("❌ Download failed after multiple attempts: Broken pipe error.")
        except Exception as e:
            st.error(f"❌ An error occurred: {e}")
            break

# Your Streamlit app code continues...

# Initialize session state for URL and output directory
if "video_url" not in st.session_state:
    st.session_state.video_url = ""
if "output_dir" not in st.session_state:
    st.session_state.output_dir = ""

# Streamlit UI
st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>YouTube Video Downloader</h1>", unsafe_allow_html=True)

# Input for YouTube URL
st.session_state.video_url = st.text_input("Enter YouTube video URL", st.session_state.video_url)

# Input for output directory
st.session_state.output_dir = st.text_input("Enter output directory", st.session_state.output_dir)

# Button to start download
if st.button("Download", key="download"):
    if st.session_state.video_url:
        output_dir = st.session_state.output_dir
        if not output_dir:  # Check if the output directory is empty
            st.warning("⚠️ Output directory is empty. Using Desktop as default directory.")
            output_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        elif not os.path.exists(output_dir):  # Check if the directory exists
            st.warning(f"⚠️ The directory '{output_dir}' does not exist. Using Desktop as default directory.")
            output_dir = os.path.join(os.path.expanduser("~"), "Desktop")

        st.write("🚀 Starting download...")
        download_video(st.session_state.video_url, output_dir)
    else:
        st.error("❌ Please enter a valid YouTube URL.")

# Button to reset progress, clear path directory, and clear inputs
if st.button("New Download", key="new_download"):
    # Reset progress bar and clear previous output
    progress_bar = st.progress(0)
    progress_text = st.empty()

    # Clear input fields by resetting session state variables
    st.session_state.video_url = ""
    st.session_state.output_dir = ""

    st.experimental_rerun()  # Rerun the app to update the UI

# Sidebar styling and content
st.sidebar.markdown("<h2 style='color: #FF4B4B;'>About</h2>", unsafe_allow_html=True)
st.sidebar.write("This app allows you to download videos from YouTube by simply providing the video URL.")
st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='color: #FF4B4B;'>Developer</h3>", unsafe_allow_html=True)
st.sidebar.write("**M. Shahjhan Gondal**")
st.sidebar.write("**Email:** shahjhangondal99@gmail.com")
