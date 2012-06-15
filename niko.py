import serial
import time
from parser import *
import sys
import thread
import os
import threading
import cherrypy
import signal

class CRC_CCITT:
   def __init__(self):
      self.tab=256*[[]]
      for i in xrange(256):
         crc=0
         c = i << 8

         for j in xrange(8):
            if (crc ^ c) & 0x8000:
               crc = ( crc << 1) ^ 0x1021
            else:
                  crc = crc << 1

            c = c << 1

            crc = crc & 0xffff

         self.tab[i]=crc
   
   def update_crc(self, crc, c):
      short_c=0x00ff & (c % 256)

      tmp = ((crc >> 8) ^ short_c) & 0xffff
      crc = (((crc << 8) ^ self.tab[tmp])) & 0xffff

      return crc
      
      
   def convertToAsccii(self,s):
      tempstr=""
      i=0
      while i+1 < len(s):
         tempstr+=   chr(int(   str(s[i])+str(s[i+1]),16))
         i+=2
      return tempstr;
    
   def calculate_crc_from_hex(self,s):
      tempstr=self.convertToAsccii(s)
      crcval=0xffff
      for c in tempstr:
         crcval=self.update_crc(crcval, ord(c))
      return '%04x' %crcval;      
      

#test=CRC_CCITT()
#print str(test.calculate_crc_from_hex('12DA04'))

serialLock=threading.Lock()
if os.name=='nt':
  ser = serial.Serial('COM5', timeout=1, writeTimeout=1,interCharTimeout =1,xonxoff=True,baudrate=9600)
else:
  ser = serial.Serial('/dev/ttyUSB0', timeout=1, writeTimeout=1,xonxoff=True,baudrate=9600)


#print "     name: "+ser.name
#print " baudrate: "+str(ser.baudrate)
#print "   parity: "+ser.parity
#print " stopbits: "+str(ser.stopbits)
#print "  xonxoff: "+str(ser.xonxoff)
#print " bytesize: "+str(ser.bytesize)

#exit()
time.sleep(3)
ser.write("++++\r")
ser.write("ATH0\r")
ser.write("ATZ\r")
ser.write("$10110000B8CF9D\r")
ser.flush()
line=ser.read(5)
print line


time.sleep(1)
ser.write("$1012DA045BF7D6\r")
ser.flush()
time.sleep(1)
line=ser.read(5)
print line

ser.write("$1012DA045BF7D6\r")
ser.flush()
time.sleep(1)
line=ser.read(5)
print line
line=ser.read(30)
print line

#time.sleep(1)
#ser.write("$1E15DA04FF00000000FFFF5CC18E\r")
#ser.flush()
#line=ser.read(20)
#print line



def CreateZetOutputCommand(uitgangen,eerste6,module,crc_byte_3):
  moduleid=module.getConvertedAdres()
  if eerste6:
     command='15'+moduleid
  else:
     command='16'+moduleid
  for uitgang in uitgangen:
    if uitgang==True:
      command+='FF'
    else:
      command+='00'
  command+='FF'  
  test=CRC_CCITT()

  command= '$1E'+command+str(test.calculate_crc_from_hex(command))+crc_byte_3+'\r'
  return command.upper();
  
def LeesModule(module,eerste6,crc_byte3='00'):
   moduleid=module.getConvertedAdres()
   cmd=""
   if eerste6:
      cmd+='12'
      j=0
   else:
      cmd+='17'
      j=6
   cmd+=moduleid
   test=CRC_CCITT()
   cmd='$10'+cmd+str(test.calculate_crc_from_hex(cmd))+crc_byte_3+'\r'
   cmd=cmd.upper()
   serialLock.acquire()
   line=ser.read(30)
   ser.write(cmd)
   ser.flush()
   time.sleep(1)
   line=ser.read(30)
   serialLock.release()
   if len(line)<10 or line.find('$1')==-1:
      print 'failed: '+ line
      return None
   else:
      line=line[line.find('$1'):]
      uitgangen=[]
      for i in range(9,21,2):
         if line[i].upper()=='0':
            uitgangen.append(False)
            module.getUitgang(j).Zet(False)
         else:
            uitgangen.append(True)
            module.getUitgang(j).Zet(True)
         j+=1
      return uitgangen
      
#print 'check LeesModule'
moduleid='DA04'
crc_byte_3='D9'
#modules=['DA04','EE11','5A05']
for module in  plaatsen.listModules():
 moduleid=module.getConvertedAdres()
# print 'uitlezen module: '+ module.getCode()+' '+module.getNaam()+' ('+moduleid+')'
 uitgangen=LeesModule(module,True)
 if (not uitgangen is None):
  i=1
  for uitgang in uitgangen:
#    print 'Uitgang: '+str(i)+' Status: ' +str(uitgang)+' '+module.getStandUitgang(i-1)  + ' '+str(module.getUitgang(i-1))
    i+=1
 else:
  print 'crc problem'
 crc_byte_3='B6'
 uitgangen=LeesModule(module,False)
 if (not uitgangen is None):
  for uitgang in uitgangen:
#    print 'Uitgang: '+str(i)+' Status: '+str(uitgang)+' '+module.getStandUitgang(i-1) + ' '+str(module.getUitgang(i-1)) 
    i+=1
 else:
  print 'crc problem'
 
"""
module=plaatsen.listModules()[0]
crc_byte_3='01'
uitgangen=[True,True,False,False,False,False]
k=0
for k in range (64):
  #for l in range(6):
  #  uitgangen[l]=((k&(1<<l))!=0)
  #print uitgangen

# $1E15DA04FF0000000000FF5F3E01.
#print '---'
  cmd= str(CreateZetOutputCommand(uitgangen,module,crc_byte_3))
  print cmd
  ser.write(cmd)
  ser.flush()
  uitgangen2=LeesModule(module,True,'00')

  if (uitgangen != uitgangen2):
    print 'FAILED: '+str(uitgangen) +' '+str(uitgangen2)
  #else:
  #  print 'SUCCESS: '+str(uitgangen) +' '+str(uitgangen2)
exit()





  
  

def ListenThread(mystring,*args):
  while (True):
    s = sys.stdin.readline()
    if not s:
      break
    print "Sending: "+s
    #ser.write('#NA537DF\r')
    ser.write(s.rstrip()+'\r')
    ser.write(s.rstrip()+'\r')
    ser.write(s.rstrip()+'\r')
    ser.write(s.rstrip()+'\r')
    ser.flush()
    ser.write("#L0\r#E1\r")
    ser.flush()

thread.start_new_thread(ListenThread,("",""))

while (False):
  time.sleep(1)
  print("AAN")
  ser.write('#N3A50F7\r')
  ser.write('#N3A50F7\r')
  ser.flush()
  time.sleep(1)
  print ("UIT")
  ser.write('#N7A50F7\r')
  ser.write('#N7A50F7\r')
  
ser.flush()  
ser.write("#L0\r#E1\r")  
print
print
"""
class ListenThread ( threading.Thread ):
 def run ( self ):
  print "Listenthread started"
  while (True):
    serialLock.acquire()
#    ser.flush()
    starttime=time.strftime("%a, %d %b %Y %H:%M:%S")
    line=ser.readline()
    serialLock.release()
    if (len(line)>0):
      print starttime
      print time.strftime("%a, %d %b %Y %H:%M:%S")
      lines=line.splitlines()
      previousknop=0   
      for line in lines:   
        line=line.rstrip()
        print line
        knop=plaatsen.verifyCommand(line)
        if knop==0:
          print ("UNKOWN")
        if knop!=previousknop:
          print knop
          if (knop.getCommand('A')==line):
            print "Knop A ingedrukt"
          if (knop.getCommand('B')==line):
            print "Knop B ingedrukt"
          if (knop.getCommand('C')==line):
            print "Knop C ingedrukt"
          if (knop.getCommand('D')==line):
            print "Knop D ingedrukt"

          previousknop=knop

#ListenThread().start()

    



