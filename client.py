import socket
import threading
import time
import cv2
import numpy as np
import array as ar
import matplotlib.pyplot as plt

def perspective(img):
    src=np.float32(
        [[2,349],
         [161,233],
         [478,233],
         [631,349]])
    dst=np.float32(
        [[115,480],
         [115,70],
         [525,70],
         [525,480]])
    img_size=(img.shape[1],img.shape[0])
    M=cv2.getPerspectiveTransform(src,dst)
    warped=cv2.warpPerspective(img,M,img_size)
    return warped

def threshold(img):
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    blur=cv2.GaussianBlur(gray,(5,5),0)
    a,thresh=cv2.threshold(blur,75,200,cv2.THRESH_BINARY)
    return thresh


def plotpid():
    plt.ion()
    t=0
    dss=25
    mdss=[]
    mt=[]
    dis=[]
    while True:
        global distance
        plt.clf()
        mt.append(t)
        mdss.append(dss)
        dis.append(distance)
        plt.plot(mt,dis,'-r')
        plt.plot(mt, mdss, '-b')
        plt.ylim(0,100)
        plt.pause(1)
        t=t+1
    plt.ioff()
    plt.show()


def PID(err,Ierr,derr):
    KP = 0.5
    KI = 0.12
    KD = 15
    out = KP*err + KI*(sum(Ierr)) + KD*derr
    if out > 50:
        out = 50
    if out < 0:
        out = 0
    return out

def A_PID(err,Ierr,derr):
    KP = 0.05
    KI = 0
    KD = 20
    err = err
    out = KP*err + KI*(sum(Ierr)) + KD*derr
    if out > 15:
        out = 15
    if out < -15:
        out = -15
    return out


def cal_distance(pixel_width):
    f = 510
    phone_width = 9
    distance = phone_width * f / pixel_width
    return distance

def cal_box(box):
    under_pix_x = box[0][0] - box[3][0]
    under_pix_y = box[0][1] - box[3][1]
    upper_pix_x = box[1][0] - box[2][0]
    upper_pix_y = box[1][1] - box[2][1]
    under_pix = np.sqrt(under_pix_x**2 + under_pix_y**2)
    upper_pix = np.sqrt(upper_pix_x ** 2 + upper_pix_y ** 2)
    return (under_pix+upper_pix)/2

def findline_edges(img, rangle):
    global Istruning
    Istruning = False
    if np.where(img[240,:]!=0) is not None:
        lowmaxv=max(max(np.where(img[240,:]!=0)),default=-1)
    else:
        lowmaxv=None
    if np.where(img[240,:]!=0) is not None:
        lowminv=min(max(np.where(img[240,:]!=0)),default=-1)
    else:
        lowminv=None
    # if np.where(img[190,:]!=0) is not None:
    #     upmaxv=max(max(np.where(img[190,:]!=0)),default=-1)
    # else:
    #     upmaxv=None
    # if np.where(img[190,:]!=0) is not None:
    #     upminv=min(max(np.where(img[190,:]!=0)),default=-1)
    # else:
    #     upminv=None

    #????????????
    if lowmaxv is None or  lowminv is None:
        averagev=320
    else:
        averagev=(lowminv+lowmaxv)/2
        deltaLine = (lowmaxv-lowminv)
    # cv2.circle(img, (int(averagev), 240), 5, (255, 255, 255), -1)
    # if averagev < 320:
    #     theta = (-1) * (np.arctan2((320 - averagev), 480)) #240
    # elif averagev >= 320:
    theta = (np.arctan2((averagev - 320), 480))
    theta = theta * 180 / np.pi
    if theta > 40:
        theta = 40
    elif theta < -40:
        theta = -40
    else:
        theta =theta

    # if lowmaxv is None or upmaxv is None :
    #     rightangle=90
    # else:
    #     x=upmaxv-lowmaxv
    #     if x == 0:
    #         rightangle=90
    #     else:
    #         rightangle=np.arctan2(80,x)*180/np.pi
    #
    # if  lowminv is None or upminv is None:
    #     leftangle = 90
    # else:
    #     x = upminv - lowminv
    #     if x == 0:
    #         leftangle =90
    #     else:
    #         leftangle = np.arctan2(80, x)*180/np.pi
    # roadangle=(rightangle+leftangle)/2
    # rangle=90-roadangle
    # allangle=rangle*3/5+theta*2/5
    allangle = theta
    # print('?????????=',allangle)
    # print('theta=',theta)
    # print('rightangle=',rightangle)
    # print('leftangle=',leftangle)
    if deltaLine<400:
        if rangle >0 and averagev >350:
            allangle=allangle
            # print("1")
        elif rangle <0 and averagev <290:
            allangle=allangle
            # print("2")
        elif rangle >0 and averagev >290 and averagev<350:
            allangle=20
            # print("3")
            Istruning = True
        elif rangle <0 and averagev >290 and averagev<350:
            allangle=-20
            # print("4")
            Istruning = True
        else:
            allangle = allangle*(-1)
            # print("5")
    # print("allangle ",allangle)
    return allangle





def findMarker (image):
    #??????
    angle = 0
    persvideo = perspective(image)
    # gray = cv2.cvtColor(persvideo, cv2.COLOR_BGR2GRAY)
    persvideo[(persvideo < 5)] = 200
    blur = cv2.GaussianBlur(persvideo,(5,5),0)
    a, thresh=cv2.threshold(blur,100,250,cv2.THRESH_BINARY)
    t_s = time.time()
    # thpersvideo=threshold(persvideo)
    th_Canny = cv2.Canny(thresh, 5, 90)
    cv2.imshow('Canny', th_Canny)
    p = np.where(th_Canny > 230)
    x = p[1]
    y = p[0]*-1
    print(len(p[0]))
    print(len(p[0])!=0)
    if  len(p[0])!=0:
        zzz = np.zeros_like(th_Canny)
        A = np.matrix.transpose(np.array([x, np.ones(x.size)]))
        B = np.matrix.transpose(np.array([y]))

        A_transpose = np.matrix.transpose(A)
        A_square = np.dot(A_transpose, A)
        A_square_inverse = np.linalg.inv(A_square)
        X_matrix = np.dot(np.dot(A_square_inverse, A_transpose), B)

        m = X_matrix[0]
        t_e = time.time()
        # print("time",t_e - t_s)
        # print("m",m)
        angle=findline_edges(th_Canny ,m)

    # cv2.line(th_Canny, (320, 0), (320, 480), (255, 192, 203), 2)
    #
    # # cv2.line(img, (0, 190), (640, 190), (255, 255, 255), 2)
    # cv2.line(th_Canny, (0, 240), (640, 240), (255, 192, 203), 2)


    # cv2.imshow('persvideo',persvideo)
    # cv2.imshow('thresh', thresh)
    findcube = image[0:300,0:640]
    #?????????
    cube, thresh_c = cv2.threshold(findcube, 60, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh_c, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # cv2.imshow('cube',thresh_c)

    if contours:
        cnt_max = max ( contours, key = cv2.contourArea )
        rect = cv2.minAreaRect(cnt_max)
        box = np.int0(cv2.boxPoints(rect))
        cv2.drawContours(findcube, [box], 0, (0, 255, 0), 2)
        # findcube = cv2.cvtColor(findcube, cv2.COLOR_GRAY2RGB)
        # cv2.imshow('pers', thpersvideo)
        pixel_width = cal_box(box)
        D = cal_distance(pixel_width)
        if D is None:
            D = 0
    else:
        D=0
    cv2.imshow('drawcont', findcube)
    return [D, angle]




def recv(sock, addr):
    '''
    ??????UDP?????????????????????????????????????????????????????????
    ???????????????send???????????????win????????????
    '''
    sock.sendto(name.encode('utf-8'), addr)
    # while True:
        # data = sock.recv(1024)


def send(sock, addr):
    '''
        ?????????????????????
        ?????????
            sock????????????????????????socket??????
            server?????????????????????IP??????
    '''
    global backVoltage
    global frontAngle
    global Istruning
    while True:
        # string = input('')
        # message = name + ' : ' + string
        # messagelist = string.split(',')
        try:

            # # print(frontAngle-45)
            # turn = abs(frontAngle-45)
            #
            # if turn >20:
            #     backVoltage = 45
            #     print("1111111")
            #
            # elif turn >10:
            #     backVoltage = 35
            #     print("2222222")
            #
            # else:
            #     backVoltage = 30
            #     print("3333333")


            # backVoltage = 30 + abs(frontAngle-45)
            # if backVoltage < 30:
            #     backVoltage = 30
            # if backVoltage >40:
            #     backVoltage = 40




            # if (frontAngle-45)>20:
            #     backVoltage = 50
            # else:
            #     backVoltage = 30
            # if abs(frontAngle-40) < 10:
            #     backVoltage = 30
            # else:
            #     backVoltage = 30
            A = ar.array('h',[int(backVoltage),int(frontAngle)])
            # A = ar.array('h', [int(0), int(0)])
            memA=memoryview(A)
            # data = message.encode('utf-8')
            sock.sendto(memA, addr)
            # print('angle=', frontAngle)
            time.sleep(0.1)
        except:
            continue
        # sock.send(pickle.dumps(A))
        # if string.lower() == 'EXIT'.lower():
        #     break

def main():
    '''
        ?????????????????????????????????????????????????????????????????????????????????
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ('192.168.50.5', 9999)
    tr = threading.Thread(target=recv, args=(s, server), daemon=True)
    ts = threading.Thread(target=send, args=(s, server))
    tr.start()
    ts.start()
    tr.join()
    ts.join()
    s.close()


def ReceiveVideo():
    global backVoltage
    global frontAngle
    global distance,plot_t
#distance pid ??????
    err = 0
    Ierr = [0,0,0]
    preerr = 0
    derr = 0
    essential_distance = 25
#angle pid ??????
    A_err = 0
    A_Ierr = [0, 0, 0]
    A_preerr = 0
    A_derr = 0


    print('recieve go')
    # IP??????'0.0.0.0'????????????????????????
    address = ('192.168.50.5', 8002)
    # ??????socket????????????????????????https://blog.csdn.net/rebelqsp/article/details/22109925
    # socket.AF_INET??????????????????????????????
    # socket.SOCK_STREAM?????????socket,for TCP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # ???????????????????????????,???AF_INET???,????????????host,port????????????????????????.
    s.bind(address)
    # ????????????TCP??????????????????????????????????????????????????????????????????????????????????????????????????????????????????1??????????????????????????????5???????????????
    s.listen(1)

    def recvall(sock, count):
        buf = b''  # buf?????????byte??????
        while count:
            # ??????TCP???????????????????????????????????????????????????count?????????????????????????????????.
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf

    # ??????TCP??????????????????conn,address???,??????conn???????????????????????????????????????????????????????????????addr??????????????????????????????
    # ??????????????????????????????
    conn, addr = s.accept()
    print('connect from:' + str(addr))
    # plt.ion()
    # plt.figure(1)
    t=[]
    dis=[]
    motorangle=45
    angle = 45
    while 1:
        start = time.time()  # ????????????????????????
        length = recvall(conn, 16)  # ???????????????????????????,16??????????????????
        # try:
        stringData = recvall(conn, int(length))  # ????????????????????????????????????????????????
        data = np.frombuffer(stringData, np.uint8)  # ???????????????????????????????????????1?????????
        decimg = cv2.imdecode(data, cv2.IMREAD_UNCHANGED)  # ????????????????????????
        wData = findMarker(decimg)
        distance = wData[0]
        angle = wData[1]

        # except Exception as e:
        #     print(e)
        #     pass

        plot_t=start
        err = distance - essential_distance
        Ierr.pop(0)
        Ierr.append(err)
        derr = err - preerr
        preerr=err
        PID_out = PID(err,Ierr,derr)

        A_err = angle
        A_Ierr.pop(0)
        A_Ierr.append(A_err)
        A_derr = A_err - A_preerr
        A_preerr=A_err
        A_PID_out = A_PID(A_err,A_Ierr,A_derr)
        # print("PID angle", A_PID_out)
        frontAngle = angle+45 #motorangle+A_PID_out
        turnEdge = 30
        if frontAngle >=45+turnEdge:
            frontAngle=45+turnEdge
        elif frontAngle <=45-turnEdge:
            frontAngle=45-turnEdge
        else:
            frontAngle=frontAngle

        motorangle=frontAngle
        # print("angle", (angle))

        backVoltage = PID_out * (100/50)
        # cv2.imshow('SERVER', decimg)  # ????????????
        # ?????????????????????
        # ???
        # ???
        # ???

        # ???????????????????????????????????????????????????????????????
        end = time.time()
        seconds = end - start
        if seconds == 0:
            fps=0
        # else:
            # print("deltaTime = ",seconds)
        # conn.send(bytes(str(int(fps)), encoding='utf-8'))
        k = cv2.waitKey(10) & 0xff
        if k == 27:
            break
    s.close()
    cv2.destroyAllWindows()









if __name__ == '__main__':
    distance = 0
    backVoltage = 0
    frontAngle = 0
    Istruning = False
    plot_t=0
    print("-----?????????????????????,????????????????????????'EXIT(???????????????)'-----")
    name = 'Kuo'
    print('-----------------%s------------------' % name)
    tvideo = threading.Thread(target=ReceiveVideo)
    tvideo.start()
    main()
    # tplot = threading.Thread(target=plotpid)
    # tplot.start()
    # tmain = threading.Thread(target=main)
    # tmain.start()
    # main()
    tvideo.join()
    # tplot.join()
    # tmain.join()

