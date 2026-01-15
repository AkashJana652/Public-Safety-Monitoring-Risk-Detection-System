# Public-Safety-Monitoring-Risk-Detection-System

***Problem Statement:***
In crowded public environments such as markets, festivals, metro stations, and public gatherings, safety incidents like panic, stampedes, sudden crowd movements, or accidents can escalate rapidly if not detected early. 


The objective of this project is to detect abnormal crowd behavior from video footage and generate timely alerts, without identifying or tracking individuals.

***Approach Overview:***

The system analyzes frame‑to‑frame motion in a crowd video to estimate overall crowd movement intensity.
Instead of detecting individuals, it operates at a crowd level, focusing on aggregate motion patterns.

The core idea is:
To detect sudden, large increases in overall pixel motion,which often indicate abnormal crowd behavior such as panic or rapid dispersal.

***1. Video Processing:***

The input video is read frame‑by‑frame using OpenCV.
Frames are resized to 640×480 to reduce computational cost while preserving global motion patterns, this also helps in speeding up the processing of data.
Frames are converted to grayscale for efficient motion analysis.

***2. Motion Estimation (Optical Flow):***

Dense Optical Flow (Farneback method) is used to compute pixel‑wise motion between consecutive frames.
For each frame, the magnitude of motion vectors is calculated and the average motion magnitude represents overall crowd movement intensity for that frame.

This avoids: Face detection, Person tracking and Identity inference.

***3. Baseline (Normal Behavior Modeling):***

The first 30 frames of the video are assumed to represent normal crowd behavior.
The average motion from these frames is used as a **baseline reference**.

All future motion values are compared relative to this baseline, making the system adaptable to different videos.

***4. Risk Classification:***

Crowd behavior is classified using rule‑based thresholds:

Condition (Relative to Baseline) ||	Risk Level

≤ 1.5 × baseline		 ||	NORMAL

> 1.5 × baseline		 ||	LOW

> 2 × baseline			 ||	MEDIUM

> 3 × baseline			 ||	HIGH

\#To reduce false positives, a risk must persist for multiple consecutive frames before being confirmed.

***5. Alert Generation:***

Alerts are printed to the console with: Video timestamp, Risk level and Human‑readable cause.
\#A priority‑aware cooldown mechanism prevents alert spam while ensuring escalation is never suppressed.

Examples:

a)LOW -> MEDIUM -> HIGH alerts are always allowed
b)Repeated alerts of the same level are rate‑limited

***6. Visualization:***

Real‑time overlays are displayed on the video feed: Average motion value, Current risk level and Video timestamp.
This helps in monitoring, debugging, and demonstration.

***7. Privacy‑preserving design principles:***

\#Ethical Considerations are also kept in mind while designing the program as no individuals are detected, tracked, or identified.
\#The analysis is performed purely on aggregate motion patterns

***## Files Included ##***

1)Risk_detection_system.py — Main Python script
2)README.md — Project documentation
3)Screenshots of: Console alerts and video feed with overlays

***## How to Run ##***

pip install opencv-python numpy
python crowd\_monitoring.py

Press e to exit the video window.

***## Limitations ##***

Sudden camera shake may affect motion estimation.
Baseline assumes initial frames represent normal behavior.
Performance depends on video resolution and frame rate.

***## Future Improvements ##***

Adaptive baseline updating for long videos
Region‑based motion analysis
Directional coherence detection

***## Conclusion ##***

This project demonstrates an explainable, ethical, and efficient approach to crowd behavior anomaly detection using classical computer vision techniques.

By focusing on logic, transparency, and safety, the system aligns well with real‑world surveillance and monitoring requirements without any individual identification or biometric data.


