import streamlit as st
from moviepy import *
import re
import os

st.set_page_config(page_title="DLS Meme Generator", layout="centered")
st.title("⚽ DLS Meme Generator - Free")
st.write("Upload DLS clip + memes + sound. Type prompt. Get video.")

video_file = st.file_uploader("1. Upload DLS Video", type=["mp4"])
meme_files = st.file_uploader("2. Upload Meme PNGs - transparent background", type=["png"], accept_multiple_files=True)
sound_file = st.file_uploader("3. Upload Sound MP3", type=["mp3"])

prompt = st.text_area("4. Write your prompt",
"value: put meme0 on player from 2s to 5s. put meme1 at 8s. play sound0 at 7s")

if st.button("🔥 Generate Video") and video_file and meme_files:
    with st.spinner("Rendering... 1-3 minutes"):
        video_path = "temp_video.mp4"
        with open(video_path, "wb") as f: f.write(video_file.read())
        clip = VideoFileClip(video_path)

        layers = [clip]
        for i, m in enumerate(meme_files):
            path = f"meme{i}.png"
            with open(path, "wb") as f: f.write(m.read())
            meme_clip = ImageClip(path).set_duration(2)

            # check "from Xs to Ys"
            times = re.findall(f"meme{i}.*?from (\\d+)s to (\\d+)s", prompt)
            if times:
                start, end = map(int, times[0])
                meme_clip = meme_clip.set_start(start).set_duration(end-start)
                layers.append(meme_clip.set_position("center"))

            # check "at Xs"
            single = re.findall(f"meme{i}.*?at (\\d+)s", prompt)
            if single:
                start = int(single[0])
                meme_clip = meme_clip.set_start(start)
                layers.append(meme_clip.set_position("center"))

        final_clip = CompositeVideoClip(layers, size=clip.size)

        if sound_file:
            sound_path = "sound.mp3"
            with open(sound_path, "wb") as f: f.write(sound_file.read())
            sound = AudioFileClip(sound_path).set_start(0)
            final_clip = final_clip.set_audio(CompositeAudioClip([clip.audio, sound]))

        output_path = "output.mp4"
        final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24, logger=None)

        st.success("✅ Done!")
        st.video(output_path)
        with open(output_path, "rb") as f:
            st.download_button("Download Video", f, file_name="dls_meme.mp4")
