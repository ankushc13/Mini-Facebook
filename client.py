import socket   #for sockets
import sys  #for exit
import getpass
from functools import partial
import tkMessageBox
import simplejson as json
import collections
from cStringIO import StringIO
from PIL import ImageTk, Image
import os
import pickle
import numpy

from tkFileDialog import askopenfile

def sendNow(packet,addr,buffer=1024):
    f=StringIO(packet)
    ft=f.read(buffer)
    while True:
        s.sendto(ft, addr)
        ft=f.read(buffer)
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


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
# host = '10.0.0.4'
host=sys.argv[1]
port = 8888



init='00'

sendNow(init,(host, port))



def convert(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return data


import Tkinter as tk     # python 2
import tkFont as tkfont  # python 2

class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.username=""
        self.profileUser=""
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.status='offline'
        self.frames = {}
        for F in (StartPage, Login, Register,MainPage,otherPage):
            frame = F(container,self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.run()

    def run(self):
        reply,addr=rcvNow(1024)
        id=reply[0:2]
        msg=reply[2:]
        if id=='01':
            self.show_frame(StartPage)

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.event_generate("<<ShowFrame>>")
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Mini Facebook", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(self, text="Login",
                            command=lambda: controller.show_frame(Login))
        button2 = tk.Button(self, text="Register",
                            command=lambda: controller.show_frame(Register))
        button1.pack()
        button2.pack()


class Login(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.user=""
        self.passw=""
        label = tk.Label(self, text="Login", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        usernameLabel = tk.Label(self, text="User Name").pack()
        username = tk.StringVar()
        usernameEntry = tk.Entry(self, textvariable=username).pack()
        
        passwordLabel = tk.Label(self,text="Password").pack()
        password = tk.StringVar()
        passwordEntry = tk.Entry(self, textvariable=password, show='*').pack()
        validateLogin = partial(self.validateLogin, username, password)
        loginButton = tk.Button(self, text="Login", command=validateLogin).pack()
        button = tk.Button(self, text="Back",
                           command=lambda : self.controller.show_frame(StartPage))
        button.pack()
        
    def validateLogin(self,username, password):
        self.user=username.get()
        self.controller.username=self.user
        id1='02'
        packet=id1+self.user

        sendNow(packet,(host, port))
        reply,addr=rcvNow(1024)
        
        id=reply[0:2]
        msg=reply[2:]
        if id=='03':
            self.passw=password.get()
            id1='04'
            packet=id1+self.passw
            sendNow(packet,(host, port))
            reply,addr=rcvNow(1024)
            id=reply[0:2]
            msg=reply[2:]
            if id == 'WP':
                tkMessageBox.showinfo("info",'Wrong Password')
            elif id =='05':
                print "success"
                self.controller.status='online'
                self.controller.show_frame(MainPage)

        elif id =='WU':
            tkMessageBox.showinfo("info",'Username not found')
            
        return 

class Register(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Register", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)



        usernameLabel = tk.Label(self, text="User Name").pack()
        username = tk.StringVar()
        usernameEntry = tk.Entry(self, textvariable=username).pack()
        
        firstnameLabel = tk.Label(self, text="First Name").pack()
        firstname = tk.StringVar()
        firstnameEntry = tk.Entry(self, textvariable=firstname).pack()

        lastnameLabel = tk.Label(self, text="Last Name").pack()
        lastname = tk.StringVar()
        lastnameEntry = tk.Entry(self, textvariable=lastname).pack()


        passwordLabel = tk.Label(self,text="Password").pack()
        password = tk.StringVar()
        passwordEntry = tk.Entry(self, textvariable=password, show='*').pack()

        Enter=partial(self.Enter,username,firstname,lastname,password)
        button = tk.Button(self, text="Enter",
                           command=Enter)
        button.pack()
        button = tk.Button(self, text="Back",
                           command=lambda : self.controller.show_frame(StartPage))
        button.pack()


    def Enter(self,username,firstname,lastname,password):
        msg=''
        id1='06'
        msg=username.get()+','+password.get()+','+firstname.get()+','+lastname.get()
        packet=id1+msg
        sendNow(packet,(host, port))
        reply,addr=rcvNow(1024)
        id=reply[0:2]
        msg=reply[2:]
        if id=='07':
            tkMessageBox.showinfo("info",'You are successfully registered')
            self.controller.show_frame(StartPage)
        elif id=='27':
            tkMessageBox.showinfo("Error",' Please fill required fields')
        elif id=='29':
            tkMessageBox.showinfo("Info",'Username already exist')
        


class MainPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.post=[]
        self.bind("<<ShowFrame>>", self.chat)
        title = tk.Label(self, text="My Profile")
        title.pack(side="top", fill="x", pady=10)
        self.f1 = tk.Frame(self, background='#98AFC7',width=500)
        self.f1.pack(side=tk.LEFT, expand=False, fill="both")
        self.f1.pack_propagate(0)
        self.f6 = tk.Frame(self.f1 ,background='white')
        self.f6.pack(side=tk.TOP, expand=False,fill="both")
        self.f7 = tk.Frame(self.f1 ,background='#98AFC7')
        self.f7.pack(side=tk.TOP, expand=False,fill="both")
        self.f8 = tk.Frame(self.f1 ,background='#98AFC7')
        self.f8.pack(side=tk.TOP, expand=False,fill="both")

        self.f2 = tk.Frame(self, background='#C0C0C0')
        self.f2.pack(side=tk.LEFT, expand=True, fill="both")
        self.f9 = tk.Frame(self.f2, background='white')
        self.f9.pack(side=tk.TOP, expand=False, fill="both")
        self.f10 = tk.Frame(self.f2, background='#98AFC7')
        self.f10.pack(side=tk.TOP, expand=False, fill="both")
        self.f3 = tk.Frame(self ,background='white',width=500)
        self.f3.pack(side=tk.LEFT, expand=False,fill="both")
        self.f3.pack_propagate(0)
        self.f4 = tk.Frame(self.f3 ,background='white')
        self.f4.pack(side=tk.TOP, expand=False,fill="both")
        self.f5 = tk.Frame(self.f3 ,background='#98AFC7')
        self.f5.pack(side=tk.TOP, expand=False,fill="both")
        
        validateLogout = partial(self.validateLogout)
        button = tk.Button(self.f8, text="Logout",
                            command=validateLogout)
        button.pack(side=tk.BOTTOM)

        label4 = tk.Label(self.f9, text="Create Post")
        label4.pack(side="top", fill="x", pady=10)
        statusLabel = tk.Label(self.f9, text="Status").pack()
        status = tk.StringVar()
        statusEntry = tk.Entry(self.f9, textvariable=status).pack()
        add = partial(self.add)
        button_add= tk.Button(self.f9, text="Add Image",command=add
                            ).pack(side=tk.RIGHT)
        post=partial(self.postNow,status)
        button_post = tk.Button(self.f9, text="Post",command=post
                            ).pack(side=tk.BOTTOM)

    def popup(self,i):
        bt=self.buttons[i]
        self.popup_menu = tk.Menu(self, 
                                       tearoff = 0) 
        
        self.popup_menu.add_command(label = "Profile", 
                                    command = lambda:self.task(bt['text'],id='10')) 
        self.popup_menu.add_separator()
        self.popup_menu.add_command(label = "Send Message", 
                                    command = lambda:self.task(bt['text'],id='12')) 
        self.popup_menu.add_separator() 
        self.popup_menu.add_command(label = "Remove Friend", 
                                    command = lambda:self.task(bt['text'],id='14')) 
        self.popupm(bt)
    def popupm(self,bt):
        try:         
            self.popup_menu.tk_popup(bt.winfo_rootx(), bt.winfo_rooty(), 0)
        finally:
            self.popup_menu.grab_release()

        
        
    def chat(self,event):
        self.event=event
        msg=self.controller.username
        id1='08'
        packet=id1+msg
        sendNow(packet,(host, port))
        reply,addr=rcvNow(1024)
        
        id=reply[0:2]
        msg=reply[2:]
        data=json.loads(msg)
        

        # # data=convert(data)
        label = tk.Label(self.f4, text="Friends")
        label.pack(side="top", fill="x", pady=10)
        text = tk.Text(self.f4, wrap="none")
        vsb = tk.Scrollbar(self.f4,orient="vertical", command=text.yview)
        text.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        text.pack(side="right",fill="both", expand=True)
        self.buttons = list()
        for user in data:
            if user!=self.controller.username:
                self.buttons.append(tk.Button(self.f4, text=user +' ('+data[user]['status']+')',height = 1, width = 15))
                popup=partial(self.popup,len(self.buttons)-1)
                self.buttons[-1].configure(command = popup)

                text.window_create("end", window=self.buttons[-1])
                text.insert("end", "\n")

        text.configure(state="disabled")
        id1='18'
        packet=id1+self.controller.username
        sendNow(packet,(host, port))
        reply,addr=rcvNow(1024)
        
        id=reply[0:2]
        msg=reply[2:]
        print(type(msg))
        data1=json.loads(msg)
        # data1=convert(data1)
        label1 = tk.Label(self.f5, text="Registred Users")
        label1.pack(side="top", fill="x", pady=10)
        text1 = tk.Text(self.f5, wrap="none")
        vsb1 = tk.Scrollbar(self.f5,orient="vertical", command=text1.yview)
        text1.configure(yscrollcommand=vsb1.set)
        vsb1.pack(side="right", fill="y")
        text1.pack(side="right",fill="both", expand=True)
        self.buttons1 = list()
        for user in data1:
            if user!=self.controller.username:
                self.buttons1.append(tk.Button(self.f5, text=user,height = 1, width = 15))
                cpopup=partial(self.cpopup,len(self.buttons1)-1)
                self.buttons1[-1].configure(command = cpopup)

                text1.window_create("end", window=self.buttons1[-1])
                text1.insert("end", "\n")

        text1.configure(state="disabled")

        id1='26'
        packet=id1+self.controller.username
        sendNow(packet,(host, port))
        reply,addr=rcvNow(1024)
        id=reply[0:2]
        msg=reply[2:]
        n_img=pickle.loads(msg)
        n_img=numpy.array(n_img)
        print n_img.shape,type(n_img)
        n_img = Image.fromarray(n_img.astype('uint8'))
        # n_img.save(("ankush10"),"png")
        self.img = ImageTk.PhotoImage(n_img)
        self.panel = tk.Label(self.f6, image = self.img)
        self.panel.photo=self.img
        self.panel.pack(side = tk.TOP, fill = "both", expand = "no")

        changeDp = partial(self.changeDp)
        cbutton = tk.Button(self.f6, text="Change Profile Picture",
                            command=changeDp)
        cbutton.pack(side=tk.TOP,pady=10)


        label3 = tk.Label(self.f6, text="Username : "+self.controller.username)
        label3.pack(side="top", fill="x", pady=10)
        label4 = tk.Label(self.f6, text="Name : "+data1[self.controller.username]["first"]+" "+data1[self.controller.username]["last"])
        label4.pack(side="top", fill="x", pady=10)
        #FriendRequest
        label2 = tk.Label(self.f7, text="Friend Request")
        label2.pack(side="top", fill="x", pady=10)
        text2 = tk.Text(self.f7, wrap="none")
        vsb2 = tk.Scrollbar(self.f7,orient="vertical", command=text2.yview)
        text2.configure(yscrollcommand=vsb2.set)
        vsb2.pack(side="right", fill="y")
        text2.pack(side="right",fill="both", expand=True)
        self.buttons2 = list()
        for user in data1:
            if user==self.controller.username:
                for rqst in data1[user]["friRqst"]:
                    self.buttons2.append(tk.Button(self.f7, text=rqst,height = 1, width = 15))
                    fpopup=partial(self.fpopup,len(self.buttons2)-1)
                    self.buttons2[-1].configure(command = fpopup)
                    text2.window_create("end", window=self.buttons2[-1])
                    text2.insert("end", "\n")
                break

        text2.configure(state="disabled")
        
        id1='28'
        packet=id1+self.controller.username
        sendNow(packet,(host, port))
        reply,addr=rcvNow(1024)
        id=reply[0:2]
        msg=reply[2:]
        d_msg=msg.split("<<seprator>>")
        totalPost=int(d_msg[0])
        print(totalPost)
        l_post=pickle.loads(d_msg[1])
        
        for i in range(totalPost):
            self.f11 = tk.Frame(self.f10, background='white',highlightbackground="black")
            self.f11.pack(side=tk.TOP, expand=True, fill="both")
            label4 = tk.Label(self.f11, text=l_post[i][0])
            label4.pack(side="top", fill="x", pady=10)
            if l_post[i][1]:
                id1='32'
                packet=id1+pickle.dumps(l_post[i][1])
                sendNow(packet,(host, port))
                reply,addr=rcvNow(1024)
                id=reply[0:2]
                msg=reply[2:]
                try:
                    pic=pickle.loads(msg)
                    te_img=numpy.array(pic)
                    te_img = Image.fromarray(te_img.astype('uint8'))
                    img = ImageTk.PhotoImage(te_img)
                    panel = tk.Label(self.f11, image = img)
                    panel.photo=img
                    panel.pack(side = tk.TOP, fill = "both", expand = "no")
                except:
                    print("error")
                









        



    def add(self):
        try:
            self.post=Image.open(askopenfile())
        except:
            print("ok")
        # self.post=(numpy.array(t)).tolist()
        # self.post=pickle.dumps(n_img)
    
    def postNow(self,status):
        post=''
        print(status.get(),"an")
        self.f11 = tk.Frame(self.f10, background='white',highlightbackground="black")
        self.f11.pack(side=tk.TOP, expand=True, fill="both")
        label4 = tk.Label(self.f11, text=status.get())
        label4.pack(side="top", fill="x", pady=10)
        if self.post:
            t=ImageTk.PhotoImage(self.post)
            panel = tk.Label(self.f11, image = t)
            panel.photo=t
            panel.pack(side = tk.TOP, fill = "both", expand = "no")
            post=(numpy.array(self.post)).tolist()
            post=pickle.dumps(post)

        msg=self.controller.username
        id1='30'
        packet=id1+msg+"<<seprator>>"+status.get()+"<<seprator>>"+post
        sendNow(packet,(host, port))
        reply,addr=rcvNow(1024)

            





    def fpopup(self,i):
        bt=self.buttons2[i]
        self.fpopup_menu = tk.Menu(self, 
                                       tearoff = 0) 
        

        self.fpopup_menu.add_command(label = "Accept", 
                                    command = lambda:self.task(bt['text'],id='22')) 
        self.fpopup_menu.add_separator()
        self.fpopup_menu.add_command(label = "Delete", 
                                    command = lambda:self.task(bt['text'],id='24'))
        self.fpopupm(bt)

    def fpopupm(self,bt):
        try:         
            self.fpopup_menu.tk_popup(bt.winfo_rootx(), bt.winfo_rooty(), 0)
        finally:
            self.fpopup_menu.grab_release()






    def changeDp(self):

        t=Image.open(askopenfile())
        n_img=(numpy.array(t)).tolist()
        n_img=pickle.dumps(n_img)
        msg=self.controller.username
        id1='20'
        packet=id1+msg+"<<seprator>>"+n_img
        sendNow(packet,(host, port))
        reply,addr=rcvNow(1024)
        for widget in self.f1.winfo_children():
            widget.destroy()
        for widget in self.f4.winfo_children():
            widget.destroy()
        for widget in self.f5.winfo_children():
            widget.destroy()
        self.chat(self.event)


    def cpopup(self,i):
        bt=self.buttons1[i]
        self.cpopup_menu = tk.Menu(self, 
                                       tearoff = 0) 
        

        self.cpopup_menu.add_command(label = "Profile", 
                                    command = lambda:self.task(bt['text'],id='10')) 
        self.cpopup_menu.add_separator()
        self.cpopup_menu.add_command(label = "Add Friend", 
                                    command = lambda:self.task(bt['text'],id='16')) 
        self.cpopupm(bt)
    def cpopupm(self,bt):
        try:         
            self.cpopup_menu.tk_popup(bt.winfo_rootx(), bt.winfo_rooty(), 0)
        finally:
            self.cpopup_menu.grab_release() 



    def validateLogout(self):
        id1='LG'
        packet=id1+""
        sendNow(packet,(host, port))
        reply,addr=rcvNow(1024)
        id=reply[0:2]
        msg=reply[2:]
        if id=='09':
            for widget in self.f6.winfo_children():
                widget.destroy()
            for widget in self.f7.winfo_children():
                widget.destroy()
            for widget in self.f4.winfo_children():
                widget.destroy()
            for widget in self.f5.winfo_children():
                widget.destroy()
            for widget in self.f10.winfo_children():
                widget.destroy()
            self.controller.show_frame(StartPage)
    
    def task(self,user,id):
        dcd=user.split(" ")
        msg=str(dcd[0])
        id1=id
        packet=id1+self.controller.username+"<<seprator>>"+msg
        sendNow(packet,(host, port))
        reply,addr=rcvNow(1024)
        
        if reply[0:2]=='11':
            for widget in self.f6.winfo_children():
                widget.destroy()
            for widget in self.f7.winfo_children():
                widget.destroy()
            for widget in self.f4.winfo_children():
                widget.destroy()
            for widget in self.f5.winfo_children():
                widget.destroy()
            for widget in self.f10.winfo_children():
                widget.destroy()
            self.chat(self.event)

        elif reply[0:2]=='25':
            self.chatpup(msg)
        elif reply[0:2]=='15':
            for widget in self.f6.winfo_children():
                widget.destroy()
            for widget in self.f7.winfo_children():
                widget.destroy()
            for widget in self.f4.winfo_children():
                widget.destroy()
            for widget in self.f5.winfo_children():
                widget.destroy()
            for widget in self.f10.winfo_children():
                widget.destroy()
            self.controller.profileUser=dcd[0]
            self.controller.show_frame(otherPage)
    

    def chatpup(self,user):
        self.top = tk.Toplevel() 
        self.top.geometry("180x100") 
        self.top.title("Chat")
        # self.messages = tk.Text(top)
        # self.messages.pack()

        self.input_user = tk.StringVar()
        self.input_field = tk.Entry(self.top, text=self.input_user)
        self.input_field.pack(side=tk.BOTTOM, fill="x")
        self.frame = tk.Frame(self.top)  # , width=300, height=300)
        self.input_field.bind("<Return>", self.Enter_pressed)
        self.frame.pack(side=tk.LEFT)
        self.top.mainloop()
    def Enter_pressed(self,event):
            input_get = self.input_field.get()
            print(input_get)
            # self.messages.insert(tk.INSERT, '%s\n' % input_get)
            label = tk.Label(self.frame, text=self.controller.username+": "+input_get)
            self.input_user.set('')
            label.pack()
            return "break"


class otherPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.bind("<<ShowFrame>>", self.profile)
        back=partial(self.back)
        button = tk.Button(self, text="My Profile",
                           command=back)
        button.pack(side=tk.TOP)
        self.f1 = tk.Frame(self, background='#98AFC7',width=500)
        self.f1.pack(side=tk.LEFT, expand=False, fill="both")
        self.f1.pack_propagate(0)
        self.f6 = tk.Frame(self.f1 ,background='white')
        self.f6.pack(side=tk.TOP, expand=False,fill="both")
        self.f7 = tk.Frame(self.f1 ,background='#98AFC7')
        self.f7.pack(side=tk.TOP, expand=False,fill="both")
        self.f8 = tk.Frame(self.f1 ,background='#98AFC7')
        self.f8.pack(side=tk.TOP, expand=False,fill="both")

        self.f2 = tk.Frame(self, background='#C0C0C0')
        self.f2.pack(side=tk.LEFT, expand=True, fill="both")
        self.f10 = tk.Frame(self.f2, background='#98AFC7')
        self.f10.pack(side=tk.TOP, expand=False, fill="both")
        self.f3 = tk.Frame(self ,background='white',width=500)
        self.f3.pack(side=tk.LEFT, expand=False,fill="both")
        self.f3.pack_propagate(0)
        self.f4 = tk.Frame(self.f3 ,background='white')
        self.f4.pack(side=tk.TOP, expand=False,fill="both")
        self.f5 = tk.Frame(self.f3 ,background='#98AFC7')
        self.f5.pack(side=tk.TOP, expand=False,fill="both")
        validateLogout = partial(self.validateLogout)
        button = tk.Button(self.f8, text="Logout",
                            command=validateLogout)
        button.pack(side=tk.BOTTOM)
        
    def back(self):
        for widget in self.f6.winfo_children():
            widget.destroy()
        for widget in self.f7.winfo_children():
            widget.destroy()
        for widget in self.f4.winfo_children():
            widget.destroy()
        for widget in self.f5.winfo_children():
            widget.destroy()
        for widget in self.f10.winfo_children():
            widget.destroy()
        self.controller.show_frame(MainPage)


    def profile(self,event):
        self.event=event
        msg=self.controller.profileUser
        id1='08'
        packet=id1+msg
        sendNow(packet,(host, port))
        reply,addr=rcvNow(1024)
        
        id=reply[0:2]
        msg=reply[2:]
        data=json.loads(msg)
        

        # # data=convert(data)
        label = tk.Label(self.f4, text=self.controller.profileUser+"'s Friends List")
        label.pack(side="top", fill="x", pady=10)
        text = tk.Text(self.f4, wrap="none")
        vsb = tk.Scrollbar(self.f4,orient="vertical", command=text.yview)
        text.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        text.pack(side="right",fill="both", expand=True)
        self.buttons = list()
        for user in data:
            if user!=self.controller.profileUser:
                self.buttons.append(tk.Button(self.f4, text=user,height = 1, width = 15))

                text.window_create("end", window=self.buttons[-1])
                text.insert("end", "\n")

        text.configure(state="disabled")
        id1='18'
        packet=id1+self.controller.username
        sendNow(packet,(host, port))
        reply,addr=rcvNow(1024)
        
        id=reply[0:2]
        msg=reply[2:]
        data1=json.loads(msg)
        # data1=convert(data1)



        id1='26'
        packet=id1+self.controller.profileUser
        sendNow(packet,(host, port))
        reply,addr=rcvNow(1024)
        id=reply[0:2]
        msg=reply[2:]
        n_img=pickle.loads(msg)
        n_img=numpy.array(n_img)

        print n_img.shape,type(n_img)
        n_img = Image.fromarray(n_img.astype('uint8'))
        # n_img.save(("ankush10"),"png")
        self.img = ImageTk.PhotoImage(n_img)
        self.panel = tk.Label(self.f6, image = self.img)
        self.panel.photo=self.img
        self.panel.pack(side = tk.TOP, fill = "both", expand = "no")


        label3 = tk.Label(self.f6, text="Username : "+self.controller.profileUser)
        label3.pack(side="top", fill="x", pady=10)
        label4 = tk.Label(self.f6, text="Name : "+data1[self.controller.profileUser]["first"]+" "+data1[self.controller.profileUser]["last"])
        label4.pack(side="top", fill="x", pady=10)

        id1='28'
        packet=id1+self.controller.profileUser
        sendNow(packet,(host, port))
        reply,addr=rcvNow(1024)
        id=reply[0:2]
        msg=reply[2:]
        d_msg=msg.split("<<seprator>>")
        totalPost=int(d_msg[0])
        print(totalPost)
        l_post=pickle.loads(d_msg[1])
        
        for i in range(totalPost):
            self.f11 = tk.Frame(self.f10, background='white',highlightbackground="black")
            self.f11.pack(side=tk.TOP, expand=True, fill="both")
            label4 = tk.Label(self.f11, text=l_post[i][0])
            label4.pack(side="top", fill="x", pady=10)
            if l_post:
                id1='32'
                packet=id1+pickle.dumps(l_post[i][1])
                sendNow(packet,(host, port))
                reply,addr=rcvNow(1024)
                id=reply[0:2]
                msg=reply[2:]
                pic=pickle.loads(msg)
                te_img=numpy.array(pic)
                te_img = Image.fromarray(te_img.astype('uint8'))
                img = ImageTk.PhotoImage(te_img)
                panel = tk.Label(self.f11, image = img)
                panel.photo=img
                panel.pack(side = tk.TOP, fill = "both", expand = "no")
        

    def validateLogout(self):
        id1='LG'
        packet=id1+""
        sendNow(packet,(host, port))
        reply,addr=rcvNow(1024)
        id=reply[0:2]
        msg=reply[2:]
        if id=='09':
            for widget in self.f6.winfo_children():
                widget.destroy()
            for widget in self.f7.winfo_children():
                widget.destroy()
            for widget in self.f4.winfo_children():
                widget.destroy()
            for widget in self.f5.winfo_children():
                widget.destroy()
            self.controller.show_frame(StartPage)









app = SampleApp()
app.title('Mini Facebook')
app.mainloop()