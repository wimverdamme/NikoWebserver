
def parse_error(linenr,comment):
  print ("Parse Error line: "+str(linenr))
  print ("Comment: "+comment)
  print ("Exit...")
  exit()
  
class Onderdeel:
  def __init__(self, naam, adres, code):
    self.naam=naam
    self.adres=adres
    self.code=code
  def getNaam(self):
    return self.naam
  def getCode(self):
    return self.code
  def getAdres(self):
    return self.adres
  def __str__( self ):
    return self.__class__.__name__.upper()+': '+self.naam+ " /// Adres: "+self.adres + " /// Code: "+self.code 

class Busdrukknop(Onderdeel):
  def __init__(self, line):
    adres=""

    code=line[:line.find(":")]
    
    naam=line[line.find(":")+1:line.find("(",line.find(":")+1)]        
    adres=line[line.rindex(' '):]

    self.modes=[]
    
    Onderdeel.__init__(self, naam, adres, code)
    
  def getCommand(self,knop):
    i=int (self.adres,16)
    b1=bin(i)
    b1=b1[2:]
    b2=''.join([b1[i] for i in range(len(b1)-1,-1,-1)])
    if knop=='A':
      prefix='10'
    if knop=='B':
      prefix='11'
    if knop=='C':
      prefix='00'
    if knop=='D':
      prefix='01'
    b3='0b'+prefix+b2
    i=int (b3,2)
    h=hex(i)[2:]
    while len(h)<6:
      h='0'+h
    command="#N"+h
    return command.upper()

  def verifyCommand(self,command):
    ret=0
    if (self.getCommand('A')==command) or (self.getCommand('B')==command) or (self.getCommand('C')==command) or (self.getCommand('D')==command):
      ret = self
    #print "---"+command+ "-"+self.getCommand('A')+"-"
    return ret

  def __str__( self ):
    ret=""
    ret = self.__class__.__name__.upper()+': '+self.naam+ " /// Adres: "+self.adres + " /// Code: "+self.code 
    for mode in self.modes:
       ret = ret+ "\n      "+str(mode)
    return ret
    
  def addMode(self,mode):
    self.modes.append(mode)
class Uitgang:
  def __init__(self, naam):
    self.naam=naam
    self.stand=False
  def ZetAan(self):
    self.stand=True
  def ZetUit(self):
    self.stand=False
  def Zet(self,waarde):
    self.stand=waarde
  def Switch(self):
    self.stand = (not self.stand)
      
  def getStand(self):
    return self.stand
  
      
  def __str__( self ):
    return self.naam

class Schakelmodule(Onderdeel):
  def __init__(self, line):
    naam=line[line.find(":")+1:line.rfind("(")]        
    adres=line[line.rindex(' '):]
    code=line[:line.find(":")]
    Onderdeel.__init__(self, naam, adres, code)
    self.uitgangen=[]

  def addUitgang(self,naam,nr):  
    if int(nr[1:])-1==len(self.uitgangen):
      self.uitgangen.append(Uitgang(naam))

  def __str__( self ):
    ret = "SCHAKELMODULE: "+self.naam
    for uitgang in self.uitgangen:
      ret= ret+'\n'+"     UITGANG: "+ str(uitgang)
    return ret

  def getUitgang(self,index):
    return self.uitgangen[index]
    
  def getStandUitgang(self,index):
    if self.uitgangen[index].getStand()==True:
      return 'AAN'
    else:
      return 'UIT'    
    
  def getConvertedAdres(self):  
    adres=self.getAdres()
    adres=adres.strip()
    converted_Adres=adres[len(adres)-2:]
    if len(adres.strip())<4:
      converted_Adres+='0'
    converted_Adres+=adres[:len(adres)-2]
    return converted_Adres
  
  
    

  
    
class Generieke_bedieningspunten(Onderdeel):
  def __init__(self, line):
    naam=line[line.find(":")+1:line.find("(",line.find(":")+1)]        
    adres=line[line.rindex(' '):]
    code=line[:line.find(":")]
    Onderdeel.__init__(self, naam, adres, code)  
    
class Feedback_Module(Onderdeel):
  def __init__(self, line):
    naam=line[line.find(":")+1:line.find("(",line.find(":")+1)]        
    adres=line[line.rindex(' '):]
    code=line[:line.find(":")]
    Onderdeel.__init__(self, naam, adres, code)      
    
    
def OnderdeelFactory(line):
  if (line.find("Busdrukknop")!=-1):
    return Busdrukknop(line)
  if (line.find("Schakelmodule")!=-1):
    return Schakelmodule(line)
  if (line.find("Generieke bedieningspunten")!=-1):
    return Generieke_bedieningspunten(line)
  if (line.find("Feedback Module")!=-1):
    return Feedback_Module(line)
    
class Plaats:
  def __init__(self, naam):
    self.naam=naam
    self.onderdelen=[]
    
  def __str__( self ):
    ret= 'PLAATS: '+self.naam
    for onderdeel in self.onderdelen:
      ret=ret+'\n   '+str(onderdeel)
    return ret
    
  def addOnderdeel(self,onderdeel):
    self.onderdelen.append(onderdeel)

  def addMode(self,knop,mode):
    for onderdeel in self.onderdelen:
      if isinstance(onderdeel, Busdrukknop):
        if onderdeel.getCode()==knop:
          onderdeel.addMode(mode)  

  def addUitgang(self,module,naam,nr):
    for onderdeel in self.onderdelen:
      if isinstance(onderdeel, Schakelmodule):          
        if onderdeel.getCode()==module:
          onderdeel.addUitgang(naam,nr)  
   
  def verifyCommand(self,command):    
    ret=0
    for onderdeel in self.onderdelen:
      if isinstance(onderdeel, Busdrukknop):
        ret=onderdeel.verifyCommand(command)
        if (ret!=0):
          return ret
    return ret
  
  def listModules(self):
    modules=[]
    for onderdeel in self.onderdelen:
      if isinstance(onderdeel, Schakelmodule):
        modules.append(onderdeel)
    return modules


class Mode:
  def __init__(self, mtype,knoppen,uitgang,bedientijd=0,afvaltijd=0):
    self.mtype=mtype
    self.knoppen=knoppen #'AB','A',B',CD',C',D'
    self.uitgang=uitgang
    self.bedientijd=bedientijd
    self.afvaltijd=afvaltijd
  def __str__( self ):
    return "Uitgang: "+self.uitgang+" Mode: "+self.mtype+" Knoppen: "+self.knoppen+" bedientijd(sec): "+str(self.bedientijd)+" afvaltijd(sec): "+str(self.afvaltijd)

class Plaatsen:
  def __init__(self):
    self.plaatsen=[]

  def append(self,plaats):
    self.plaatsen.append(plaats)

  def addMode(self,knop,mode):
    for plaats in self.plaatsen:
      plaats.addMode(knop,mode)
  
  def addUitgang(self,module,naam,nr):
    for plaats in self.plaatsen:
      plaats.addUitgang(module,naam,nr)
    
  def __str__( self ):
    ret=""
    for plaats in self.plaatsen:
      ret=ret+"\n"+str(plaats)
    return ret

  def verifyCommand(self,command):    
    ret=0
    for plaats in self.plaatsen:
      ret=plaats.verifyCommand(command)
      if (ret!=0):
        return ret
    return ret

  def listModules(self):
    modules=[]
    for plaats in self.plaatsen:
      modules.extend(plaats.listModules())
    return modules

f=open('installatie.txt','r')

templines=f.readlines()
lines=[]

for line in templines:
  if (not line.startswith("Nikobus database")):
    lines.append(line.rstrip())
if (len(lines)>0):
  i=0    
  while (i<len(lines) and lines[i]!="3. Plaatsen"):
    i=i+1
    
  i=i+2
  if (i>=len(lines)):
    parse_error(i,"'3. Plaatsen' not found.")
    
  plaatsen=Plaatsen()
  while (i<len(lines) and  lines[i]!="4. Inputgroepen"):
    plaatsnaam=lines[i]
    plaats=Plaats(plaatsnaam)
    i=i+1
    onderdelen=[]
    while (i<len(lines) and  (lines[i].find("Schakelmodule")!=-1 or lines[i].find("Busdrukknop")!=-1 or lines[i].find("Generieke bedieningspunten")!=-1 or lines[i].find("Feedback Module")!=-1)): 
      onderdeel=OnderdeelFactory(lines[i])
      plaats.addOnderdeel(onderdeel)
      i=i+1
    
    plaatsen.append( plaats)
  while (i<len(lines) and  lines[i]!="6. Sensoren"):
    i=i+1
  i=i+1

  while (i<len(lines) and  lines[i][:5].find(":")!=-1 and lines[i].startswith("BP")):
    #lees knop lijn
    knoplijn=lines[i][:lines[i].find(":")]
    i=i+1
    while lines[i].endswith("Ingang"):
      inganglijn=lines[i][:lines[i].find(":")]
      i=i+1
      while lines[i].startswith("O") and lines[i][3]==":":
        uitgang=lines[i][:lines[i].find(":")]
        i=i+1
        modelijn=lines[i][18:21]
        i=i+1
        if modelijn.find("M02")!=-1 or modelijn.find("M03")!=-1:
          bedientijd=lines[i][13:lines[i].rfind(" ")]
          bedientijd=int(bedientijd)
          i=i+1   
        else:
          bedientijd=0
        if modelijn.find("M06")!=-1:
          afvaltijd=int(lines[i][25:lines[i].rfind(" ")])*60
          i=i+1
        else:
          afvaltijd=0 
        voorwaardelijn=lines[i]      
        i=i+1
        mode=Mode(modelijn,knoplijn,uitgang,bedientijd,afvaltijd)
        plaatsen.addMode(knoplijn,mode)

  i=i+1
  while (i<len(lines) and  lines[i][:5].find(":")!=-1 and lines[i].startswith("S")):
    module=lines[i][:lines[i].find(":")]
    i=i+1
    while lines[i].startswith("O") and lines[i][3]==":":
#      print lines[i]      
      naam=lines[i][lines[i].find(":")+2:]
      nr=lines[i][:lines[i].find(":")]
#      print Uitgang
      plaatsen.addUitgang(module,naam,nr)
      i=i+1
      while not lines[i].startswith("O") and not lines[i].startswith("S") and not lines[i]=="8. Interfaces":
        i=i+1
      

    
#  print str(plaatsen)  
  #for plaats in  Plaatsen:    
  #  print "Plaats: "+str(plaats)
    
  #print
  #testknop=Busdrukknop("BP35: Busdrukknop, 4 bedieningspunten - Trap/Bureau onderaan (05-064 : Busdrukknop, 4 bedieningspunten) 3E74CC")
  #print str(testknop)
  #print testknop.getCommand('A')
  #print testknop.getCommand('B')
  #print testknop.getCommand('C')
  #print testknop.getCommand('D')
  #print testknop.getCode()

  

  
  
    
  
    
  
  
