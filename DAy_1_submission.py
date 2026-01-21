
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
risk_frame_counter = 0
last_alert_risk = None

risk_priority = {"NORMAL":0,
                 "LOW": 1,
                 "MEDIUM": 2,
                 "HIGH":3}

#variable to decide ifinitial baseline created
baseline_initialised=False

#Handles sudden camera shake or sudden movements
min_motion_threshold = 0.5

#holds the risk scores until an alert is printed
risk_frame_buffer = []

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
    avg_motion = np.mean(magnitude)

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
    risk_score = ((avg_motion / normal_motion)*20)
    
    #Classify risk based on avg and normal motion
    if risk_score>70:
        risk_frame_buffer.append(risk_score)
        risk_frame_counter += 1
        if risk_frame_counter>=3:
            risk = "HIGH"
    elif 30<risk_score>70:
        risk_frame_buffer.append(risk_score)
        risk_frame_counter += 1
        if risk_frame_counter>=3:        
            risk = "MEDIUM"
    elif 30>risk_score>1:
        risk_frame_buffer.append(risk_score)
        risk_frame_counter += 1      
        if risk_frame_counter>=3:   
            risk = "LOW"
    else:
        risk = "NORMAL"
        risk_frame_counter=0
              
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

        if allow_alert:
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
            else:
                cause = "Possible panic or stampede-like movement detected"
                factor = "HUge instabilty was detected in pixel movement"

            print(f"Cause: {cause}")
            
            print("Supporting factors:")
            print(f"{factor}")

            #Calculate confidence
            if len(risk_frame_buffer):
                confidence_score = sum(risk_frame_buffer)/len(risk_frame_buffer)
                confidence_score = (confidence_score/80)#to convert into percentage but in decimals(0 t0 1)
            else:
                confidence_score = risk_score/100
            risk_frame_buffer=[]  

            print(f"Confidence: {confidence_score: .2f}")
            print("-----------------\n")

            #cReate log file
            with open("alert.log","a") as f:
                f.write(f"{timestamp} : {risk} : {risk_score} :{cause}\n")
            
            risk_frame_counter=0
            last_alert_time = video_time
            last_alert_risk = risk
    prev_gray = gray
    
cv2.destroyAllWindows()
print("\nFOOtAGE ENDED\n")
video.release()



