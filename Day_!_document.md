Topic: Motion-Based Risk Detection System

Team Code: 26CC4925

Team Leader: Akash Jana

Team Member: Utkarsh Pandey







**1. Risk Score Calculation Mechanism**

The system quantifies "risk" based on the intensity of pixel movement (optical flow) compared to a learned baseline. The calculation follows a three-step process:



Step A: Motion Magnitude Extraction (Optical Flow) The system uses the Farneback Optical Flow algorithm (cv2.calcOpticalFlowFarneback) to track the movement of pixels between the previous frame and the current frame.



Magnitude: For every pixel, a motion vector is calculated. The code computes the magnitude (speed) of these vectors.



Average Motion (avg\_motion): The mean value of all motion magnitudes across the entire frame is calculated to represent the global activity level of that specific moment.



Step B: Baseline Establishment



Initialization: For the first 30 frames, the system records the avg\_motion to understand the standard environment.



Normal Motion (normal\_motion): The average of these first 30 frames becomes the "Zero Point" or baseline against which future anomalies are measured.



Step C: The Risk Score Formula The risk score is a dimensionless ratio that indicates how many times intense the current motion is compared to the baseline.



RiskScore=( Normal Motion/Current Average Motion)×20

Interpretation: A score of 10 implies the motion is exactly normal. A score of 70 implies the motion is 7x more intense than the established baseline.



**2. Risk Classification Thresholds**

Once the risk\_score is calculated, it is categorized into severity levels. 

Risk Level	Threshold Logic	Interpretation

HIGH	Score > 70	Massive instability; typically panic or stampede-like behavior.

MEDIUM	30 < Score <= 70	Rapid movement; significant deviation from the norm.

LOW	Score < 30	Unusual increase; slightly higher than normal activity.





3\. False Alarm Mitigation Strategies

To prevent noise, camera shake, or momentary glitches from triggering invalid alerts, the system implements four distinct layers of protection:



A. Temporal Persistence Check (The 3-Frame Rule)



Mechanism: An alert is not triggered the moment the risk\_score crosses a threshold.



Logic: The system uses a variable risk\_frame\_counter. The risk condition must persist for at least 3 consecutive frames before the system accepts it as a valid state.



Benefit: This filters out single-frame anomalies (e.g., a glitch in the video feed or a sudden light flash) that would otherwise cause a "flickering" risk status.



B. Adaptive Baseline (Environmental Drift)



Mechanism: When the risk is NORMAL, the system slowly updates the normal\_motion value using a weighted average:normal\_motion = 0.99 \* normal\_motion + 0.1 \* avg\_motion



Logic: If the crowd naturally gets slightly busier over time, the "Normal" baseline gradually rises to match it.



Clamping: To prevent the baseline from rising too high (which would mask real dangers), it is capped at 1.3x the initial\_baseline.



Benefit: Prevents false alarms due to gradual environmental changes (e.g., traffic slowly building up over an hour).



C. Alert Cooldown Timer



Mechanism: The alert\_cooldown variable is set to 3 seconds.



Logic: Once an alert is sent, the system records last\_alert\_time. It blocks identical or lower-priority alerts until 3 seconds have passed (video\_time - last\_alert\_time >= alert\_cooldown).



Benefit: Prevents the logs or console from being flooded with hundreds of duplicate messages for

