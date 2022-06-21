import os
import re
import datetime as dt

LogPattern = re.compile("(\d{4})(0[1-9]|1[0-2])([0-2][0-9]|3[0-1])(0[0-9]|1[0-9]|2[0-3])([0-5][0-9])([0-5][0-9]),(\d+.\d+.\d+.\d+/\d+),(\d+|-)") #日/月/年:時:分:秒,アドレス/マスク,ping

AddPattern = re.compile('((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])/[1-30]')


#path = 'log' #ファイル名


#ansar1
class Server:
    def __init__(self,ad):
        self.addres = ad #アドレス
        self.sTime = [] #故障開始時間のリスト
        self.eTime = [] #故障終了時間のリスト
        self.state = False #故障状態かどうかを表す T:故障 F:正常
        self.count = 0 #タイムアウトの連続回数


#self.countを進める
    def addcount(self):
        self.count = 1

#self.countを0にリセットする
    def resetcount(self):
        self.count = 0


# 故障状態かどうか判定し、時間の記録を行う
    def isBreak(self,time):
        if self.count == 1:
        #故障開始時の処理
            if self.state is False:
                self.sTime.append(time) # 直前の状態が正常状態なら記録を行う
                self.state = True
        else:
        #正常時の処理
            if self.state is True:
                self.eTime.append(time) # 直前の状態が故障状態なら記録を行う
                self.state = False


#記録した時間を報告する関数
    def ReportTime(self):
        print(self.addres)
        for i in range(len(self.sTime)):
            if len(self.eTime) > i:
                #終了時間がある場合
                print('[' +str(self.sTime[i])  + '] - [' + str(self.eTime[i]) + ']')
            else:
                #終了時間がない場合
                print('[' + str(self.sTime[i]) + '] -')
    pass



#実行関数
def ReportTimeOutServer(path):
    servers = [] #サーバーのリスト
    looksv = '' #見るサーバーを表す

    with open(path, 'r') as f:
        for line in f.readlines():
            logdata = LogPattern.search(line)

            if logdata is not None: # 空行への配慮
                looksv = '' #初期化
                lyear, lmonth, lday, lhour, lminutu, lsecond, addres, ping = logdata.groups() # 抽出
                if AddPattern.search(addres) is not None: #アドレスが正常なら実行する
                    time = dt.datetime(year=int(lyear), month=int(lmonth), day=int(lday), hour=int(lhour), minute=int(lminutu), second=int(lsecond))

                    #serversにすでに同じアドレスを持つサーバーを探す。
                    for i in range(len(servers)):
                        if addres == servers[i].addres:
                            looksv = i

                    #serversに同じアドレスを持つサーバーがないときに追加を行う
                    if looksv == '':
                        #print('add: ' + addres)
                        looksv = len(servers)
                        servers.append(Server(addres))

                    if ping == '-': 
                        servers[looksv].addcount()
                    else:
                        servers[looksv].resetcount()

                    servers[looksv].isBreak(time)

    for server in servers:
        server.ReportTime()

# 少数でないかの判定
def is_integer(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()



while True:
    name = input('ファイル名を入力してくだい: ') #標準入力用
    if os.path.exists(name):
        break
    else:
        print('ファイルが存在しません')


ReportTimeOutServer(name)
