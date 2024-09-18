import network
import time
import ubinascii
from machine import Pin, PWM
import random
import neopixel
from mqtt import MQTTClient

#network manager and mqtt manager were both organized by chatgpt
class NetworkManager:
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password
        self.station = network.WLAN(network.STA_IF)
        self.station.active(True)
        self.mac = ubinascii.hexlify(network.WLAN().config('mac'), ':').decode()
        print(self.mac)

    def scan_and_connect(self):
        print("Scanning...")
        for _ in range(2):
            scan_result = self.station.scan()
            for ap in scan_result:
                print("SSID:%s BSSID:%s Channel:%d Strength:%d RSSI:%d Auth:%d " % ap)
            print()
            time.sleep_ms(1000)

        self.station.connect(self.ssid, self.password)
        while self.station.ifconfig()[0] == '0.0.0.0':
            print('.', end=' ')
            time.sleep(1)
        print(self.station.ifconfig())

class MQTTManager:
    def __init__(self, broker, port, client_id, topic_sub, topic_pub):
        self.client = MQTTClient(client_id, broker, port, keepalive=60)
        self.topic_sub = topic_sub
        self.topic_pub = topic_pub

    def connect(self, callback):
        mqtt_broker = 'broker.hivemq.com' 
        self.client.connect()
        print('Connected to %s MQTT broker' % mqtt_broker)
        self.client.set_callback(callback)
        self.client.subscribe(self.topic_sub.encode())

    def check_messages(self):
        self.client.check_msg()
        
# buzzer class was organized by chat gpt but we added some functions to it (play_rocky)
class Buzzer:
    def __init__(self, pin):
        self.buzzer = PWM(Pin(pin, Pin.OUT))
        self.buzzer.freq(440)

    def play_tone(self, freq=440, duration=0.3):
        self.buzzer.freq(freq)
        self.buzzer.duty_u16(int(65536/2))
        time.sleep(duration)
        self.buzzer.duty_u16(0)
    def play_rocky(self):
        

        b = 2.0
        rest = 1000000
        A = 440
        B = 494
        C = 262
        D = 294
        E = 330
        F = 349
        G = 392
        highF = 698
        highE = 660
        highC = 524
        notes1 = [E, G, A, rest, A, B, E, rest]
        duration1 = [b/16, 3*b/16, 3*b/4 - 0.2, 0.2, b/16, 3*b/16, 3*b/4 - 0.2, 0.2]
        
        notes2 = [C, D, C, D, C, D, E, rest]
        duration2 = [b/12, b/12, b/12, 3*b/16, b/16, b/16, 3*b/16+b/4 - 0.2, 0.2]
        
        notes3 = [E, highC, rest, highC, B, rest, B, A, rest, A, rest, A, G, highF, highE]
        duration3 = [b/8, b/16-0.01, 0.01, b/16, b/8 - 0.01, 0.01, b/16, b/16 - 0.01, 0.01, b/16 - 0.01, 0.01, b/16, b/4, b/8, b]
        
        buzzer = machine.PWM(machine.Pin('GPIO18', Pin.OUT))
        
        def beep(freq = 440, duration = 0.3):
            buzzer.freq(freq)
            buzzer.duty_u16(int(65536/2))
            time.sleep(duration)
            buzzer.duty_u16(0)
        
        for i in range(2):
            for i in range(len(notes1)):
                beep(notes1[i], duration1[i])
                
        for i in range(len(notes2)):
            beep(notes2[i], duration2[i])
            
        for i in range(len(notes3)):
            beep(notes3[i], duration3[i])

#This function was organized by chat gpt
class LEDController:
    def __init__(self, pin):
        self.led = neopixel.NeoPixel(Pin(pin), 1)
        self.stateoff = (0, 0, 0)

    def set_color(self, color):
        self.led[0] = color
        self.led.write()

# we wrote this class from scratch
class GPIOLED:
    def __init__(self, pin):
    	self.led= PWM(Pin(pin, Pin.OUT))
    def blink(self):
    	for i in range(0,5):
    		self.led.on()
    		time.sleep(1)
    		self.led.off()
        	time.sleep(1)
    def breath(self):
        self.led.freq(50)
        for i in range(0, 65535, 500):
            self.led.duty_u16(i)
            time.sleep(0.01)
        for i in range(65535, 0, -500):
            self.led.duty_u16(i)
            time.sleep(0.01)

#chat gpt
class Button:
    def __init__(self, pin):
        self.button = Pin(pin, Pin.IN)

    def is_pressed(self):
        return not self.button.value()

#chat gpt
class Robot:
    def __init__(self, ssid, password, mqtt_broker, mqtt_port):
        self.network_manager = NetworkManager(ssid, password)
        self.mqtt_manager = MQTTManager(mqtt_broker, mqtt_port, 'ME35_chris', 'ME35-24/Jeffrey', 'ME35-24/tell')
        self.buzzer = Buzzer('GPIO18')
        self.led_controller = LEDController(28)
        self.button = Button('GPIO20')
        self.led = GPIOLED('GPIO0')
        self.mode = True

    def callback(self, topic, msg):
        print((topic.decode(), msg.decode()))
        if msg.decode() == "on":
            self.mode = True
        elif msg.decode() == "off":
            self.mode = False

    

    def random_num(self, min_value, max_value):
        if min_value > max_value:
            raise ValueError("min_value must be less than or equal to max_value")
        return random.randint(min_value, max_value)

    


    def run(self):
        self.network_manager.scan_and_connect()
        self.mqtt_manager.connect(self.callback)
        self.led_controller.set_color((0,255,0))

        while True:
            self.mqtt_manager.check_messages()
            if self.mode:
                self.led_controller.set_color((0,255,0))
                self.led.breath()
                if self.button.is_pressed():
                    self.led_controller.set_color((self.random_num(0, 255), self.random_num(0, 255), self.random_num(0, 255)))
                    #self.led_controller.set_color((88, 6, 156))
                    #self.play_rocky()
                    self.buzzer.play_tone(880, 1)
                    #self.buzzer.play_rocky()
                    
            else:
                self.led_controller.set_color(self.led_controller.stateoff)
            time.sleep(0.1)

if __name__ == "__main__":
    robot = Robot('tufts_eecs', 'foundedin1883', 'broker.hivemq.com', 1883)
    robot.run()
