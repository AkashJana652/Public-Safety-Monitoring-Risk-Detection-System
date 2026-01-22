



import cv2
import numpy as np

video = cv2.VideoCapture("Crowd.mp4")
if not video.isOpened():
    print("Video not found")
    exit()

fps = video.get(cv2.CAP_PROP_FPS)

ret, prev_frame = video.read()
prev_gray=cv2.cvtColor(prev_frame,cv2.COLOR_BGR2GRAY)
prev_gray = cv2.resize(prev_gray,(640,480))#resized to speed up processing

normal_motion_values = []#will be used later to calculate avg value of normal motion

#Create a variable to keep frame count also helps in calculating video time and normal motion
video_frame_index=0
frame_count = 0 
avg_motion = 0.0
timestamp="00:00"

#create cooldown to avoid similar risk alerts in short time
alert_cooldown = 3 #sec
last_alert_time = -999

#Create variables to keep track of risk level and risk priority
risk="NORMAL"
candidate_risk = "NORMAL"#hysteris
risk_frame_counter = 0
last_alert_risk = None

risk_priority = {"NORMAL":0,
                 "LOW": 1,
                 "MEDIUM": 2,
                 "HIGH":3}

#variable to decide ifinitial baseline created
baseline_initialised=False

#Handles sudden camera shake or sudden movements
min_motion_threshold = 0.8

#ANgle chaos
ANGLE_CHAOS_THRESHOLD = 1.2  # radians

#COntrol risk state/ hysteris
risk_downgrade_counter = 0
DOWNGRADE_FRAMES = 5
current_risk = "NORMAL"

#Critical zone for zone sepearation
critical_zone = "N/A"
current_zone=None
last_zone=None
zone_alert_counter=0
risk_changed = False
zone_risk = None
last_alerted_state = None
while True:
    #this variable counts the total frames that have processed ubtil now
    #frame_count_total+=1

    '''if frame_count_total%10==0:
        print(f"Processed frame: {frame_count_total}")'''#used this to check if program is working

    #calculate timeframe of video   
    video_time = video_frame_index//fps
    minutes = int(video_time//60)
    seconds = int(video_time%60)
    timestamp = f"{minutes:02d}:{seconds:02d}"

    #Read a single frame of video and check with ret if the variable frame holds a value or not
    ret, frame = video.read()
    if not ret:
        break
    video_frame_index+=1

    #frame resized to size of prev_frame this helped in reducing computational time
    frame = cv2.resize(frame,(640,480))

    #additional info on footage
    cv2.putText(frame,f"Motion: {avg_motion: .2f}",(10,30),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)
    cv2.putText(frame,f"Risk: {risk}",(10,60),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
    cv2.putText(frame,f"Time: {timestamp}",(10,90),cv2.FONT_HERSHEY_SIMPLEX,0.7,(225,255,0),2)
    cv2.putText(frame,f"Zone: {critical_zone}",(10, 120),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255, 255, 0),2)


    #using imshow display a slow but continuous footage of the video
    cv2.imshow("Crowd Feed",frame)
    if cv2.waitKey(1) & 0xFF == ord('e'): #press e to exit the loop
        break 
    
    #convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #calculate the movement of pixels 
    flow = cv2.calcOpticalFlowFarneback(
        prev_gray, gray,
        None,
        0.5, 3, 15, 3, 5, 1.2, 0
    )

    magnitude, angle = cv2.cartToPolar(flow[:,: ,0], flow[:,:, 1])

    #Divide frame into top middle and bottom frames
    h, w = magnitude.shape

    zone_top = magnitude[0:h//3, :]
    zone_middle = magnitude[h//3:2*h//3, :]
    zone_bottom = magnitude[2*h//3:, :]

    #Compute motion perzone
    zone_motion = {
                    "TOP": np.mean(zone_top),
                    "MIDDLE": np.mean(zone_middle),
                    "BOTTOM": np.mean(zone_bottom)
    }

    #DEcide critical zone
    critical_zone = max(zone_motion, key=zone_motion.get)
    current_zone = critical_zone
    avg_motion = zone_motion[critical_zone]
    '''We divide the frame into spatial regions and compute motion independently.
      The most critical region drives the overall risk, enabling localized panic detection.'''

    #avg_motion = np.mean(magnitude) #previously avg motion calculated like this before zones
    angle_std = np.std(angle)#chaos angle

    #How much of the area of the frame is actually moving// Density //
    motion_pixels = magnitude > min_motion_threshold
    motion_density = np.sum(motion_pixels) / magnitude.size


    #Eliminates frame where motion is low
    if avg_motion<min_motion_threshold:
        risk = "NORMAL"
        risk_frame_counter=0
        risk_frame_buffer = []
        prev_gray = gray
        continue

    #calculates what is normal motion using initial 30 frames
    if frame_count < 30:
        normal_motion_values.append(avg_motion)
        frame_count += 1
        prev_gray = gray
        continue

    #Initialize baseline
    if not baseline_initialised:
        normal_motion = np.mean(normal_motion_values)
        baseline_initialised = True
        initial_baseline = normal_motion

    #Calculate risk score    
    risk_score = ((avg_motion / normal_motion)*20)

    #Add chaos factor to risk score
    chaos_factor = 1.0
    if angle_std > ANGLE_CHAOS_THRESHOLD and risk_score > 30:
        chaos_factor = 1.3

    risk_score *= chaos_factor #Chaos should only amplify the risk score not manipulate it entirely
    '''Panic events introduce directional instability. Using angular variance of,
      optical flow vectors we amplify risk only when motion is both strong and chaotic.'''
    
    density_factor = 1.0 #Denisty should only amplify risk not change it completely
    if motion_density > 0.3: #Below 0.3 considered for vehicles and almost no motion like noise
        density_factor = 1.2

    risk_score *= density_factor

    
    #Classify risk based on avg and normal motion
    if risk_score>70:
        risk_frame_counter += 1
        if risk_frame_counter>=3:
            candidate_risk = "HIGH"
    elif 30<risk_score<70:
        risk_frame_counter += 1
        if risk_frame_counter>=3:        
            candidate_risk = "MEDIUM"
    elif 30>risk_score>1:
        risk_frame_counter += 1      
        if risk_frame_counter>=3:   
            candidate_risk = "LOW"
    else:
        candidate_risk = "NORMAL"
        risk_frame_counter=0

    # ---------------- HYSTERESIS LOGIC ---------------- #
    # Escalation: immediate
    if risk_priority[candidate_risk] > risk_priority[current_risk]:
        current_risk = candidate_risk
        risk_downgrade_counter = 0
    # Downgrade: slow and controlled
    elif risk_priority[candidate_risk] < risk_priority[current_risk]:
        risk_downgrade_counter += 1
        if risk_downgrade_counter >= DOWNGRADE_FRAMES:
            current_risk = candidate_risk
            risk_downgrade_counter = 0
    # Same risk: reset downgrade counter
    else:
        risk_downgrade_counter = 0
    # Lock final risk to state
    risk = current_risk

    if risk=="MEDIUM" and zone_alert_counter<48:
        if zone_risk == "MEDIUM":
            risk_changed = True
            zone_risk = None
            risk = "HIGH"
            zone_alert_counter = 0

    #Update baseline
    if risk == "NORMAL" and avg_motion < normal_motion * 1.2:
        normal_motion = 0.99 * normal_motion + 0.1 * avg_motion
        normal_motion = min(normal_motion,initial_baseline*1.3)

    if risk != "NORMAL":
        
        allow_alert = False

        if last_alert_risk == None:
            allow_alert=True
        elif risk_priority[risk]>risk_priority[last_alert_risk]:
            allow_alert=True
        elif video_time - last_alert_time >= alert_cooldown:
            allow_alert=True

        if allow_alert and risk != last_alerted_state:
            last_alerted_state = risk
            print("----- ALERT -----")
            print(timestamp)
            print(f"Risk Level: {risk}")
            print(f"Risk score: {risk_score: .2f}")
            if risk == "LOW":
                cause = "Unusual increase in crowd movement"
                factor = "A sudden shift in pixel movement was detected"
            elif risk == "MEDIUM":
                cause = "Rapid crowd movement detected"
                factor = "A moderate amount of pixel movement was detected for multiple frames"
            elif risk == "HIGH":
                if motion_density>0.45:
                    cause = "The crowd is moving at varied angles. stampede is likely to happen"
                    factor = "High directional chaos and density"
                    unit = "SRPF and crowd control unit to be deployed"
                    action= "OBserve the situation and control the crowd"
                    urgency="Urgent"
                elif risk_changed and last_alert_risk == "MEDIUM":
                    cause = " POtential increase in crowd level is suspected"
                    factor = "The crowd density is at a higher level for long time"
                    unit = "Crowd Management Force(CMF) is to be deployed"
                    action = "Control the crowd and diffuse any potential mob activities"
                    urgency = "Immediate"
                    zone_alert_counter = 0
                else:
                    cause = "Continuous high activity in the region"
                    factor = "High density"
                    unit = "observation unit"
                    action= "OBserve the situation only via feed"
                    urgency="minimal"                    


            if risk!="HIGH":
                print(f"Time:{timestamp}:Cause: {cause} (Zone: {critical_zone}\nRisk level: {risk}: Risk score:{risk_score} \n{factor})")
            else:
                print(f"Time:{timestamp}:Cause: {cause} (Zone: {critical_zone}\nUnit: {unit}\nACtion: {action}\nUrgency: {urgency}\n{factor})")

            
            #Calculate confidence(How strong and consistent the evidence was for this alert)
#COnfidence change
            #normalize risk score into [0, 1]
            if risk_score < 30:
                strength = 0.5 + 0.1 * (risk_score / 30)
            elif risk_score < 70:
                strength = 0.7 + 0.1 * ((risk_score - 30) / 40)
            else:
                strength = 0.9

            persistence = min(risk_frame_counter / 3, 1.0) #How many consecutive frames agreed

            confidence_score = 0.6 * strength + 0.4 * persistence  #Strength matters more than duration

 

            print(f"Confidence: {confidence_score: .2f}")
            print("-----------------\n")

            #cReate log file
            with open("alert.log","a") as f:
                if risk!="HIGH":
                    f.write(f"\n{timestamp} : {risk} : {risk_score} :{cause} :{critical_zone}:{factor}\n\n")
                else:
                    f.write(f"\n{timestamp} : {risk}: {risk_score} :{cause} :{critical_zone}:{factor}: Unit: {unit}\nACtion: {action}\nUrgency: {urgency}\n")

                    f.write("\n\n")      

            if risk == "MEDIUM":
                if current_zone == last_zone:
                    zone_alert_counter += 1
                else:
                    zone_alert_counter = 0
            last_zone = current_zone

            risk_changed = False
            last_alert_time = video_time
            last_alert_risk = risk
    prev_gray = gray
    
cv2.destroyAllWindows()
print("\nFOOtAGE ENDED\n")
video.release()



