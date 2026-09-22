#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
COMPOSE="docker compose -f docker-compose.dev.yml"
WORK=/tmp/unividown-phase3-complete
LOG_FILE="$ROOT/phase3-complete-compose.log"
cleanup(){ $COMPOSE logs --no-color worker web redis >"$LOG_FILE" 2>&1 || true; $COMPOSE down -v >/dev/null 2>&1 || true; rm -rf "$WORK"; }
trap cleanup EXIT
mkdir -p "$WORK"

echo "[1/5] Run full security, lifecycle, UI, validation, and storage baseline"
bash scripts/validate_phase3f_local.sh

echo "[2/5] Start clean stack and generate deterministic fixtures"
$COMPOSE up -d --build --wait
BASELINE_UPLOADS="$($COMPOSE exec -T worker sh -lc 'find /app/data/uploads -maxdepth 1 -type f -printf "%f\n" | sort')"
ffmpeg -loglevel error -f lavfi -i testsrc=size=640x360:rate=24:duration=4 -f lavfi -i sine=frequency=440:duration=4 -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest -y "$WORK/video.mp4"
ffmpeg -loglevel error -f lavfi -i color=c=red:s=640x480 -frames:v 1 -y "$WORK/image.png"
printf '1\n00:00:00,000 --> 00:00:02,000\nUnividown subtitle fixture\n' >"$WORK/subtitle.srt"
ffmpeg -loglevel error -i "$WORK/video.mp4" -f srt -i "$WORK/subtitle.srt" -map 0:v -map 0:a -map 1:0 -c:v copy -c:a copy -c:s srt -y "$WORK/subtitled.mkv"

queue_and_verify(){
  local name="$1" endpoint="$2" file="$3" extension="$4"; shift 4
  echo "Testing $name"
  local response job_id status_url status result_url
  response="$(curl -fsS -F "file=@$file" "$@" "http://localhost:8000$endpoint")"
  job_id="$(printf '%s' "$response" | python3 -c 'import json,sys; print(json.load(sys.stdin)["job_id"])')"
  status_url="$(printf '%s' "$response" | python3 -c 'import json,sys; print(json.load(sys.stdin)["status_url"])')"
  status=pending
  for attempt in $(seq 1 90); do
    curl -fsS "http://localhost:8000$status_url" -o "$WORK/status.json"
    status="$(python3 -c 'import json; print(json.load(open("/tmp/unividown-phase3-complete/status.json"))["status"])')"
    case "$status" in completed|failed) break;; esac
    sleep 2
  done
  [[ "$status" == completed ]] || { cat "$WORK/status.json"; echo "ERROR: $name ended with $status"; exit 1; }
  ! grep -Eq '"input_files"|"output_files"|/app/data' "$WORK/status.json" || { echo "ERROR: $name leaked filesystem paths"; exit 1; }
  result_url="$(python3 -c 'import json; print(json.load(open("/tmp/unividown-phase3-complete/status.json"))["results"][0]["download_url"])')"
  curl -fSL "http://localhost:8000$result_url" -o "$WORK/result-$job_id.$extension"
  test -s "$WORK/result-$job_id.$extension"
}

echo "[3/5] Validate every core media tool end-to-end"
queue_and_verify video-convert /api/tools/convert "$WORK/video.mp4" webm -F format=webm
queue_and_verify video-trim /api/tools/trim "$WORK/video.mp4" mp4 -F start=0.5 -F end=2.5
queue_and_verify audio-convert /api/tools/audio/convert "$WORK/video.mp4" mp3 -F format=mp3
queue_and_verify image-optimize /api/tools/image/optimize "$WORK/image.png" png -F quality=80 -F max_width=320
queue_and_verify gif-maker /api/tools/gif/make "$WORK/video.mp4" gif -F start=0 -F duration=2 -F fps=10 -F scale=320
queue_and_verify subtitle-extract /api/tools/subtitle/extract "$WORK/subtitled.mkv" vtt

echo "[4/5] Validate optional transcription capability"
CODE="$(curl -sS -o "$WORK/transcription.json" -w '%{http_code}' -F "file=@$WORK/video.mp4" -F model=tiny http://localhost:8000/api/tools/transcribe)"
[[ "$CODE" == 503 ]] || { echo "ERROR: core transcription expected HTTP 503, got $CODE"; cat "$WORK/transcription.json"; exit 1; }
python3 -c 'import json; data=json.load(open("/tmp/unividown-phase3-complete/transcription.json")); assert "capability unavailable" in data["detail"].lower()'

CURRENT_UPLOADS=""
for attempt in $(seq 1 15); do
  CURRENT_UPLOADS="$($COMPOSE exec -T worker sh -lc 'find /app/data/uploads -maxdepth 1 -type f -printf "%f\n" | sort')"
  [[ "$CURRENT_UPLOADS" == "$BASELINE_UPLOADS" ]] && break
  sleep 1
done
if [[ "$CURRENT_UPLOADS" != "$BASELINE_UPLOADS" ]]; then
  printf 'ERROR: terminal processing did not restore the upload baseline\nBaseline uploads:\n%s\nCurrent uploads:\n%s\n' "$BASELINE_UPLOADS" "$CURRENT_UPLOADS"
  exit 1
fi
! $COMPOSE exec -T worker sh -lc 'find /app/data/uploads -maxdepth 1 -type f -name "*.part" -print -quit' | grep -q . || { echo "ERROR: partial upload files remain"; exit 1; }

echo "[5/5] PASS"
echo "PASS: Complete Phase 3 media fixture gate completed"
