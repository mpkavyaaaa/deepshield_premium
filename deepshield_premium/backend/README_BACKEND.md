# Backend (FastAPI) - DeepFake Premium Demo

## New endpoints
- POST /predict-image -> image upload (same as before)
- POST /predict-video -> video upload. Accepts form file `file`. Optional form field `sample_rate` (int, default 5) to downsample frames.

## Notes
- The server uses OpenCV (headless) to read videos and samples frames to produce aggregated score.
- For production, ensure ffmpeg/opencv availability and tune `sample_rate` to balance speed vs accuracy.
