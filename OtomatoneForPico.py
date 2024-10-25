from machine import Pin
import time
from BLE_CEEO import Yell
from mqtt import MQTTClient
import network


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('Tufts_Robot', '')

while wlan.ifconfig()[0] == '0.0.0.0':
    print('.', end=' ')
    time.sleep(1)

# We should have a valid IP now via DHCP
print(wlan.ifconfig())
mqtt_broker = 'broker.hivemq.com' 
port = 1883
topic_sub = 'ME35-24/julian'       # this reads anything sent to ME35
topic_pub = 'ME35-24/julian'

vel='f'
def callback(topic, msg):
    #global state
    global vel
    if msg.decode()=="stop":
        #state=False
        print("state is false")
        vel='fff'
    else:
        #state=True
        print("state is true")
        vel='f'
    

client = MQTTClient('JULIAN', mqtt_broker , port, keepalive=60)
client.connect()
print('Connected to %s MQTT broker' % (mqtt_broker))
client.set_callback(callback)          # set the callback if anything is read
client.subscribe(topic_sub.encode())   # subscribe to a bunch of topics


ldr=machine.ADC(27)
f=Pin('GPIO14', Pin.IN, Pin.PULL_UP)
led1 = Pin('GPIO17', Pin.OUT)

NoteOn = 0x90
NoteOff = 0x80
StopNotes = 123
SetInstroment = 0xC0
Reset = 0xFF

velocity = {'off':0, 'pppp':8,'ppp':20,'pp':31,'p':42,'mp':53,
    'mf':64,'f':80,'ff':96,'fff':112,'ffff':127}
    
p = Yell('julian', verbose = True, type = 'midi')
p.connect_up()
        
channel = 0
#note = 55
cmd = NoteOn

channel = 0x0F & channel
timestamp_ms = time.ticks_ms()
tsM = (timestamp_ms >> 7 & 0b111111) | 0x80
tsL =  0x80 | (timestamp_ms & 0b1111111)

c =  cmd | channel     
G = bytes([tsM,tsL,c,55,velocity['f']])
Gs = bytes([tsM,tsL,c,56,velocity['f']])
A = bytes([tsM,tsL,c,57,velocity['f']])
As=bytes([tsM,tsL,c,58,velocity['f']])
B=bytes([tsM,tsL,c,59,velocity['f']])
C=bytes([tsM,tsL,c,60,velocity['f']])
Cs=bytes([tsM,tsL,c,61,velocity['f']])
D=bytes([tsM,tsL,c,62,velocity['f']])
Ds=bytes([tsM,tsL,c,63,velocity['f']])
E=bytes([tsM,tsL,c,64,velocity['f']])
F=bytes([tsM,tsL,c,65,velocity['f']])
Fs=bytes([tsM,tsL,c,66,velocity['f']])

time.sleep(2)
state=True

while True:
    led1.on()
    client.check_msg()

    G = bytes([tsM,tsL,c,55,velocity[vel]])
    Gs = bytes([tsM,tsL,c,56,velocity[vel]])
    A = bytes([tsM,tsL,c,57,velocity[vel]])
    As=bytes([tsM,tsL,c,58,velocity[vel]])
    B=bytes([tsM,tsL,c,59,velocity[vel]])
    C=bytes([tsM,tsL,c,60,velocity[vel]])
    Cs=bytes([tsM,tsL,c,61,velocity[vel]])
    D=bytes([tsM,tsL,c,62,velocity[vel]])
    Ds=bytes([tsM,tsL,c,63,velocity[vel]])
    E=bytes([tsM,tsL,c,64,velocity[vel]])
    F=bytes([tsM,tsL,c,65,velocity[vel]])
    Fs=bytes([tsM,tsL,c,66,velocity[vel]])


    
    time.sleep(.2)
    ldr_value=ldr.read_u16()
    #print(ldr_value)
    #print(f.value())
    if ldr_value < 500 and f.value()==0 and state==True:
        p.send(Fs)
    if ldr_value < 550 and ldr_value >500 and f.value()==0 and state==True:
        p.send(F)
    if ldr_value < 600 and ldr_value >550 and f.value()==0 and state==True:
        p.send(E)
    if ldr_value < 650 and ldr_value >600 and f.value()==0 and state==True:
        p.send(Ds)
    if ldr_value < 700 and ldr_value >650 and f.value()==0 and state==True:
        p.send(D)
    if ldr_value < 750 and ldr_value >700 and f.value()==0 and state==True:
        p.send(Cs)
    if ldr_value < 800 and ldr_value >750 and f.value()==0 and state==True:
        p.send(C)
    if ldr_value < 850 and ldr_value >800 and f.value()==0 and state==True:
        p.send(B)
    if ldr_value < 900 and ldr_value >850 and f.value()==0 and state==True:
        p.send(As)
    if ldr_value < 950 and ldr_value >900 and f.value()==0 and state==True:
        p.send(A)
    if ldr_value < 1000 and ldr_value >950 and f.value()==0 and state==True:
        p.send(Gs)
    if ldr_value > 1000 and f.value()==0 and state==True:
        p.send(G)
        
    
    
p.disconnect()
led1.off()
