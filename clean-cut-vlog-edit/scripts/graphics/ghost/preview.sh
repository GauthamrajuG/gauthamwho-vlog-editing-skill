#!/usr/bin/env bash
# Preview of the walk-in scare: v6 35.0-39.5 s with the ghost window (v6 frames 2169..2270)
# swapped in and its sound mixed under his voice. Each part is read as its own input
# (no split+trim: that buffers frames in RAM on this PC).
set -e
cd "$(dirname "$0")"
V6="D:/Claude/Video/Reel 29/Final video/GauthamWho_Reel29_AirFryerWorld_v6_SDR.mp4"
# part A: frames 2100..2168 (69); window: 102 frames; part C: frames 2271..2369 (99)
ffmpeg -hide_banner -loglevel error -y -threads 2 \
  -ss 34.992 -i "$V6" -i anim/ghost_window.mp4 -ss 37.842 -i "$V6" -ss 34.992 -i "$V6" -i anim/ghost_sfx.wav \
  -filter_threads 1 -filter_complex "\
[0:v]trim=end_frame=69,setpts=PTS-STARTPTS[a];\
[1:v]setpts=PTS-STARTPTS,format=yuv420p[g];\
[2:v]trim=end_frame=99,setpts=PTS-STARTPTS[c];\
[a][g][c]concat=n=3:v=1:a=0[v];\
[3:a]atrim=duration=4.5,asetpts=PTS-STARTPTS,aresample=48000[voice];\
[4:a]adelay=1150|1150[s];\
[voice][s]amix=inputs=2:normalize=0:duration=first[aout]" \
  -map "[v]" -map "[aout]" -c:v libx264 -preset medium -crf 15 -threads 2 -pix_fmt yuv420p \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv -r 60 \
  -c:a aac -b:a 256k -movflags +faststart anim/ghost_preview.mp4
ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 anim/ghost_preview.mp4
