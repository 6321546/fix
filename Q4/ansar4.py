import os
import re
import datetime as dt
import ipaddress as ip
import typing as tp

LogPattern = re.compile("(\d{4})(0[1-9]|1[0-2])([0-2][0-9]|3[0-1])(0[0-9]|1[0-9]|2[0-3])([0-5][0-9])([0-5][0-9]),(\d+.\d+.\d+.\d+/\d+),(\d+|-)") #日/月/年:時:分:秒,アドレス/マスク,ping

AddPattern = re.compile('((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])/[1-30]')


#path = 'log' #ファイル名

#ansar4



class Server:
    def __init__(self,ad,N):
        self.addres = ad #アドレス
        self.sTime = [] #故障開始時間のリスト
        self.eTime = [] #故障終了時間のリスト
        self.count = 0 #タイムアウトの連続回数
        self.N = N #閾値
        self.state = False #故障状態かどうかを表す T:故障 F:正常


#self.countを進める
    def addcount(self):
        if self.count <= self.N:
            self.count += 1

#self.countを0にリセットする
    def resetcount(self):
        self.count = 0


# 故障状態かどうか判定し、時間の記録を行う
    def isBreak(self,time):
        if self.count == self.N:
        #故障開始時の処理
            if self.state is False:
                self.sTime.append(time) # 直前の状態が正常状態なら記録を行う

            self.state = True

        elif self.count == 0:
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


class SubNetwork:
    def __init__(self,nw,N):
        self.network = nw #ネットワーク
        self.sTime = [] #故障開始時間のリスト
        self.eTime = [] #故障終了時間のリスト
        self.state = False #故障状態かどうか T:故障  F:正常
        self.servers = [] #従属サーバーのリスト

#self.serversに新たなserverを加える
    def addserver(self, server:tp.Type[Server]):
        self.servers.append(server)
        
        #初期化
        self.state = False
        self.sTime = []
        self.eTime = []
        #if len(self.sTime) == len(self.eTime):
        #    del self.sTime[-1]


#引数のアドレスを持つ従属サーバーがあればそのインデックスを返す。
    def isServer(self,addres):
        for i in range(len(self.servers)):
            if addres == self.servers[i].addres:
                return i

        return ''


#ネットワークが落ちているかどうかを判断し、開始時間と終了時間の記録を行う
    def isNetDown(self, time):
        allstate = True #全てのサーバが故障しているかどうかを表す。 T:全て故障 F:正常なサーバが１つ以上ある
        #正常なサーバーがあるか探す
        for server in self.servers:
            if server.count < server.N:
                allstate = False

        #print(time)
        #print(self.network)
        #for server in self.servers:
        #    print('ad: ' + server.addres + ' | count: ' + str(server.count))
        #print(allstate)

        if allstate:
        #ネットワークが落ちている時の処理
            if self.state is False:
                self.sTime.append(time) # 直前の状態が正常だったら記録
                self.state = True
        else:
        #ネットワークが落ちていない時の処理
            if self.state is True:
                self.eTime.append(time) # 直前の状態が故障なら記録
                self.state = False



#記録した時間を報告する関数
    def ReportTime(self):
        print('NW: ' + str(self.network))
        for i in range(len(self.sTime)):
            if len(self.eTime) > i:
                #終了時間がある場合
                print('[' +str(self.sTime[i])  + '] - [' + str(self.eTime[i]) + ']')
            else:
                #終了時間がない場合
                print('[' + str(self.sTime[i]) + '] -')
    pass




#実行関数
def ReportBreakNet(path,N):
    nets = [] #ネットワークのリスト
    looksv = '' #見るサーバーを表す
    looknet = '' #見るサーバーを表す

    with open(path, 'r') as f:
        for line in f.readlines():
            logdata = LogPattern.search(line)

            if logdata is not None: # 空行への配慮
                looknet = '' #初期化
                lyear, lmonth, lday, lhour, lminutu, lsecond, addres, ping = logdata.groups() # 抽出
                if AddPattern.search(addres) is not None: #アドレスが正常なら実行する
                    time = dt.datetime(year=int(lyear), month=int(lmonth), day=int(lday), hour=int(lhour), minute=int(lminutu), second=int(lsecond))

                    nw = ip.ip_network(addres,False) # ネットワーク取得

                    #netsにすでに同じネットワークがあるか探す
                    for i in range(len(nets)):
                        if nw == nets[i].network:
                            looknet = i

                    #netsに同じネットワークがない時、netsに新しいネットワークの追加を行う
                    if looknet == '':
                        #print('add: ' + addres)
                        looknet = len(nets)
                        nets.append(SubNetwork(nw,N))

                    looksv = nets[looknet].isServer(addres)

                    #serversに同じアドレスを持つサーバーがないときに追加を行う
                    if looksv == '':
                        #print('add: ' + addres)
                        looksv = len(nets[looknet].servers)
                        nets[looknet].addserver(Server(addres,N))


                    if ping == '-': 
                    #タイムアウト時の処理
                        nets[looknet].servers[looksv].addcount()
                    else:
                    #非タイムアウト時の処理
                        nets[looknet].servers[looksv].resetcount()

                    nets[looknet].servers[looksv].isBreak(time)
                    nets[looknet].isNetDown(time)


    for net in nets:
        net.ReportTime()
        #for server in net.servers:
        #    server.ReportTime()


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
    N = input('故障とみなす回数(N)を入力してくだい: ') #標準入力用
    if N.isdigit() and is_integer(N) and int(N) > 0: 
        break
    else:
        print('数値を入力してくだい(1以上の整数)')


ReportBreakNet(name,int(N))
