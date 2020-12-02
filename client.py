import socket
from config import *
import bcrypt
import getpass

class Client:
    def __init__(self):
        self.addr=(ip,port)
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.username=''
        self.passwrd=''
        self.type=None
        
        self.connect()

    def _set(self):
        self.username=input("Username:")
        # print(type(self.username))
        # self.passwrd=self.__get_passwrd(input("Please enter the password:"))
        self.passwrd=getpass.getpass(("Please enter the password:"))
    
    def __get_passwrd(self,passwrd):
        return bcrypt.hashpw(passwrd.encode("utf-8"), bcrypt.gensalt())

    """to validate username while registring"""

    def validate(self):
        reply=self.rcv_msg()
        print(reply)
        if reply=="ok":
            return 1
        return 0

    def rcv_msg(self):
        msg=self.sock.recv(chunk_size).decode().split(sep)[0]
        # print(msg)
        return msg


    def send_msg(self,message):
        message+=sep
        message+="0"*(chunk_size-len(message))
        message=bytes(message,encoding="utf-8")
        self.sock.send(message) 

    

    def client_1(self):
        name=input("Name: ")
        self._set()
        print("Press Y if your are teacher otherwise N")
        ans=input()
        teacher=0 if ans=="N" else 1  
        self.send_msg(self.username+sep+str(self.passwrd)+sep+name+sep+str(teacher))
        if not self.validate():
            print("This username is taken \n please type other username")
            self.client_1()    
        self.client_2()

    def client_2(self):
        self._set()
        self.send_msg(self.username+sep+str(self.passwrd))
        if not self.validate():
            print("incorrect username and password")
            self.client_2()
        self.type=int(self.rcv_msg())
        self.next_steps()
    
    def connect(self):
        self.sock.connect(self.addr)
        _info=self.sock.recv(chunk_size).decode().split(sep)[0]
        print(_info)
        client_type=input()
        self.send_msg(str(client_type))
        client_type=int(client_type)
        """ if the client connected for registering"""
        if client_type==1:
            self.client_1()
        """ if the client connected for login""" 
        if client_type==2:
            self.client_2()

    def create_course(self):
        course_code = input("Course_code:")
        course_name= input("Course name: ")
        self.send_msg(course_code+sep+course_name)
        if not self.validate():
            print("course not created")
        else:
            print(f"course {course_name} with course code {course_code} created")

    def view_courses(self):  
        msg=self.rcv_msg()
        print(msg)

    def chat_session_instructor(self):  
        while(True):
            choose = input("please enter 1 to send message and 2 for view messages")
            if(int(choose)==1):
                message = input("please write message to share:")
                self.send_msg(message)
                if(message=="exit"):
                    break
            else:
                message = "showall"
                self.send_msg(message)
                message = self.rcv_msg()
                print(message)
        self.next_steps()
        
    def add_and_view_posts(self):
        msg=self.rcv_msg()
        print(msg)
        course_code = input("please enter course code :")
        self.send_msg(str(course_code))
        msg=self.rcv_msg()
        print(msg)
        choose = input()
        self.send_msg(choose)
        if(choose== "1"):
            msg=self.rcv_msg()
            print(msg)
            post = input("please enter post details:")
            keywords = input("please add keywords for the post:")
            self.send_msg(post+sep+keywords)
            if(self.validate()):
                print("post created succefully ")

        elif(choose== "2"):
            msg=self.rcv_msg()
            print(msg)
            
            filter = input("choose 1 to filter by keywords else choose 0:")
            self.send_msg(filter)
            if(filter == "1"):
                msg=self.rcv_msg()
                print(msg)
                keyword = input("keyword:")
                self.send_msg(keyword)
                msg=self.rcv_msg()
                print(msg)
            else:
                msg=self.rcv_msg()
                print(msg)
        
        elif choose== "3":
            self.chat_session_instructor()
        
        elif choose=='4':
            topic=input("Give Topic Name:")
            self.send_msg(topic)
            if self.validate():
                print(self.rcv_msg())
            else:
                print(self.rcv_msg())

        elif choose=='5':
            self.view_gd()

        elif choose == "6":
            self.convo()

        self.next_steps()
        
    def view_gd(self):
        print(self.rcv_msg())
        topic=input()
        self.send_msg(topic)
        if self.validate():
            print(self.rcv_msg())
            v=input()
            self.send_msg(v)
            if v=='1':
                print(self.rcv_msg())
            elif v=='2':
                print(self.rcv_msg())
                msg=input()
                self.send_msg(msg)
                if self.validate():
                    print("Successfully added")
                else:
                    print("Not added")
        else:
            print("GD")
            return


    def convo(self):
        if self.validate():
            students=self.rcv_msg().split()
            print("These are students in private convo\n",*students)
            student_name=input("give student name:")
            while student_name not in students:
                student_name=input("give student name:")
            self.send_msg(student_name)
            print(self.rcv_msg())
            v=input()
            self.send_msg(v)
            if v=='1':
                print(self.rcv_msg())
            elif v=='2':
                msg=input("Please give message:")
                self.send_msg(msg)
                if self.validate():
                    print("successfully sent message")
                else:
                    print("not able to sent message")


        self.next_steps()
    def check_reg(self):
        msg=self.rcv_msg()
        print(msg)
        course_code=input("Course_code:")
        self.send_msg(course_code)
        if(self.validate()):
            print(self.rcv_msg())
            self.stu_all_details()
        else:
            self.rcv_msg()
        self.next_steps() 
       
    def stu_all_details(self):
        msg=self.rcv_msg()
        print(msg)
        choose=input()
        self.send_msg(choose)
        if choose=='1':
            print(self.rcv_msg())
        elif choose=='2':
            self.view_gd()
        elif choose=='3':
            print('start')
            if self.validate():
                print('validated')
                print(self.rcv_msg())
                
                while(True):
                    ch = input("please enter 1 to send message and 2 for view messages")
                    if(int(ch)==1):
                        message = input("please write message to share:")
                        self.send_msg(message)
                        if(message=="exit"):
                            break
                    else:
                        message = "showall"
                        self.send_msg(message)
                        message = self.rcv_msg()
                        print(message)
            else:
                print(self.rcv_msg())

        elif choose=='4':
            print(self.rcv_msg())
            v=input()
            self.send_msg(v)
            if v=='1':
                print(self.rcv_msg())
            elif v=='2':
                msg=input("Please give message:")
                self.send_msg(msg)
                if self.validate():
                    print("successfully sent message")
                else:
                    print("not able to sent message")

        self.next_steps()

    
    def next_steps(self):
        msg_rcvd=self.rcv_msg()
        print(msg_rcvd)
        instruction=input()
        self.send_msg(str(instruction))
        instruction=int(instruction)
        if self.type==1:
            if instruction==2:
                self.create_course()
            elif instruction==1:
                self.view_courses()
            elif( instruction == 3):
                self.add_and_view_posts()
            else:
                print("Not valid command")
        else:
            if instruction == 1:
                self.view_courses()
            elif instruction == 2:
                self.enroll()
            elif instruction ==3:
                self.view_courses()
            elif instruction==4:
                self.check_reg()
            else:
                print("Not valid command")
        self.next_steps()
    def enroll(self):    
        print(self.rcv_msg())
        course_code = input("Course Code: ")
        self.send_msg(course_code)
        print(self.rcv_msg())
        print(self.rcv_msg())

c=Client()
