import os
import re
import datetime as dt

LogPattern = re.compile("(\d{4})(0[1-9]|1[0-2])([0-2][0-9]|3[0-1])(0[0-9]|1[0-9]|2[0-3])([0-5][0-9])([0-5][0-9]),(\d+.\d+.\d+.\d+/\d+),(\d+|-)") #日/月/年:時:分:秒,アドレス/マスク,ping

AddPattern = re.compile('((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])/[1-30]')


#path = 'log1' #ファイル名
TimeOut = 4000

#ansar3
class Server:
    def __init__(self, ad, m, t):
        self.addres = ad #アドレス
        self.sTime = [] #故障開始時間のリスト
        self.eTime = [] #故障終了時間のリスト
        self.count = 0 #タイムアウトの連続回数
        self.state = False #故障状態かどうかを表す T:故障 F:正常
        self.M = m #計算する直近回数
        self.T = t #平均応答時間の閾値
        self.PingMemory = [0] * self.M #ping値のリスト
        self.index = 0 #self.PingMemoryのインデックス

#self.PingMemoryにping値を追加
    def addping(self,ping):
        self.PingMemory[self.index] = int(ping)
        self.next()
        if self.count < self.M:
            self.count += 1

#self.indexを進める
    def next(self):
        self.index += 1
        if self.index > self.M-1:
            self.index -= self.M

#self.countを初期化
    def resetcount(self):
        self.count = 0


# 直近M回のpingの平均を出す。直近がM回未満なら記録してある分の平均を出す。
    def averageping(self):
        if self.count < self.M:
            return sum(self.PingMemory)/self.count
        else:
            return sum(self.PingMemory)/self.M



# 過負荷状態かどうか判定し、時間の記録を行う
    def isOver(self,time):
        if self.averageping() > self.T:
        #平均応答時間がtを超えた場合の処理
            if self.state is False:
                self.sTime.append(time) #直前の状態が正常状態なら記録を行う
                self.state = True
        else:
            if self.state is True:
                self.eTime.append(time) # 直前の状態が過負荷状態なら記録を行う。
                self.state = False
        #print(self.state)
        #return self.state
        #print(self.PingMemory)
        #print(self.averageping())


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





def ReportOverServer(path,m,t):
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
                        servers.append(Server(addres, m, t))

                    if ping == '-': 
                        ping = TimeOut

                    servers[looksv].addping(ping)
                    servers[looksv].isOver(time)

    for server in servers:
        server.ReportTime()

#実行関数
#path = input('ファイル名を入力してくだい: ') #標準入力用
#m = input('見たい直近の回数を入力してくだい: ') #標準入力用
#t = input('平均応答時間の閾値を入力してくだい: ') #標準入力用

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


while True:
    m = input('見る直近の回数(m)を入力してくだい: ') #標準入力用
    if m.isdigit() and is_integer(m) and int(m) > 0: 
        break
    else:
        print('数値を入力してくだい(1以上の整数)')

while True:
    t = input('閾値(t)を入力してくだい: ') #標準入力用
    if t.isdigit() and is_integer(t) and int(t) > 0: 
        break
    else:
        print('数値を入力してくだい(1以上の整数)')


ReportOverServer(name,int(m),int(t))
