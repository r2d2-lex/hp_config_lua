#!/usr/bin/env
import requests, json, sys
#import compago
#app = compago.Application()

session = requests.Session()
session.trust_env = False
url = "http://" + sys.argv[1]
urlLogin = "/htdocs/login/login.lua"
urlData = "/htdocs/pages/base/support.lsp"
urlLogout = "/htdocs/pages/main/logout.lsp"
urlFileTransfer = '/htdocs/pages/base/file_transfer.lsp'
username = sys.argv[3]
password = sys.argv[4]



#@app.command
def getFileTransfer():
    if login()==0:
        print("login failed")
    else:
        responseData = login()
        html = responseData.text
        noFindCPUStr = html.find('id="cpu_util_prog_bar_val">')
        noCPUStr = len('id="cpu_util_prog_bar_val">')
        cpu = responseData.text[noFindCPUStr + noCPUStr:(noFindCPUStr + noCPUStr + 2)]
        print(cpu)
    logout()

#@app.command
def getCPU():
    if login()==0:
        print("login failed")
    else:
        responseData = login()
        html = responseData.text
        noFindCPUStr = html.find('id="cpu_util_prog_bar_val">')
        noCPUStr = len('id="cpu_util_prog_bar_val">')
        cpu = responseData.text[noFindCPUStr + noCPUStr:(noFindCPUStr + noCPUStr + 2)]
        print(cpu)
    logout()


#@app.command
def getMem():
    if login()==0:
        print("login failed")
    else:
        responseData = login()
        html = responseData.text
        noFindMEMStr = html.find('id="mem_util_prog_bar_val">')
        noMEMStr = len('id="mem_util_prog_bar_val">')
        memory = responseData.text[noFindMEMStr + noMEMStr:(noFindMEMStr + noMEMStr + 2)]
        print(memory)
    logout()


def login():

    data = {'username':username,'password':password}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    responseLogin = session.post(url + urlLogin, data, headers)
    #print responseLogin.status_code
    if responseLogin.status_code == 200:
        #Logincookies = responseLogin.cookies
        #responseData = session.post(url + urlData, cookies = Logincookies)
        responseData = session.post(url + urlData)
        #html = responseData.text
        #print html
        return responseData
    else:
        return 0


def logout():
    session.post(url + urlLogout)
    #print logout.status_code
    session.close()


if __name__ == "__main__":
    #app.run()
    if sys.argv[2] == "getCPU":
        getCPU()
    elif sys.argv[2] == "getMem":
        getMem()
    else:
        print("Invalid argument! (script.py ip function)")
