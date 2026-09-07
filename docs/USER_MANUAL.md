# Unividown User Manual

## Overview

Unividown is a self-hosted media downloader and processing toolkit powered by yt-dlp and FFmpeg. It provides a web interface for downloading, converting, and processing media files.

## Getting Started

### Access the Web Interface

1. Open your browser and navigate to `https://your-domain.com`
2. You'll see the dashboard with navigation sidebar

### Navigation

- **Download** - Download media from URLs (YouTube, TikTok, X, Instagram, etc.)
- **History** - View all past download jobs
- **Settings** - Configure application settings
- **Tools** - Media processing utilities

---

## Download Media

### Single Video/Audio Download

1. Go to **Download** page
2. Paste a media URL in the input field
3. Select quality/format:
   - **Best Available** - Highest quality video + audio
   - **1080p/720p/480p** - Specific resolution
   - **Audio Only (MP3)** - Extract audio as MP3
4. Click **Start Download**

### Playlist Download

1. Paste a playlist URL (e.g., YouTube playlist)
2. The app automatically detects playlists
3. A **Playlist Selector** appears showing all videos
4. Select individual videos or click **Select All**
5. Click **Download Selected** to queue multiple downloads

### Monitor Progress

- Real-time progress bar with speed and ETA
- WebSocket updates (no page refresh needed)
- Status: Queued → Downloading → Completed/Failed

### Retry Failed Downloads

1. Go to **History** or **Download Queue**
2. Find failed job (red status badge)
3. Click **Retry** button (circular arrow icon)
3. Job re-queues with exponential backoff retry logic

---

## Media Tools

### Video Converter

Convert video containers/formats:
1. Go to **Tools → Video Converter**
2. Upload video file (drag & drop or click)
3. Select output format: MP4, MKV, WebM, AVI, MOV
4. Click **Convert**

### Video Trimmer

Cut video segments:
1. Go to **Tools → Video Trimmer**
2. Upload video file
3. Set start time and end time (in seconds)
4. Click **Trim**

### Audio Converter

Extract/convert audio from video or audio files:
1. Go to **Tools → Audio Converter**
2. Upload file (audio or video)
3. Select output format: MP3, WAV, FLAC, AAC, OGG
4. Click **Extract / Convert**

### Image Optimizer

Optimize images for web:
1. Go to **Tools → Image Optimizer**
2. Upload image (JPG, PNG, WebP, GIF)
3. Adjust quality (10-100) and max width
4. Click **Optimize Image**

### Subtitle Extractor

Extract embedded subtitles:
1. Go to **Tools → Subtitle Extractor**
2. Upload video with subtitles (MP4, MKV, WebM)
3. Click **Extract Subtitles**
4. Output: WebVTT (.vtt) format

### GIF Maker

Create animated GIFs from video:
1. Go to **Tools → GIF Maker**
2. Upload video file
3. Set start time, duration (max 30s), FPS (10-30), width (320-720)
4. Click **Create GIF**

### AI Transcription (Whisper)

Transcribe audio/video to text:
1. Go to **Tools → Transcribe**
2. Upload audio or video file
3. Select Whisper model:
   - **Tiny** (~39 MB) - Fastest, English only
   - **Base** (~74 MB) - Fast, multilingual
   - **Small** (~244 MB) - Better accuracy
   - **Medium** (~769 MB) - Good accuracy
   - **Large** (~1550 MB) - Best accuracy
4. Click **Transcribe to Text**
5. Output: .txt transcript + .json segments with timestamps

---

## History

View all download and processing jobs:
- Filter by status (All, Pending, Processing, Completed, Failed)
- Sort by date, status, or progress
- Click job for details and file access
- Retry failed jobs with one click

---

## Settings

Configure application:
- Default download quality
- Download directory
- FFmpeg options
- Theme (Light/Dark/System)

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + K` | Focus URL input |
| `Ctrl/Cmd + Enter` | Start download |
| `Ctrl/Cmd + D` | Go to Download page |
| `Ctrl/Cmd + H` | Go to History page |
| `Ctrl/Cmd + T` | Go to Tools page |
| `Escape` | Close dialogs/clear selection |

---

## Tips & Best Practices

1. **Use Playlist Selector** for bulk downloads - saves time
2. **Tiny Whisper model** for quick English transcriptions
3. **15 FPS / 480px** for GIFs - good balance of size/quality
4. **Monitor queue** - large files take time, especially with larger Whisper models
5. **Retry failed downloads** - network issues often resolve on retry

---

## Disclaimer

This tool is for **personal use only**. Users are responsible for:
- Complying with platform Terms of Service
- Respecting copyright and intellectual property
- Not using for illegal activities

The developer is not liable for misuse.