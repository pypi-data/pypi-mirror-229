import time

class Saranphat:
    
    def __init__(self):
        self.name = 'Saranphat'
        self.lastname = 'Roungkitrakran'
        self.nickname = 'J'
        self.age = 25
        self.nationality = 'Thai'
        self.workplace = 'Kamiitasosei Co.LTD'
        self.liveplace = 'Maruyama Fujimino-Shi Saitama-Ken Japan'
        self.country = 'Thailand'
        self.account ='Gungungungundam'
    
    
    def WhatAmI(self):
        print('*********************************************************************************')
        time.sleep(0.5)
        print('My name is {} {}. And my nickname is {}. I am from {}. '.format(self.name , self.lastname , self.nickname ,self.country ))
        time.sleep(0.5)
        print('I live in {}. This year I am {} years old.' .format(self.liveplace , str(self.age)))
        time.sleep(0.5)
        print('I work in {}. Contract me by email {}.' .format(self.workplace , self.email))
        time.sleep(0.5)
        print('*********************************************************************************')
        
    @property    
    def email(self):
        return '{}@hotmail.com' .format(self.account)
    
    def thainame(self):
        print('นาย ศรัณย์ภัทร เรืองกิจตระการ')
        return 'นาย ศรัณย์ภัทร เรืองกิจตระการ'
        
    def japanname(self):
        print('ルンキッタカーン サランパット')
        return 'ルンキッタカーン サランパット'
      
    def __str__(self):
        return '*********************************************************************************\n This Saranphat module is for practice making python library \n *********************************************************************************'
        
if __name__ == '__main__':
    mystatus = Saranphat()
    print(mystatus)
    time.sleep(0.5)
    mystatus.thainame()
    time.sleep(0.5)
    mystatus.japanname()
    time.sleep(0.5)
    mystatus.WhatAmI()

