"""
好友闯关预告 python版本
其实现在已经实现一些功能了，我可以给你看看
"""

import urllib
import urllib.parse as parse
import urllib.request as request
import zipfile
import os, sys
import struct

data_path = '.\data'
HttpTableComPath = 'Com_TableCom_Android_Bin'
TableComFileName = 'TableComBin.zip'
TableComPath = 'TableCom'
grade = ['', 'D', 'C', 'B', 'A', 'S', 'SS', 'SSS']
diff = ['', '简单', '一般', '困难']
keys = ['', '4键', '5键', '6键']
eff = ['', '上隐', '下隐', '闪烁', '镜像']

def load_zip(): # 从官方服务器下载游戏数据
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    url = "http://game.ds.qq.com/" + HttpTableComPath + '/' + TableComFileName
    res = request.urlopen(url)
    filename = os.path.join(data_path, 'TableCom.zip')
    with open(filename, 'wb') as f:
        f.write(res.read())
    with zipfile.ZipFile(filename, 'r') as file_zip:
        file_zip.extractall(path=os.path.join(data_path, TableComPath))
        
class FileBuffer:
    
    def __init__(self, filename):
        self._file = filename
        self.open()
        
    def open(self):
        self.buffer = open(self._file, 'rb')
        
    def close(self):
        self.buffer.close()
        
    def readInt(self):
        return struct.unpack('i', self.buffer.read(4))[0]
        
    def readStr(self, length=64): #实际使用时，常用的长度是64，所以默认64了
        return bytes.decode(self.buffer.read(length)).rstrip('\0')
        # 游戏数据中，固定64位字符串，不足的后面就一串\0
        # 在cmd中看的会不爽，就像一堆空格
        
    def read(self, length=1):
        return self.buffer.read(length)
        
    def readShort(self):
        return struct.unpack('i', self.buffer.read(2)+b'\x00\x00')[0]
        
    # 暂时不需要读取浮点数，就不继续写了
    
        
class Map: # 好友闯关相关
    Data = {}
    
    @staticmethod
    def read_file():
        filename = os.path.join(data_path, TableComPath, 'mrock_Map_client.bin')
        try:
            f = FileBuffer(filename)
            f.read(193)
            for j in range(4):
                _d = {}
                for i in range(20):
                    d = {}
                    pr = ""
                    Id = f.readInt() #序号
                    MapId = f.readInt()#友闯序号
                    f.read(5)
                    d['LevelId'] = f.readInt()#关卡序号
                    d['NodeId'] = f.readInt()#过关条件
                    d['NodeValue'] = f.readInt()#过关条件参数
                    d['SongId'] = f.readInt()#歌曲ID
                    d['Difficulty'] = f.readInt()#难度
                    d['Keys'] = f.readInt()#键数
                    d['Value1'] = f.readInt()#？
                    d['Value2'] = f.readInt()#？
                    d['LevelRecord'] = f.readInt()#宝箱奖励
                    d['MiniVersion'] = f.readInt()#版本号
                    d['Effect'] = f.readInt() #特效
                    _d[Id]=d
                Map.Data[MapId]=_d
                    
        #print(Map.Data)
        finally:
            f.close()
    
    @staticmethod
    def getData():
        res = ''
        index = 0
        for i in Map.Data:
            _d = Map.Data[i]
            res += "友闯编号: " + str(i) + "\r\n\r\n"
            for j in _d:
                d = _d[j]
                pr = ''
                pr += "第"+str(d['LevelId'])+"关 "
                nodeTxt = d['NodeId']
                pr += Songs.Data[d['SongId']]['songName'] + ' '
                pr += keys[d['Keys']] + ' '
                pr += diff[d['Difficulty']] + ' '
                pr += Txt.getData(d['NodeId'], d['NodeValue']) + ' '
                pr += eff[d['Effect']] + ' '
                #print(pr)
                res += pr + '\r\n'
                index += 1
                if index % 20 == 0:
                    res += '\r\n'
        return res
            
                
class Songs: # 歌单文件
    Data = {}

    @staticmethod
    def read_file(level=False):
        if level == False:
            Songs.read_file(level=True)
            filename = os.path.join(data_path, TableComPath, 'mrock_song_client_android.bin')
        else:
            filename = os.path.join(data_path, TableComPath, 'mrock_songlevel_client.bin')
        try:
            f = FileBuffer(filename)
            f.read(8)
            size = f.readInt()
            num = f.readInt()
            f.read(120)
            for i in range(num):
                d = {}
                songId = f.readShort()
                d['iVersion'] = f.readInt()
                d['songName'] = f.readStr()
                d['songPath'] = f.readStr()
                d['songArtist'] = f.readStr()
                d['songComposer'] = f.readStr()
                # songTime = bytes.decode(f.read(64)).rstrip('\0') #越小，bpm越大
                # iGameTime = f.readInt()
                # iRegion = f.readInt()
                # iStyle = f.readInt()
                # isNew = f.readInt()
                # isHot = f.readInt()
                # isRecommend = f.readInt()
                f.read(568) # 这些数据暂时没用 ，就没读
                #print(songId, songName, songPath, songArtist)
                Songs.Data[songId]=d
            f.read()
        #print(Songs.Data)
        finally:
            f.close()
        
        
class Txt: # 过关条件
    Data = {}
    
    @staticmethod
    def read_file():
        filename = os.path.join(data_path, TableComPath, 'mrock_txt_client.bin')
        try:
            f = FileBuffer(filename)
            f.read(8)
            size = f.readInt()
            num = f.readInt()
            f.read(120)
            for _ in range(num):
                l = []
                Id = f.readInt()
                TxtString = f.readStr(256)
                Txt.Data[Id] = TxtString
        finally:
            f.close()
    
    @staticmethod    
    def getData(nodeId, nodeValue):
        nodeTxt = Txt.Data[nodeId]
        #print(nodeTxt)
        if '%s' in nodeTxt:
            return nodeTxt %(grade[nodeValue])
        elif '%d' in nodeTxt:
            return nodeTxt %(nodeValue)
        else:
            return nodeTxt
  
  
class Guide: #战队竞技歌曲
    Data = {}
    
    @staticmethod
    def read_file():
        filename = os.path.join(data_path, TableComPath, 'mrock_guild_song_client.bin')
        try:
            f = FileBuffer(filename)
            f.read(8)
            size = f.readInt()
            num = f.readInt()
            f.read(120)
            for _ in range(num):
                d = {}
                Id = f.readInt()
                d['SongId'] = f.readInt()
                d['Difficulty'] = f.readInt()
                d['Keys'] = f.readInt()
                d['NodeId'] = f.readInt()
                d['NodeValue'] = f.readInt()
                d['Effect'] = f.readInt()
                Guide.Data[Id] = d
        finally:
            f.close()
        
    @staticmethod
    def getData():
        res = ''
        for i in Guide.Data:
            d = Guide.Data[i]
            pr = ''
            pr += Songs.Data[d['SongId']]['songName'] + ' '
            pr += keys[d['Keys']] + ' '
            pr += diff[d['Difficulty']] + ' '
            pr += Txt.getData(d['NodeId'], d['NodeValue'])
            # if '%s' in Txt.Data[l[3]]:
                # pr += Txt.Data[l[3]] %(grade[l[4]]) + ' '
            # elif '%d' in Txt.Data[l[3]]:
                # pr += Txt.Data[l[3]] %(l[4]) + ' '
            # else:
                # pr += Txt.Data[l[3]] + ' '
            pr += eff[d['Effect']]
            res += pr + '\r\n'
        return res
     

class StarMall:
    
    Data = {}

    @staticmethod
    def read_file():
        filename = os.path.join(data_path, TableComPath, 'mrock_starmall_exchange_client.bin') 
        try:
            f = FileBuffer(filename)
            f.read(229)
            for i in range(4):
                _d = {}
                for j in range(6):
                    d = {}
                    Id = f.readInt()
                    StarId = f.readInt()
                    GoodId = f.readInt()
                    #f.read(5)
                    d['Type'] = f.read()
                    d['Value'] = f.readInt()
                    d['GoodName'] = f.readStr()
                    d['GoodValue'] = f.readInt()#限时人物天数/歌曲ID/道具数量
                    d['StarNum'] = f.readInt()
                    f.read(4)
                    #print(Id, StarId, GoodId, GoodName, GoodLimitDays, StarNum)
                    _d[GoodId] = d
                StarMall.Data[StarId] = _d
                
        finally:
            f.close()
            
    @staticmethod
    def getData():
        res = ""
        for i in StarMall.Data:
            res += "星值商店编号: " + str(i) + "\r\n\r\n"
            for j in StarMall.Data[i]:
                d = StarMall.Data[i][j]
                pr = ''
                pr += d['GoodName'] + ' '
                if d['Type'] == b'\x0a': #限时人物
                    pr += str(d['GoodValue']) + '天 '
                elif d['Type'] == b'\x05': #道具
                    pr += str(d['GoodValue']) + '个 '
                pr += '价格: ' + str(d['StarNum'])
                res += pr + '\r\n'
            res += '\r\n'
        return res        
        
def main_list():
    pr = ""
    pr += "1: 更新数据\n"
    pr += "2: 好友闯关预告\n"
    pr += "3: 战队竞技预告\n"
    pr += "4: 星值商店预告\n"
    pr += "0: 退出\n"
    print(pr)
    
def quit():
    i = input("退出?Y/N\n")
    while 1:
        if i.upper() == 'Y':
            sys.exit(0)
        elif i.lower() == 'N':
            return
        else:
            i = input("请输入Y或N\n")
            #print(i)
        
classes = [Map, Songs, Txt, Guide, StarMall]
# load_zip()
# for c in classes:
    # c.read_file()
# for c in [Map, Guide, StarMall]:
    # print(c.getData())
#print(Map.getData())

if __name__ == '__main__':
    os.system("cls")
    while 1:
        main_list()
        i = input("请输入序号\n")
        os.system("cls")
        if i == '1':
            load_zip()
            for c in classes:
                c.read_file()
        elif i == '2':
            print(Map.getData())
        elif i == '3':
            print(Guide.getData())
        elif i == '4':
            print(StarMall.getData())
        elif i == '0':
            quit()
        else:
            print("序号不合法，请重新输入")
            continue
        