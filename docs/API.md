# Unividown API Documentation

Base URL: `https://your-domain.com/api`

## Authentication

Currently no authentication required for personal use deployments.

## Rate Limiting

- General API: 10 requests/second
- Download endpoints: 2 requests/second
- Tools endpoints: 5 requests/second

## Endpoints

### Downloads

#### Create Download Job
```http
POST /api/downloads
Content-Type: application/json

{
  "url": "https://youtube.com/watch?v=...",
  "quality": "best",
  "priority": 0
}
```

**Response:**
```json
{
  "job_id": 1,
  "status": "queued",
  "job": { ... }
}
```

#### Batch Download
```http
POST /api/downloads/batch
Content-Type: application/json

{
  "urls": [
    "https://youtube.com/watch?v=...",
    "https://youtube.com/watch?v=..."
  ],
  "quality": "best"
}
```

#### List Downloads
```http
GET /api/downloads?status=completed&limit=50&offset=0
```

#### Get Download Status
```http
GET /api/downloads/{job_id}
```

#### Cancel/Delete Download
```http
DELETE /api/downloads/{job_id}
```

#### Retry Failed Download
```http
POST /api/downloads/{job_id}/retry
```

#### Extract URL Info (Playlist Detection)
```http
GET /api/downloads/info?url=https://youtube.com/playlist?list=...
POST /api/downloads/info
Content-Type: application/json
{ "url": "..." }
```

---

### Tools

#### Convert Media
```http
POST /api/tools/convert
Content-Type: multipart/form-data

file: <video_file>
format: mp4|mkv|webm|avi|mov
```

#### Trim Video
```http
POST /api/tools/trim
Content-Type: multipart/form-data

file: <video_file>
start: 0.0
end: 10.0
```

#### Compress Video
```http
POST /api/tools/compress
Content-Type: multipart/form-data

file: <video_file>
bitrate: 1000k
```

#### Merge Videos
```http
POST /api/tools/merge
Content-Type: multipart/form-data

files: <video_file_1>
files: <video_file_2>
```

#### Audio Convert (Extract/Convert Audio)
```http
POST /api/tools/audio/convert
Content-Type: multipart/form-data

file: <audio_or_video_file>
format: mp3|wav|flac|aac|ogg
```

#### Image Optimize
```http
POST /api/tools/image/optimize
Content-Type: multipart/form-data

file: <image_file>
quality: 85
max_width: 1920
```

#### Subtitle Extract
```http
POST /api/tools/subtitle/extract
Content-Type: multipart/form-data

file: <video_file>
```

#### GIF Maker
```http
POST /api/tools/gif/make
Content-Type: multipart/form-data

file: <video_file>
start: 0.0
duration: 5.0
fps: 15
scale: 480
```

#### AI Transcription
```http
POST /api/tools/transcribe
Content-Type: multipart/form-data

file: <audio_or_video_file>
model: tiny|base|small|medium|large
```

#### List Processing Jobs
```http
GET /api/tools/jobs?status=pending
```

#### Get Processing Job
```http
GET /api/tools/jobs/{job_id}
```

---

### Monitoring

#### Health Check
```http
GET /api/health
GET /api/status
```

#### Prometheus Metrics
```http
GET /metrics
```

---

### WebSocket (Socket.IO)

Connect to worker for real-time updates:

```javascript
import { io } from 'socket.io-client';

const socket = io('https://your-domain.com', {
  path: '/socket.io',
  transports: ['websocket', 'polling']
});

// Join job room
socket.emit('join_download', jobId);

// Listen for events
socket.on('download:progress', (data) => {
  console.log(`Job ${data.jobId}: ${data.progress}% (${data.speed}, ETA: ${data.eta})`);
});

socket.on('download:status', (data) => {
  console.log(`Job ${data.jobId} status: ${data.status}`);
});

socket.on('download:completed', (data) => {
  console.log(`Job ${data.jobId} completed: ${data.title}`);
});

socket.on('download:error', (data) => {
  console.error(`Job ${data.jobId} error: ${data.error}`);
});

// Leave room
socket.emit('leave_download', jobId);
```

---

### Error Responses

All endpoints may return:

```json
{
  "detail": "Error message"
}
```

Status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 404: Not Found
- 429: Rate Limited
- 500: Internal Server Error