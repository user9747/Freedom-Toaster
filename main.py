from flask import Flask,render_template,request,redirect,url_for
from flask import *

import os
from glob import iglob
from subprocess import Popen, PIPE
import time
import signal
from decimal import Decimal, localcontext, ROUND_DOWN

delim = " - "
endOption = "x" + delim + "Exit program"
optionString = "Enter Your Option : "
sureString = "Are you sure (Y/n) : "
invalidString = "Invalid option entered, Please Enter a valid option\n"
DEVICE = "/dev/null"
yes = ['YES', 'y', 'Y', 'yes', '']
device=""
dd = ""

app = Flask(__name__)


def printList(isoList):
    count = 0
    for iso in isoList:
        count += 1
        print(str(count) + delim + os.path.basename(iso))
    print()
    print(endOption)


def getIsos():
    isoList = []
    count = 1
    for filename in iglob("**/*.iso", recursive=True):
        isoList.append(filename)
        count += 1
    return isoList

def createBootable(fileName, device):
        print("Format Device")
        Popen(['umount', device], stderr=PIPE)
        os.system('mkfs.fat -I '+device)
        global fileSize
        fileSize = getSize(fileName)
        global dd
        dd = Popen(['dd'] + ['if='+fileName, 'of='+device],
                   stderr=PIPE, stdout=PIPE)
        os.system('clear')
        dd.send_signal(signal.SIGUSR1)
        print("kazhinju")
        return
       


# def updateProgress(progress, copyText):
#     print("\r"+copyText, end="", flush=True)


def truncFloat(floatNumber):
    with localcontext() as context:
        context.rounding = ROUND_DOWN
        return Decimal(floatNumber).quantize(Decimal('0.01'))


def getSize(fileName):
    file = open(fileName, 'rb')
    file.seek(0, 2)
    size = file.tell()
    return int(size)


def clearScreen():
    os.system('clear')


def readOption(myList):
    return render_template("read.html")
@app.route('/')
def getFile():
    isoList = getIsos()
    # printList(isoList)
    count=0
    optionList = []
    # for iso in isoList:
    #     count += 1
    #     print(iso)
    #     optionList.append(str(count) + delim + os.path.basename(iso))
    #     print(str(count) + delim + os.path.basename(iso))

    # optionList = list(range(1, len(isoList)+1))
    usbList = []
    usbRaw = os.popen('lsblk | grep -v sda').read()
    count = 1
    print("Select your device from the following list \n")
    print("\t"+usbRaw.splitlines()[0])
    for line in usbRaw.splitlines()[1:]:
        usbList.append(line)

    return render_template("index.html",distros=isoList,usbs=usbList)


@app.route('/write',methods=['GET', 'POST'])
def write():
    line = request.form['usbOption']
    device = line.split(" ", 1)[0]
    if("─" in device):
        device = device.split("─", 1)[1]
    print(device)
    createBootable(request.form['isoOption'],'/dev/'+device )
    return render_template("progress.html")

@app.route('/progress')
def progress():
    def generate():
        print("2")
        progress = 0
        while dd.poll() is None:
            time.sleep(.3)
            print("1")
            dd.send_signal(signal.SIGUSR1)
            while (progress*100)< 100:
                time.sleep(.3)
                dd.send_signal(signal.SIGUSR1)
                print("2")
                l = dd.stderr.readline()
                print(bytes(l))
                if b'bytes' in l:
                    done = int(l[:l.index(b'bytes')-1])
                    print(done)
                    print(fileSize)
                    if(fileSize != 0):
                        print("4")
                        progress = done/fileSize
                        progress = truncFloat(progress)
                        print(progress)
                    yield "data:" + str(progress*100) + "\n\n"
                    time.sleep(0.5)
            break
    return Response(generate(),mimetype='text/event-stream') 



if __name__ == "__main__":
    app.run()
