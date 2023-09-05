#includes
import os
import time

def perimeter(a, b = "pass"): #perimeter периметр
    if b != "pass":
        try:
            return (a+b)*2
        except:
            return "FATAL ERROR"
    else:
        try:
            return a*4
        except:
            return "FATAL ERROR"

def square(a, b = "pass"): #square площадь
    if b != "pass":
        try:
            return a*b
        except:
            return "FATAL ERROR"
    else:
        try:
            return a*a
        except:
            return "FATAL ERROR"
        

def bif(condition, action, elaction = 'False', elifcondition = 'False', elifaction = 'False'): #if else elif action - дейтвие, condition - условие
    try:
        if eval(str(condition)):
            return eval(str(action))
        elif eval(str(elifcondition)):
            return eval(str(elifaction))
        else:
            return eval(str(elaction))
    except:
        return "FATAL ERROR if construction or library construction"
def bwhile(condition, action): #while action - дейтвие, condition - условие
    try:
        while eval(str(condition)):
            eval(str(action))
    except:
        return "FATAL ERROR while construction or library construction"
def bfor(condition, action, rangef): #for action - дейтвие, condition - условие
    try:
        #return "for"
        for condition in eval(str(rangef)): #eval(str(condition)):
            eval(str(action))
    except:
        return "FATAL ERROR for construction or library construction"
    
def bfile(filename, mode1 = 'r', mode2 = 'read', mode3 = '', encodingf = 'utf-8'):
    try:
        dekfjhyggchdjcnd = open(filename, mode1, encoding=encodingf)
        if mode3 == '':
            return eval("dekfjhyggchdjcnd." + mode2 + '(' + str(mode3) + ')')
            dekfjhyggchdjcnd.close()
        else:
            return eval("dekfjhyggchdjcnd." + mode2 + '("' + str(mode3) + '")')
            dekfjhyggchdjcnd.close()
    except:
        return "FATAL ERROR filewere construction or library construction"

def btime(timef, typef = 'sec'):
    try:
        if typef == 'sec':
            return eval(time.sleep(timef))
        elif typef == 'mlsec':
            return eval(time.sleep(timef/1000))
    except:
        return "FATAL ERROR time construction or library construction"

def bpause():
    try:
        return eval(os.system('pause'))
    except:
        return "FATAL ERROR pause construction or library construction"
    
def download(proceng = 101, shag = 0.1, pause = False, language = 'ru'):
    if language == 'ru':
        s='|'
        for i in range(proceng):
            time.sleep(shag)
            print('\r','Загруска: ',i*s,str(i),'%',end='')
        print ('')
        if pause == True:
            os.system('pause')
    elif language == 'en':
        s='|'
        for i in range(proceng):
            time.sleep(shag)
            print('\r','Download: ',i*s,str(i),'%',end='')
        print ('')
        if pause == True:
            os.system('pause')

#@
#r
#@
#r
#@
#r
#@
#r
#@
#r
#@

def register(count = 1, language = 'ru', downloadf = True):
    array_login = []
    array_password = []
    array_reg = []
    if language == 'ru':
        for i in range(count):
            login = str(input('Введите логин: '))
            password = str(input('Введите пароль: '))
            array_login.append(login)
            array_password.append(password)
        if downloadf == True:
            download()
        print('Регитрация успешно завершена.')
    elif language == 'en':
        for i in range(count):
            login = str(input('Enter the login: '))
            password = str(input('Enter the password: '))
            array_login.append(login)
            array_password.append(password)
        if downloadf == True:
            download(language = 'en')
        print('Registration completed successfully.')

    array_reg.append(array_login)
    array_reg.append(array_password)
    return array_reg



def login(logins, count = 1, language = 'ru', downloadf = True):
    array_login = logins[0]
    array_password = logins[1]
    
    array_loginf = []
    array_passwordf = []
    array_logins = []
    if language == 'ru':
        for i in range(count):
            login = str(input('Введите логин: '))
            password = str(input('Введите пароль: '))
            if login in array_login:
                passwordf = array_password[array_login.index(login)]
                if passwordf == password:
                    array_loginf.append(login)
                    array_passwordf.append(password)
                    print('Вход успешно завершен.')
                    print()
                else:
                    array_loginf.append('False')
                    array_passwordf.append('False')
                    print('Неправельный логин или пароль.')
                    print()
            else:
                array_loginf.append('False')
                array_passwordf.append('False')
                print('Неправельный логин или пароль.')
                print()

        array_logins.append(array_loginf)
        array_logins.append(array_passwordf)
        if downloadf == True:
            download()
        return array_logins
        
    #elif language == 'en':
    #    for i in range(count):
    #        login = str(input('Enter the login: '))
    #        password = str(input('Enter the password: '))
    #    if downloadf == True:
    #        download(language = 'en')
    #    print('Registration completed successfully.')

#@
#r
#@
#r
#@
#r
#@
#r
#@
#r
#@
