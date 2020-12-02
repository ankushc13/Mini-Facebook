import socket
import sys
from Tkinter import *
from pprint import pprint
import csv
from cStringIO import StringIO
import simplejson as json
from collections import defaultdict
from PIL import ImageTk, Image
import os
import numpy
from tkFileDialog import askopenfile
import pickle


def sendNow(packet,addr):
    f=StringIO(packet)
    ft=f.read(1024)
    while True:
        s.sendto(ft, addr)
        ft=f.read(1024)
        if not ft:
            break
    s.sendto(b'',addr)

def rcvNow(buffer):
    d = s.recvfrom(buffer)
    addr = d[1]
    data =''
    while True:
        data=data+d[0]
        d = s.recvfrom(buffer)
        if not d[0]:
            break
    
    return data,addr


# HOST = '10.0.0.4'
HOST=sys.argv[1]
PORT = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, PORT))
class Users:
    def __init__(self,username,password,first,last,perAddr,tempAddr,friends,dp,friRqst,post):
        self.username=username
        self.password=password
        self.first=first
        self.last=last
        self.perAddr = perAddr
        self.tempAddr = tempAddr
        self.friends=friends
        self.friRqst=friRqst
        self.dp=dp
        self.post=post


user_list = []
try:
    with open('register.json', 'r') as openfile: 
        # Reading from json file 
        json_object = json.load(openfile)
        for user in json_object:    
            user_profile = Users(user,json_object[user]['password'],json_object[user]['first'],
            json_object[user]['last'],json_object[user]['peraddr'],json_object[user]['tempaddr'],
            json_object[user]['friends'],json_object[user]['dp'],json_object[user]['friRqst'],
            json_object[user]['post'])

            print(json_object[user]['friRqst'])
            user_list.append(user_profile)
except:
    print("File Not Exist")



connected_users = []


while(1):

    reply,addr=rcvNow(1024)
    msg=reply[2:]
    id=reply[0:2]
    id1=id
    print id
    if '00'==id:
        id1='01'
        msg=""
    elif '02'==id:
        for i,user in enumerate(user_list):
            if user.username==msg:
                user_list[i].tempAddr=addr[0]
                id1='03'
                msg=""
                break
        else:
            id1='WU'
            msg=""

    elif '04'==id:
        for j,user in enumerate(user_list):
            if user.password==msg and user.tempAddr==addr[0]:
                user_list[j].perAddr=addr[0]
                connected_users.append(addr[0])
                id1='05'
                msg=""
                break
        else:
            id1='WP'
            msg=""

    elif '06'==id:
        msg=msg.split(',')
        info=defaultdict()
        if ( msg[1]) and ( msg[2]) and ( msg[3]):
            info[msg[0]]={  "password": msg[1],
                            "first" : msg[2],
                            "last"  :msg[3],
                            "peraddr":"",
                            "tempaddr":"",
                            "friends":[],
                            "friRqst":[],
                            "dp":"default.jpeg",
                            "post":[]
            }
            try :
                with open('register.json') as json_file: 
                    data = json.load(json_file)
                    if msg[0] in data:
                        id1='29'
                    else:
                        id1='07'
                        data.update(info)
                json_file.close()
                
            except:
                data=info
            
            with open('register.json','w') as f: 
                json.dump(data, f, indent=4)
                f.close()

        else:
            print(msg)
            id1='27'
        msg=''
    elif id == 'LG':
      for i, user in enumerate(user_list):
        if user.perAddr == addr[0]:
          user_list[i].tempAddr = ''
          user_list[i].perAddr = ''
          connected_users[connected_users.index(addr[0])] = ''
          id1 = '09'
    elif id=='08':
        id1='11'
        info=defaultdict()
        for j,user in enumerate(user_list):
            for i in connected_users:
                if user.perAddr==i and msg in user.friends:
                    info[user.username]={
                        "first" : user.first,
                        "last"  :user.last,
                        "status" : "Online"
                    }
                    break
            else:
                if msg in user.friends:
                    info[user.username]={
                            "first" : user.first,
                            "last"  :user.last,
                            "status" : "Offline"
                    }


        info=json.dumps(info)
        msg=info




    elif id=='18':
        id1='13'
        info=defaultdict()
        for user in user_list:
            
            info[user.username]={
                            "first" : user.first,
                            "last"  :user.last,
                            "friRqst":user.friRqst}



        info=json.dumps(info)
        print(json.loads(info))
        msg=info
    
    elif id=='26':
        id1='17'
        for user in user_list:
            if user.username==msg:
                img=Image.open(user.dp)
                n_img=(numpy.array(img)).tolist()
                msg=pickle.dumps(n_img)
                break

    elif id=='20':
        d_msg=msg.split("<<seprator>>")
        print(d_msg[0])
        n_img=pickle.loads(d_msg[1])
        print type(n_img)
        n_img=numpy.array(n_img)
        n_img = Image.fromarray(n_img.astype('uint8'))
        n_img.save((d_msg[0]+"dp.png"),"png")

        for i, user in enumerate(user_list):
            if user.username==d_msg[0]:
                user_list[i].dp=d_msg[0]+"dp.png"
                with open('register.json') as json_file: 
                    data = json.load(json_file)
                    data[d_msg[0]]["dp"]=d_msg[0]+"dp.png"
                json_file.close()
                with open('register.json','w') as f: 
                    json.dump(data, f, indent=4)
                f.close()
        id1='11'
        msg=json.dumps(defaultdict())
    
    elif id=='16':
        d_msg=msg.split("<<seprator>>")
        for i, user in enumerate(user_list):
            if user.username==d_msg[1] and (d_msg[0] not in user_list[i].friRqst):
                user_list[i].friRqst.append(d_msg[0])
                with open('register.json') as json_file: 
                    data = json.load(json_file)
                    data[d_msg[1]]["friRqst"].append(d_msg[0])
                json_file.close()
                print(data)
                with open('register.json','w') as f: 
                    json.dump(data, f, indent=4)
                f.close()
        id1='11'
        msg=json.dumps(defaultdict())
        print(msg)

    elif id=='22':
        d_msg=msg.split("<<seprator>>")
        for i, user in enumerate(user_list):
            if user.username==d_msg[0]:
                user_list[i].friRqst.remove(d_msg[1])
                user_list[i].friends.append(d_msg[1])
                with open('register.json') as json_file: 
                    data = json.load(json_file)
                    data[d_msg[0]]["friends"].append(d_msg[1])
                    data[d_msg[0]]["friRqst"].remove(d_msg[1])
                json_file.close()
                with open('register.json','w') as f: 
                    json.dump(data, f, indent=4)
                f.close()
            
            elif user.username==d_msg[1]:
                user_list[i].friends.append(d_msg[0])
                with open('register.json') as json_file: 
                    data = json.load(json_file)
                    data[d_msg[1]]["friends"].append(d_msg[0])
                json_file.close()
                print(data)
                with open('register.json','w') as f: 
                    json.dump(data, f, indent=4)
                f.close()


        id1='11'
        msg=json.dumps(defaultdict())


    elif id == '24':
        d_msg=msg.split("<<seprator>>")
        for i, user in enumerate(user_list):
            if user.username==d_msg[0]:
                user_list[i].friRqst.remove(d_msg[1])
                with open('register.json') as json_file: 
                    data = json.load(json_file)
                    data[d_msg[0]]["friRqst"].remove(d_msg[1])
                json_file.close()
                print(data)
                with open('register.json','w') as f: 
                    json.dump(data, f, indent=4)
                f.close()
        id1='11'
        msg="ankush"
    elif id=='14':
        d_msg=msg.split("<<seprator>>")
        for i, user in enumerate(user_list):
            if user.username==d_msg[0]:
                user_list[i].friends.remove(d_msg[1])
                with open('register.json') as json_file: 
                    data = json.load(json_file)
                    data[d_msg[0]]["friends"].remove(d_msg[1])
                json_file.close()
                print(data)
                with open('register.json','w') as f: 
                    json.dump(data, f, indent=4)
                f.close()
            elif user.username==d_msg[1]:
                user_list[i].friends.remove(d_msg[0])
                with open('register.json') as json_file: 
                    data = json.load(json_file)
                    data[d_msg[1]]["friends"].remove(d_msg[0])
                json_file.close()
                with open('register.json','w') as f: 
                    json.dump(data, f, indent=4)
                f.close()

        id1='11'
        msg=json.dumps(defaultdict())

    elif id=='10':
        id1='15'
        msg=json.dumps(defaultdict())

    elif id=='28':
        id1='19'
        for i, user in enumerate(user_list):
            if user.username==msg:
                lent=len(user_list[i].post)
                post=pickle.dumps(user_list[i].post)
                msg=str(lent)+"<<seprator>>"+post


    elif id=='30':
        id1='21'
        d_msg=msg.split("<<seprator>>")
        for i, user in enumerate(user_list):
            if user.username==d_msg[0] and d_msg[2]!='':
                n_img=pickle.loads(d_msg[2])
                n_img=numpy.array(n_img)
                n_img = Image.fromarray(n_img.astype('uint8'))
                if not os.path.exists(os.path.join("post",d_msg[0])):
                    os.makedirs(os.path.join("post",d_msg[0]))
                n_img.save(os.path.join("post",d_msg[0],(d_msg[0]+str(len(user_list[i].post)+1)+"post.png")),"png")
                user_list[i].post.append([d_msg[1],os.path.join("post",d_msg[0],(d_msg[0]+str(len(user_list[i].post)+1)+"post.png"))])
                with open('register.json') as json_file:
                    data = json.load(json_file)
                    data[d_msg[0]]["post"].insert(0,[d_msg[1],os.path.join("post",d_msg[0],(d_msg[0]+str(len(user_list[i].post))+"post.png"))])
                json_file.close()

                with open('register.json','w') as f: 
                    json.dump(data, f, indent=4)
                f.close()



        msg=""
                
    elif id=='32':
        id1='23'
        d_msg=pickle.loads(msg)
        print(d_msg)
        img=Image.open(d_msg)
        n_img=(numpy.array(img)).tolist()
        msg=pickle.dumps(n_img)


    elif id=='12':
        id1='25'
        msg=''
    

    
    packet=id1+msg
    sendNow(packet,addr)
