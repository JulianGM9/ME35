from pyscript.js_modules import teach, pose, ble_library, mqtt_library

myClient = mqtt_library.myClient("broker.hivemq.com", 8884)
mqtt_connected = False
sub_topic = 'ME35-24/listen'
pub_topic = 'ME35-24/tell'

async def received_mqtt_msg(message):
    message = myClient.read().split('	')  #add here anything you want to do with received messages

async def run_model(URL2):
    s = teach.s  # or s = pose.s
    s.URL2 = URL2
    await s.init()
    
async def connect(name):
    global mqtt_connected
    myClient.init()
    while not myClient.connected:
        await asyncio.sleep(2)
    myClient.subscribe(sub_topic)
    myClient.callback = received_mqtt_msg
    mqtt_connected = True


def get_predictions(num_classes):
    predictions = []
    for i in range (0,num_classes):
        divElement = document.getElementById('class' + str(i))
        if divElement:
            divValue = divElement.innerHTML
            predictions.append(divValue)
    return predictions

import asyncio
await run_model("https://teachablemachine.withgoogle.com/models/xF2N4LG6v/") #Change to your model link
await connect('JULIAN')

while True:
    predictions = get_predictions(2)
    class1=predictions[0]
    class2=predictions[1]
    print(class2)
    if mqtt_connected:
        if class1[9]=="1":
            print("C1")
            myClient.publish("ME35-24/julian", "start")
        if class2[9]=="1":
            print("C2")
            myClient.publish("ME35-24/julian", "stop")
    await asyncio.sleep(2)
