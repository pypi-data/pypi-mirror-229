class Package(object):
    
     def __init__(self): #,instance="Instance Name"):
         self._id = id(self)
         self._name="Package"
         self._desc="Package for test builds"
         self._vers="v0.01.08" 
         self._model = "" 
         self._about="About package class"
         self._instance_name = ""
         self._debug_flag = False
       
     def whoami(self):
          print(self._name,self._vers,self._model)
         
     def name(self):
          print(self._name)
         
     def vers(self):
          return self._vers
         
       
