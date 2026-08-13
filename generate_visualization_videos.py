import json
import os
import subprocess
from pathlib import Path
import cv2
import numpy as np
from mediapipe.framework.formats import landmark_pb2
from mediapipe.python.solutions import drawing_styles, drawing_utils, pose


def generate_video(path):
    path = str(path) + "/"
    width = 750
    height = 750
    preview = False

    # Check for core files
    phone_file = os.path.join(path, "phone.json")
    watch_file = os.path.join(path, "watch.json")

    # Support pose_landmarks.json or pose.json
    pose_file = os.path.join(path, "pose_landmarks.json")
    if not os.path.exists(pose_file):
        pose_file = os.path.join(path, "pose.json")

    # Support meta_data.json or metadata.json
    meta_file = os.path.join(path, "meta_data.json")
    if not os.path.exists(meta_file):
        meta_file = os.path.join(path, "metadata.json")

    audio_file = os.path.join(path, "audio.m4a")

    if not all(
        os.path.exists(p) for p in [phone_file, watch_file, pose_file, meta_file]
    ):
        print(f"[Skipped] Missing required JSON files in {path}")
        return

    with open(phone_file, "r", encoding="utf-8") as f:
        phone_data = json.load(f)
    with open(watch_file, "r", encoding="utf-8") as f:
        watch_data = json.load(f)
    with open(pose_file, "r", encoding="utf-8") as f:
        pose_data = json.load(f)
    with open(meta_file, "r", encoding="utf-8") as f:
        meta_data = json.load(f)

    def reencode_video(video_path):
        try:
            command = [
                "ffmpeg",
                "-y",
                "-i",
                video_path + "old_video.mp4",
                "-vcodec",
                "libx264",
                "-crf",
                "23",
                video_path + "video_without_audio.mp4",
            ]
            subprocess.run(
                command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            os.remove(video_path + "old_video.mp4")
        except Exception as e:
            print(f"Failed to re-encode video: {e}")

    def draw_landmarks_on_image(detection_result):
        # Support dict with 'landmarks' or direct landmark list
        pose_landmarks_list = (
            detection_result["landmarks"]
            if isinstance(detection_result, dict) and "landmarks" in detection_result
            else detection_result
        )

        image = np.zeros((height, int(width / 2), 3), dtype=np.uint8)
        pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        pose_landmarks_proto.landmark.extend(
            [
                landmark_pb2.NormalizedLandmark(x=l["x"], y=l["y"], z=l["z"])
                for l in pose_landmarks_list
            ]
        )
        drawing_utils.draw_landmarks(
            image,
            pose_landmarks_proto,
            pose.POSE_CONNECTIONS,
            drawing_styles.get_default_pose_landmarks_style(),
        )
        return image

    def find_closest_entry(data, timestamp_a):
        return min(data, key=lambda x: abs(x["timestamp"] - timestamp_a))

    def draw_data_on_image(img, timestamp):
        phone_frame_data = find_closest_entry(phone_data, timestamp)
        watch_frame_data = find_closest_entry(watch_data, timestamp)

        # Support 'gait_pattern' (English) or 'gangtyp' (German)
        label = meta_data.get("gait_pattern", meta_data.get("gangtyp", "Unknown"))

        lines = [
            "Phone Data:",
            f"Accel:  x={int(phone_frame_data['accel']['x'])}  y={int(phone_frame_data['accel']['y'])}  z={int(phone_frame_data['accel']['z'])}",
            f"Gyro:   x={int(phone_frame_data['gyro']['x'])}  y={int(phone_frame_data['gyro']['y'])}  z={int(phone_frame_data['gyro']['z'])}",
            f"Orient: yaw={int(phone_frame_data['orientation']['yaw'])} pitch={int(phone_frame_data['orientation']['pitch'])} roll={int(phone_frame_data['orientation']['roll'])}",
            "",
            "Watch Data:",
            f"Accel:  x={int(watch_frame_data['accel']['x'])}  y={int(watch_frame_data['accel']['y'])}  z={int(watch_frame_data['accel']['z'])}",
            f"Gyro:   x={int(watch_frame_data['gyro']['x'])}  y={int(watch_frame_data['gyro']['y'])}  z={int(watch_frame_data['gyro']['z'])}",
            "",
            "Meta Data:",
            f"Label: {label}",
            f"ID: {meta_data.get('id', 'N/A')}",
            f"Pose: {entrys_per_second(pose_data)}",
            f"Phone: {entrys_per_second(phone_data)}",
            f"Watch:{entrys_per_second(watch_data)}",
        ]

        for i, text in enumerate(lines):
            cv2.putText(
                img,
                text,
                (int(width / 2), 100 + i * 40),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )
        return img

    def entrys_per_second(data):
        duration = (data[-1]["timestamp"] - data[0]["timestamp"]) / 1000
        eps = len(data) / duration if duration > 0 else 25.0
        wait_ms = int((1 / eps) * 1000) if eps > 0 else 40
        return [round(duration, 2), round(eps, 2), wait_ms]

    def add_audio_to_video(path):
        if os.path.exists(audio_file):
            try:
                command = [
                    "ffmpeg",
                    "-y",
                    "-i",
                    path + "video_without_audio.mp4",
                    "-i",
                    audio_file,
                    "-filter:a",
                    "volume=5.0",
                    "-c:v",
                    "copy",
                    "-c:a",
                    "aac",
                    "-shortest",
                    path + "video.mp4",
                ]
                subprocess.run(
                    command,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                os.remove(path + "video_without_audio.mp4")
                print(f"  [Success] Video generated with audio in {path}")
            except Exception as e:
                print(f"  [Warning] Failed merging audio: {e}")
                os.rename(path + "video_without_audio.mp4", path + "video.mp4")
        else:
            # If audio is missing (removed for privacy), keep video without audio as video.mp4
            os.rename(path + "video_without_audio.mp4", path + "video.mp4")
            print(f"  [Success] Video generated (no audio) in {path}")

    frame_info = entrys_per_second(pose_data)

    videoWriter = cv2.VideoWriter(
        path + "old_video.mp4",
        cv2.VideoWriter_fourcc(*"mp4v"),
        frame_info[1],
        (width, height),
    )

    for i in range(len(pose_data)):
        pose_image_plus_data = np.zeros((height, width, 3), dtype=np.uint8)
        pose_image_plus_data[:, : int(width / 2), :] = draw_landmarks_on_image(
            pose_data[i]
        )

        timestamp = (
            pose_data[i]["timestamp"]
            if isinstance(pose_data[i], dict) and "timestamp" in pose_data[i]
            else pose_data[i][0].get("timestamp", 0)
        )

        pose_image_plus_data = draw_data_on_image(pose_image_plus_data, timestamp)

        if preview:
            cv2.imshow("Pose Image", pose_image_plus_data)
            cv2.waitKey(frame_info[2])

        videoWriter.write(pose_image_plus_data)

    videoWriter.release()
    reencode_video(path)
    add_audio_to_video(path)


def main():
    root_path = Path(".")

    # Automatically find all numeric recording directories across Location_1, Location_2, etc.
    recording_dirs = sorted(
        [p for p in root_path.glob("Location_*/*") if p.is_dir() and p.name.isdigit()]
    )

    print(f"Found {len(recording_dirs)} recordings to generate videos for.\n")

    for recording_path in recording_dirs:
        print(f"Processing {recording_path}...")
        generate_video(recording_path)


if __name__ == "__main__":
    main()