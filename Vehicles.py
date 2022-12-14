
import pigpio
import time
import threading
import RPi.GPIO as GPIO
import socket
import cv2
import numpy
import time
import pickle

backmotorspeed=0                 
fmotorspeed=45
#motor class
class Motor:
    def __init__(self,ena,in1,in2):
        self.ENA=ena
        self.IN1=in1
        self.IN2=in2


        GPIO.setup(self.ENA,GPIO.OUT,initial=GPIO.LOW)
        self.ENA_speed=GPIO.PWM(self.ENA,600)
        self.ENA_speed.start(0)
        self.ENA_speed.ChangeDutyCycle(0)
        GPIO.setup(self.IN1, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.IN2, GPIO.OUT, initial=GPIO.LOW)

    #轉速設定
    def speed(self,speed1):
        self.ENA_speed.ChangeDutyCycle(speed1)

    def forward(self):
        GPIO.output(self.ENA, True)
        GPIO.output(self.IN1, True)
        GPIO.output(self.IN2, False)

    def backward(self):
        GPIO.output(self.ENA, True)
        GPIO.output(self.IN1, False)
        GPIO.output(self.IN2, True)

    def stop(self):
        GPIO.output(self.ENA, True)
        GPIO.output(self.IN1, False)
        GPIO.output(self.IN2, False)
        
def angle_to_duty_cycle(angle=0):
    duty_circle=int(500*PWM_FREQ +(1900*PWM_FREQ*angle/180))
    return duty_circle
        
#motor setting
PWM_CONTROL_PIN = 18
PWM_FREQ = 50
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
motor=Motor(25,12,16)

def frontmotor():
    global fmotorspeed
    STEP = 15
    pi = pigpio.pi()
    try:
        while True:
            angle=fmotorspeed
#             angle=rnadom.randint(5,85)
#             print('angle=',angle)
#             if angle < 5:
#                 angle=5
#             elif angle > 85:
#                 angle=85
#             else:
#                 angle=angle
            pi.hardware_PWM(PWM_CONTROL_PIN, PWM_FREQ, angle_to_duty_cycle(angle))
            time.sleep(0.1)
    except KeyboardInterrupt:
        print('close program')
    finally:
        pi.set_mode(PWM_CONTROL_PIN, pigpio.INPUT)


def backmotor():
    while True:
        global backmotorspeed
        global fmotorspeed
#         print('bspeed=',backmotorspeed,'\n')
#         print('fspeed=',fmotorspeed,'\n')
        #speed=random.randrange(0,100)
#         if backmotorspeed/3 >= 30:
#             bspeed=30
#         else:
#             bspeed=backmotorspeed/3
#         print('b1=',backmotorspeed)
#         print('b2=',bspeed)
        speed=backmotorspeed
        if speed >=50:
            speed=50
        else:
             speed=speed   
        print('speed=',speed)
        motor.speed(speed)
        motor.forward()
        time.sleep(0.1)
#         motor.speed(bspeed)

#         if backmotorspeed == 0:
#             motor.stop()
#         else:
#             motor.forward()
#             time.sleep(1)

        if 0xFF==ord('p'):
            print("back motor stop")
            motor.stop()
            
def SendVideo():
    #建立sock連線
    #address要連線的伺服器IP地址和埠號
    address = ('192.168.50.5',8002)
    try:
        #建立socket物件，引數意義見https://blog.csdn.net/rebelqsp/article/details/22109925
        #socket.AF_INET：伺服器之間網路通訊 
        #socket.SOCK_STREAM：流式socket,for TCP
        sockv = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        #開啟連線
        sockv.connect(address)
    except socket.error as msg:
        print(msg)
        sys.exit(1)

    #建立影象讀取物件
    capture = cv2.VideoCapture(0)
    #讀取一幀影象，讀取成功:ret=1 frame=讀取到的一幀影象；讀取失敗:ret=0
    ret,frame = capture.read()
    #壓縮引數，後面cv2.imencode將會用到，對於jpeg來說，15代表影象質量，越高代表影象質量越好為 0-100，預設95
    encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),15]

    while ret:
        #停止0.1S 防止傳送過快服務的處理不過來，如果服務端的處理很多，那麼應該加大這個值
        time.sleep(0.01)
        #cv2.imencode將圖片格式轉換(編碼)成流資料，賦值到記憶體快取中;主要用於影象資料格式的壓縮，方便網路傳輸
        #'.jpg'表示將圖片按照jpg格式編碼。
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        result,imgencode = cv2.imencode('.jpg',frame,encode_param)
        #建立矩陣
        data = numpy.array(imgencode)
        #將numpy矩陣轉換成字元形式，以便在網路中傳輸
        stringData = data.tostring()
        
        #先發送要傳送的資料的長度
        #ljust() 方法返回一個原字串左對齊,並使用空格填充至指定長度的新字串
        sockv.send(str.encode(str(len(stringData)).ljust(16)));
        #傳送資料
        sockv.send(stringData);
        #讀取伺服器返回值
#         receive = sockv.recv(1024)
        #if len(receive):print(str(receive,encoding='utf-8'))
        #讀取下一幀圖片
        ret,frame = capture.read()
        if cv2.waitKey(10) == 27:
            break
    sockv.close()

t1 = threading.Thread(target = SendVideo)
t1.start()
t2 = threading.Thread(target = backmotor)
t2.start()
t3 = threading.Thread(target = frontmotor)
t3.start()

    
    
def recv(sock, addr):
    '''
    一個UDP連線在接收訊息前必須要讓系統知道所佔埠
    也就是需要send一次，否則win下會報錯
    '''
    global backmotorspeed
    global fmotorspeed,step
    sock.sendto(name.encode('utf-8'), addr)
    while True:  
        data,addr = sock.recvfrom(1024)
        backmotorspeed=data[0]
        fmotorspeed=data[2]
#         print('distance=',backmotorspeed)
#         print('angle=',fmotorspeed)
#         print(fmotorspeed)
#         print('b=',backmotorspeed)
#         print('dis=',fmotorspeed)
        

        
        


# def send(sock, addr):
#     '''
#         傳送資料的方法
#         引數：
#             sock：定義一個例項化socket物件
#             server：傳遞的伺服器IP和埠
#     '''
#     while True:
#         string = input('')
#         message = name + ' : ' + string
#         data = message.encode('utf-8')
#         sock.sendto(data, addr)
#         if string.lower() == 'EXIT'.lower():
#             break

def main():
    '''
        主函式執行方法，通過多執行緒來實現多個客戶端之間的通訊
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ('192.168.50.5', 9999)
    tr = threading.Thread(target=recv, args=(s, server), daemon=True)
#     ts = threading.Thread(target=send, args=(s, server))
    tr.start()
    tr.join()
#     ts.start()
#     ts.join()
    s.close()

if __name__ == '__main__':
    print("-----歡迎來到聊天室,退出聊天室請輸入'EXIT(不分大小寫)'-----")
    name = 'Andy'
    print('-----------------%s------------------' % name)
    main()
    t1.join()
    t2.join()
    t3.join()

