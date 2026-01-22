

&nbsp;                   CROWD RISK ANALYSIS \& ACTION SYSTEM

&nbsp;                           Technical Documentation



\#OVERVIEW



This Python application performs real-time video analysis to detect crowd risks. 

It goes beyond simple motion detection by calculating a "Risk Score" based on 

motion intensity, flow chaos (panic), and density.



The system provides "Actionable Intelligence"—instead of just beeping, it 

recommends specific operational units (e.g., SRPF, CMF, Observation Unit) and 

urgency levels based on the specific type of crowd behavior detected.



###### CHANGES MADE TODAY



A.(Decision Support Intelligence At Higher Risk)

B.(Multi-Zonal Risk Propagation and Escalation)

C.(

\#ALGORITHM \& LOGIC

A. OPTICAL FLOW \& ZONING

&nbsp;  - The system uses the Farneback Optical Flow algorithm to estimate the 

&nbsp;    velocity and direction of every pixel.

&nbsp;  - The video frame is resized to 640x480 for performance.

&nbsp;  - The frame is divided into three horizontal zones: TOP, MIDDLE, BOTTOM.

&nbsp;  - The "Critical Zone" is the specific zone with the highest motion intensity.



B. RISK SCORING FORMULA

&nbsp;  The system calculates a dynamic score for every frame:

&nbsp;  

&nbsp;  Risk Score = (Current Motion / Normal Baseline) \* 20



&nbsp;  This score is then amplified by two factors:

&nbsp;  1. Chaos Factor (x1.3): Triggered if the variance in movement angles 

&nbsp;     exceeds 1.2 radians (indicates panic/disorder).

&nbsp;  2. Density Factor (x1.2): Triggered if more than 30% of the frame 

&nbsp;     contains motion.



C. RISK CLASSIFICATION

&nbsp;  - NORMAL: Score < 1

&nbsp;  - LOW:    Score 1 - 30

&nbsp;  - MEDIUM: Score 30 - 70

&nbsp;  - HIGH:   Score > 70



D. DECISION MATRIX (ACTIONABLE INTELLIGENCE)

&nbsp;  When Risk is HIGH, the system categorizes the threat to suggest actions:

&nbsp;  

&nbsp;  Type 1: STAMPEDE RISK

&nbsp;  - Condition: Motion Density > 0.45 (Very high congestion).

&nbsp;  - Action: "Observe and control crowd."

&nbsp;  - Unit: SRPF (State Reserve Police Force).

&nbsp;  - Urgency: URGENT.



&nbsp;  Type 2: ESCALATING CROWD

&nbsp;  - Condition: Risk jumped from MEDIUM to HIGH after sustained activity.

&nbsp;  - Action: "Diffuse potential mob activities."

&nbsp;  - Unit: Crowd Management Unit.

&nbsp;  - Urgency: IMMEDIATE.



&nbsp;  Type 3: HIGH ACTIVITY (General)

&nbsp;  - Condition: High motion but organized/low density.

&nbsp;  - Action: "Observe via feed."

&nbsp;  - Unit: Observation Unit.

&nbsp;  - Urgency: MINIMAL.



E. STABILITY LOGIC (HYSTERESIS)

&nbsp;  To prevent false alarms and "flickering" alerts:

&nbsp;  - Escalation: Immediate (Normal TO High happens instantly).

&nbsp;  - De-escalation: Controlled. The risk must remain low for 5 consecutive 

&nbsp;    frames (DOWNGRADE\_FRAMES) before the system lowers the alert level.





C. LOG FILE (alert.log)

&nbsp;  Automatically appends all alerts to 'alert.log' for audit purposes.

&nbsp;  Format: \[Timestamp] : \[Risk] : \[Score] : \[Cause] : \[Zone]



6\. CONFIGURATION PARAMETERS



You can tune these variables inside the script:



\- min\_motion\_threshold (Default: 0.8): 

&nbsp; Sensitivity filter. Increase this if the system is detecting dust or wind.



\- ANGLE\_CHAOS\_THRESHOLD (Default: 1.2): 

&nbsp; The threshold for "Panic". Lowering this makes the system more sensitive 

&nbsp; to disorganized movement.



\- alert\_cooldown (Default: 3): 

&nbsp; Time in seconds to wait before repeating the same alert.



7\. LIMITATIONS

--------------

1\. Camera Stability: The code assumes a static camera (CCTV). If the camera 

&nbsp;  pans, tilts, or shakes, the Optical Flow will treat the entire screen as 

&nbsp;  moving, triggering a false High Risk alert.



2\. Initialization: The system learns "Normal" motion from the first 30 frames.

&nbsp;  The video must start with a relatively calm scene for accurate calibration.

&nbsp;  However an adaptive baseline has been set which will automatically reconfigure 

&nbsp;  the base line condition whenever situation\\crowd becomes normal.



3.The System Does Not Incorporate Skeleton Mapping For every individual in the crowd.

&nbsp; due to this suspicious activity of a single individual cannot be analyzed

