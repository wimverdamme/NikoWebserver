from niko import *
import cherrypy
class Webserver(object):
   def CSS(self):
     return"""
<style type="text/css">
[class=AAN]{background-color:yellow;}
[class=UIT] {background-color:RoyalBlue ;}
</style>     
     """

   def index(self):
      ret="""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
</head>
<body>
<a href="ModuleView">Modules</a> 
</body>
</html>
    
        
        """
      return ret

   index.exposed = True
   
   def ModuleView(self,Refresh="",Module="",Uitgang=""):
      if Module != "":
         for module in plaatsen.listModules():
           uitgang=-1
           try:
             uitgang=int(Uitgang)
           except:
             pass
           if module.getAdres()==Module and uitgang>-1 and uitgang <12:
             module.getUitgang(uitgang).Switch()
             eerste6 = (uitgang<6)
             uitgangen=[False,False,False,False,False,False]
             if eerste6:
               for i in range(6):
                  uitgangen[i]=module.getUitgang(i).getStand()
             else:
               for i in range(6):
                  uitgangen[i]=module.getUitgang(i+6).getStand()
                
             cmd=CreateZetOutputCommand(uitgangen,eerste6,module,'00')
             serialLock.acquire()
             ser.write(cmd)
             ser.flush()
             serialLock.release()
             Refresh="RELOAD"
             break
      if Refresh=="RELOAD":
         for module in  plaatsen.listModules():
	  moduleid=module.getConvertedAdres()
	  uitgangen=LeesModule(module,True)

      ret="""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
"""+self.CSS()+"""
</head>
<body>
<h1>Nikobus - Schakelmodules:</h1>
"""
      for module in  plaatsen.listModules():
         ret+= "<h2>"+module.getCode()+' '+module.getNaam()+' ('+module.getConvertedAdres()+')'+"</h2>"
         ret+= '<table border="1">'         
         for i in range(12):
            ret+='<tr><td>'+str(module.getUitgang(i))+'</td>'
            if module.getStandUitgang(i)=="AAN":            
               ret+='<td class=AAN><a href="ModuleView?Module='+module.getAdres()+'&Uitgang='+str(i)+'">'+str(module.getStandUitgang(i))
            else:
               ret+='<td class=UIT><a href="ModuleView?Module='+module.getAdres()+'&Uitgang='+str(i)+'">'+str(module.getStandUitgang(i))
            ret+='</a></td></tr>'
         ret+='</table> '

      ret+="""
<form name="input" action="ModuleView" method="post">
<input type="submit" value="RELOAD" name="Refresh" />
</form>       
</body>
</html>
     
        
        """
         
      return ret
        
   ModuleView.exposed=True

cherrypy.config.update({'server.socket_host': '0.0.0.0'})
cherrypy.config.update({'server.socket_port': 8888})
cherrypy.quickstart(Webserver())
