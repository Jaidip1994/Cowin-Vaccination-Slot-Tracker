# Cowin Vaccination Slot Tracker

### Problem Statement
In covid situation its a very crucial thing to get vaccinated and the most difficult part is to get a vaccination slot. As currently there is a medical supply shortage so as a result the slots available are very less. 

### How to get slots for vaccination ?
Answer is via automation. So that was my Idea, I know cowin open APIs are present but still its been a while i have played around with automation Tools, for this use case selenium, Once there is a slot available notification is being sent to the user, via windows10 notification, in whatsapp and in Andoid app ( via PushBullet APP)

### Prerequisite 
1. This script is written only for Windows based OS , especially windows 10.
2. Python 3.5 > 
3. Need to download PushBullet App https://www.pushbullet.com/, on your Android and Windows machine, so using this one type of notification will sent, and it will be synced across your configured devices
4. After downloading the pushbullet app, you need to get the access token.
Got to https://www.pushbullet.com/#settings -> Settings -> Account -> Access Token -> Create Access Token. Copy that and keep it aside.
5. This only looks for Paid Vaccination Center , as this was my ask. Script can be enhanced by changing the xpath of the paid to any. 
6. So as to run the script run this command, after cloning the project.
    ```shell
    $ pip install -r requirement.txt
    ```
7. Then in the open `cowinTracker.py` and then provide 
    -   list of Pincode 
    -   access token created in step 5
    -   Whatsapp Group or Person's Name
    
    ![pinv](Cowin-Vaccination-Slot-Tracker\utility\carbon.png)
8. Now run `cowinTracker.py` this will run infinetely for each Pincode & Paid Vaccination Center and it will identify whether any vacination slots are available or not after every 10mins interval
    ```shell
    $ python cowinTracker.py
    Trying for 1 Times
    |████████████████████████████████████████| 7/7 [100%] in 27.7s (0.25/s)
    Will Try after 10mins...
    [22164:24836:0506/164442.362:ERROR:gpu_init.cc(426)] Passthrough is not supported, GL is disabled
    Trying for 2 Times
    |████████████████████████████████████████| 7/7 [100%] in 27.7s (0.25/s)
    Will Try after 10mins...
    Trying for 3 Times
    |████████████████████████████████████████| 7/7 [100%] in 28.0s (0.25/s)
    Will Try after 10mins... 
    ```
9. In Pushbullet App it will be sent like this 
    ![PushBulletApp](Cowin-Vaccination-Slot-Tracker\utility\pushBullet.jpg)
10. And in windows Notification Tab
    ![Windows Notification](Cowin-Vaccination-Slot-Tracker\utility\windowsToast.jpg)
