import socket
from config import *
import threading
import sys
import sqlite3

class Server:
    def __init__(self):
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.addr=(ip,port)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.addr)
        self.conn=sqlite3.connect("./database/database.db", check_same_thread=False,timeout=100)
        self.chat_details = {}
        self.sock.listen()
        self.run()
        
    def send_message(self,message,client_sock):
        message=message+sep
        try:
            client_sock.send(bytes(message+'0'*(chunk_size-len(message)),encoding="utf-8"))

        except Exception as E:
            print("Exception in sending message")
            print(E)
            # self.sock.close()
            # self.conn.close()
            sys.exit(0)

    def receive_message(self,client_sock):
        # print(type(client_sock))
        try:
            return client_sock.recv(chunk_size).decode().split(sep)

        except Exception as E:
            print("Exception in recieving message")
            print(E)
            # self.sock.close()
            # self.conn.close()
            sys.exit(0)

    def run(self):
        try:
            while(True):
                # try:
                client_sock,client_addr=self.sock.accept()
                client_sock = client_sock
                threading.Thread(target=self.connect,args=(client_sock,)).start()
                # except socket.error:
                #     self.run()
                #     print("Got socket error")
                    
        except Exception as e:
            print("An Exception occured")
            print(e)
            sys.exit(1)
        finally:
            self.sock.close()
    
    def connect(self,client_sock):
        reg_msg="Choose [1]Register or [2]Login\n Type the corresponding no."+sep
        client_sock.send(bytes(reg_msg+'0'*(chunk_size-len(reg_msg)),encoding="utf-8"))
        msg_rcvd=client_sock.recv(chunk_size).decode()
        msg_rcvd=int(msg_rcvd.split(sep)[0])
        self.next_steps(client_sock,msg_rcvd)
        # return msg_rcvd
    
    def next_steps(self,client_sock,msg_rcvd):
        registration= 0
        login_status = 0
        if(msg_rcvd == 1):
            while(True):
                if(self.register(client_sock)):
                    registration = 1
                    break

        if(registration == 1 or msg_rcvd==2):
            while(True):
                values = self.login(client_sock)
                if(values[0]):
                    login_status =1 
                    break
        print("User Logged IN")

        self.functions(values[1],values[2],client_sock)
        self.sock.close()
        return 

    def register(self,client_sock):
        val = (client_sock.recv(chunk_size).decode().split(sep))
        # print(val)
        usr,passwrd,name,typ,_= val 
        try:
            cursor=self.conn.cursor()
            tmp=(usr,passwrd,name,int(typ),)
            cursor.execute('select * from user_password where user_name== ?',(usr,))
            res=cursor.fetchall()
            # print(res)
            if(len(res)!=0):
                self.send_message("not ok",client_sock)
                
                return False
            # print(tmp)
            cursor.execute('insert into user_password("user_name","passwrd","name","type") values(?,?,?,?)',tmp)
            self.conn.commit()
            self.send_message("ok",client_sock)
            cursor.close()
            return True
        except Exception as e:
            self.sock.close()
            print("exception in registering")
            print(e)
            sys.exit(0)


    def login(self,client_sock):
        try:
            usr,passwrd,_=client_sock.recv(chunk_size).decode().split(sep)
            cursor=self.conn.cursor()
            tmp=(usr,passwrd,)
            cursor.execute('select * from user_password where user_password.user_name==? and user_password.passwrd==?',tmp)
            res=cursor.fetchone()
            # print(res)
            if(len(res)==0):
                self.send_message("not ok",client_sock)
                return (False,1,usr)
            cursor.close()
            self.send_message("ok",client_sock)
            self.send_message(str(res[4]),client_sock)
            if(res[4]==1):
            
                return (True,1,usr)
            else:
                return (True,0,usr)
        except Exception as e:
            print("exception in login")
            print(e)
            sys.exit(0)

    def functions(self,check,user_name,client_sock):

        if(check==1):
            self.home_teacher(user_name,client_sock)
        else:
            self.home_student(user_name,client_sock)    
    
    def view_post(self,client_sock,username,course_code):
        self.send_message("do you want to filter by keywords",client_sock)
        filter = int(self.receive_message(client_sock)[0])
        if(filter):
            self.send_message("please write keyword",client_sock)
            keyword = self.receive_message(client_sock)[0]
            try:
                cursor=self.conn.cursor()
                tmp=(course_code,keyword)
                cursor.execute('select * from posts where course_code == ? and keyword == ?',tmp)
                res=cursor.fetchall()
                string = "Course_Code   Post  Keyword TimePosted\n"
                for i in res:
                    string+= str(i[1])+"    " +i[2]+"   "+i[3]+"    "+i[4]+"\n"
                self.send_message(string,client_sock)
            except Exception as e:
                self.send_message("Failed to show posts",client_sock)
                print(e)
                cursor.close()
        else:
            try:
                cursor=self.conn.cursor()
                tmp=(course_code,)
                cursor.execute('select * from posts where course_code == ?',tmp)
                res=cursor.fetchall()
                string = "Course_Code   Post  Keyword TimePosted\n"
                for i in res:
                    string+= str(i[1])+"    " +i[2]+"   "+i[3]+"    "+i[4]+"\n"
                self.send_message(string,client_sock)
            except Exception as e:
                self.send_message("Failed to show posts",client_sock)
                print(e)
                cursor.close()
        
            

    def add_post(self,client_sock,user_name,course_code):

        self.send_message("please type post to add to classroom",client_sock)

        temp= self.receive_message(client_sock)
        post_details = temp[0]
        if(len(temp)>2):
            keyword = temp[1]
        else:
            keyword = None
        cursor=self.conn.cursor()
        try:
            tmp=(user_name,course_code,post_details,keyword,)
            cursor.execute('insert into posts("user_name","course_code","post_details","keyword", "add_time") values(?,?,?,?,datetime(\'now\', \'localtime\'))',tmp)
            self.conn.commit()
            self.send_message("ok",client_sock)
        
        except Exception as e:
            
            self.send_message("Failed to add posts",client_sock)
            print("Exception")
            print(e)

    def broadcast(self,message,client_sock,course_code,user_name):        
        print("ALOINDAWOINEFAEORFNAERNFO")
            
        try:
            for i in self.chat_details[course_code]["clients"]:
                if(i!= client_sock):
                    self.send_message(message,i)
            self.chat_details[course_code]["messages"].append(user_name+"---->"+message)
        except Exception as e:
            print(e)
            print("ALOINDAWOINEFAEORFNAERNFO")
            

    def chat_session(self,user_name,course_code,client_sock):

        if course_code not in self.chat_details:
            self.chat_details[course_code] = {"clients":[],"messages":[]}
        
        self.chat_details[course_code]["clients"].append(client_sock)
        # print('asdasdasdasdasd')
        while(True):
            
            message = self.receive_message(client_sock)[0]
            # print('asdasdasdasdasd')
            print(message)
            if(message == "exit"):
                self.broadcast("i am closing chat session",client_sock,course_code,user_name)
                self.chat_details.pop(course_code)
                break 
            elif(message == "showall"):
                final = ""
                message = self.chat_details[course_code]["messages"]
                for i in message:
                    final+=i+"\n"
                # print(final)
                self.send_message(final,client_sock)
            else:
                self.broadcast(message,client_sock,course_code,user_name)
        self.home_teacher(user_name,client_sock)

        
        
    def show_posts_and_courses(self,client_sock,user_name):
        
        self.send_message("Please enter Course Code to view course details",client_sock)
        course_code = int(self.receive_message(client_sock)[0])
        self.send_message("""please enter 1 to add post and 2 to view posts and 3 to start a chat session and 4 create GD and 5 for viewing GD 
        and 6 for private_convo""",client_sock)
        value  = int(self.receive_message(client_sock)[0])
        if(value == 1):
            self.add_post(client_sock,user_name,course_code)
        elif(value ==2 ):
            self.view_post(client_sock,user_name,course_code)
        elif(value ==3):
            # print(3,'asdasdass')
            self.chat_session(user_name,course_code,client_sock)
        elif value==4:
            self.create_gd(course_code,client_sock,user_name)
        elif value==5:
            self.view_gd_teacher(course_code,client_sock,user_name)
        elif value==6:
            self.teacher_private_conv(user_name,client_sock,course_code)
        self.home_teacher(user_name,client_sock)
        return 
    
    def teacher_private_conv(self,user_name,client_sock,course_code):
        cursor=self.conn.cursor()
        sql='select distinct student_name from private_conv where teacher_name==? and course_code==?'
        try:
            cursor.execute(sql,(user_name,course_code,))
            res=cursor.fetchall()
            if(len(res)!=0):
                string="choose private_conv with student from "
                for i in res:
                    string+=i[0]+" "
                string+="\n"
                self.send_message("ok",client_sock)
                self.send_message(string,client_sock)
            else:
                self.send_message("nok",client_sock)
                self.send_message("No student conversation",client_sock)
                self.home_teacher(user_name,client_sock)
                return
        except Exception as e:
            print(e)
            self.send_message("nok",client_sock)
            self.send_message("Not",client_sock)
            self.home_teacher(user_name,client_sock)
            return

        student_name=self.receive_message(client_sock)[0]
        self.send_message("Please select 1 to view message and 2 to send message",client_sock)    
        choose=self.receive_message(client_sock)[0]
        # print(teacher_name,type(teacher_name))
        if choose=='1':
            try:
                cursor.execute("select * from private_conv where student_name==? and teacher_name == ? and course_code==?",(student_name,user_name,course_code,))
                res=cursor.fetchall()
                string="Message  time\n"
                for i in res:
                    string+=i[2]+" "+i[3]+"\n"
                self.send_message(string,client_sock)
            except Exception as e:
                self.send_message("No convo",client_sock)
                print(e)

        else:
            """insert name of sender"""
            try:
                msg=self.receive_message(client_sock)[0]
                msg=f"{user_name}--->"+msg
                cursor.execute("insert into private_conv values(?,?,?,datetime(\'now\', \'localtime\'),?)",(student_name,user_name,msg,course_code,))
                self.conn.commit()
                self.send_message("ok",client_sock)
            except Exception as e:
                self.send_message("No",client_sock)
                print(e)
        cursor.close()
        self.home_teacher(user_name,client_sock)


    def create_gd(self,course_code,client_sock,user_name):
        sql='insert into group_discussion("topic","course_code","user_name","message","post_time") values(?,?,?,?,datetime(\'now\', \'localtime\'))'
        temp= self.receive_message(client_sock)
        topic=temp[0]
        cursor=self.conn.cursor()
        try:
            cursor.execute("select * from group_discussion where course_code==? and topic==? and user_name==?",(course_code,topic,user_name,))
            res=cursor.fetchall()
            if len(res)>0:
                self.send_message("not ok",client_sock)
                self.send_message("Already available",client_sock)
                self.home_teacher(user_name,client_sock)
                return
            cursor.execute(sql,(topic,course_code,user_name,"Created GD",))
            self.conn.commit()
            self.send_message("ok",client_sock)
            self.send_message("Created GD",client_sock)
        except Exception as E:
            print(E)
            self.send_message("not ok",client_sock)
            self.send_message("Not created GD",client_sock)
        self.home_teacher(user_name,client_sock)
            

    def view_gd_teacher(self,course_code,client_sock,user_name):
        self.send_message("Please input topic",client_sock)
        topic=self.receive_message(client_sock)[0]
        cursor=self.conn.cursor()
        try:
            cursor.execute("select * from group_discussion where course_code==? and topic==? and user_name==?",(course_code,topic,user_name,))
            res=cursor.fetchall()
            if len(res)<=0:
                self.send_message("not",client_sock)
                self.home_teacher(user_name,client_sock)
                return        
        except Exception as e:
            print(e)
            self.send_message("not",client_sock)
            self.home_teacher(user_name,client_sock)
            return
        
        
        self.send_message("ok",client_sock)
        self.send_message("input 1 for viewing messages in gd and 2 for adding messages to gd",client_sock)
        v=int(self.receive_message(client_sock)[0])
        sql1="select user_name,message,post_time from group_discussion where course_code == ? and topic == ?"
        sql2='insert into group_discussion("topic","course_code","user_name","message","post_time") values(?,?,?,?,datetime(\'now\', \'localtime\'))'
        if v==1:
            try:
                cursor.execute(sql1,(course_code,topic,))
                res=cursor.fetchall()
                string = "user_name  message  post_time\n"
                for i in res:
                    string+=i[0]+"  "+i[1]+"  "+i[2]+"\n"
                self.send_message(string,client_sock)
                
            except Exception as E:
                print(E)
                self.send_message("Not able to fetch",client_sock)
            
        elif v==2:
            self.send_message("please type message to add to gd",client_sock)
            temp= self.receive_message(client_sock)
            message = temp[0]
            try:
                cursor.execute(sql2,(topic,course_code,user_name,message,))
                self.conn.commit()
                self.send_message("ok",client_sock)
            except Exception as E:
                print(E)
                self.send_message("not ok",client_sock)
            
        cursor.close()
        self.home_teacher(user_name,client_sock)
        return



    def home_teacher(self,user_name,client_sock):
        self.send_message(f"Hi {user_name}\nPress 1 for showing existing courses\nPress 2 for creating new course \n press 3 for viewing course",client_sock)
        instruction=self.receive_message(client_sock)[0]
        print(instruction)
        if instruction=="1":
            self.view_courses_teacher(user_name,client_sock)
        elif instruction=="2":
            self.create_course(user_name,client_sock)
        elif instruction == "3":
            self.show_posts_and_courses(client_sock,user_name)
        else:
            self.home_teacher(user_name,client_sock)
    
    def view_courses_teacher(self,user_name,client_sock):

        try:
            cursor=self.conn.cursor()
            tmp=(user_name,)
            cursor.execute('select * from courses where courses.user_name== ?',tmp)
            res=cursor.fetchall()
            string = "Course_Code   Course_Name\n"
            
            for i in res:
                string+= str(i[0])+" " +i[1]+"\n"
            self.send_message(string,client_sock)

        except Exception as e:
            self.send_message("Failed to show courses",client_sock)
            print(e)
        cursor.close()
        self.home_teacher(user_name,client_sock)


    def create_course(self,user_name,client_sock):

        # message = "Please input course code and course name to create course "
        # self.send_message(message,client_sock)
        course_code,course_name,_ = self.receive_message(client_sock)
        cursor=self.conn.cursor()
        try:
            tmp=(user_name,course_code,course_name,)
            cursor.execute('insert into courses("user_name","course_code","course_name") values(?,?,?)',tmp)
            self.conn.commit()
            self.send_message("ok",client_sock)
        except Exception as e:
            self.send_message("Failed to create course",client_sock)
            print("Exception")
            print(e)
            # self.sock.close()
            # sys.exit(0)

        cursor.close()
        self.home_teacher(user_name,client_sock)


    def home_student(self,user_name,client_sock):

        self.send_message("""Hi, welcome to the classroom\nHere you can view and enroll for courses \n 
        input 1 for showing existing courses \n
        input 2 for enrollig new course \n 
        input 3  for viewing updates for registered courses\n
        input 4  for viewing details of a registered course\n
        """,client_sock)
        message = self.receive_message(client_sock)[0]
        message=int(message)
        if message==1:
            self.view_courses_student(user_name,client_sock)
        elif message==2:
            self.enroll_course(user_name,client_sock)
        elif message==3:
            self.view_updates(user_name,client_sock)
        elif message==4:
            self.check_course_reg(user_name,client_sock)
        else:
            self.home_student(user_name,client_sock)
    
    def check_course_reg(self,user_name,client_sock):
        self.send_message("please input the registered course's code",client_sock)
        course_code=self.receive_message(client_sock)[0]
        cursor=self.conn.cursor()
        sql1="select course_name from student_courses where user_name==? and course_code==?"
        try:
            cursor.execute(sql1,(user_name,course_code,))
            res=cursor.fetchone()
            if len(res):
                self.send_message("ok",client_sock)
                self.send_message(f"Welcome to Course {res[0]} with course_code {course_code}",client_sock)
                self.all_details(user_name,client_sock,course_code)
            else:
                self.send_message("not ok",client_sock)
                self.send_message("Input correct code",client_sock)
                self.home_student(user_name,client_sock)
            
        except Exception as e:
            print(e)
        cursor.close()
        self.home_student(user_name,client_sock)


    
    def all_details(self,user_name,client_sock,course_code):
        
        self.send_message("please select 1 for seeing posts and 2 for GD and 3 for chat session and  4 for private conversation with teacher",client_sock)
        value = self.receive_message(client_sock)[0]
        if(int(value)==1):    
            sql1="select keyword,post_details,add_time from posts where  course_code == ?  order by add_time desc"
            # conn=se
            try:
                cursor=self.conn.cursor()
                cursor.execute(sql1,(course_code,))
                res=cursor.fetchall()
                string ="keyword  post_details  add_time\n"
                for i in res:
                    # print(i)
                    string+="  ".join([j for j in i]) +"\n"
                self.send_message(string,client_sock)

            except Exception as e:
                self.send_message("Not able to see post")
                print(e)
            
        elif int(value)==2:
            self.view_gd(course_code,client_sock,user_name)
        elif int(value)==3:
            self.chat_session_student(user_name,course_code,client_sock)
        elif int(value)==4:
            self.private_conv(user_name,client_sock,course_code)
        cursor.close()
        self.home_student(user_name,client_sock)

    def private_conv(self,user_name,client_sock,course_code):
        cursor=self.conn.cursor()
        try:
            cursor.execute("select user_name from courses where course_code==?",(course_code,))
            res=cursor.fetchone()
            teacher_name=res[0]
        except:
            self.send_message("Not able to fetch teacher's name",client_sock)
            self.home_student(user_name,client_sock)
            return
        self.send_message("Please select 1 to view message and 2 to send message",client_sock)    
        choose=self.receive_message(client_sock)[0]
        # print(teacher_name,type(teacher_name))
        if choose=='1':
            try:
                cursor.execute("select * from private_conv where student_name==? and teacher_name == ? and course_code==?",(user_name,teacher_name,course_code,))
                res=cursor.fetchall()
                string="Message  time\n"
                for i in res:
                    string+=i[2]+" "+i[3]+"\n"
                self.send_message(string,client_sock)
            except Exception as e:
                self.send_message("No convo",client_sock)
                print(e)

        else:
            """insert name of sender"""
            try:
                msg=self.receive_message(client_sock)[0]
                msg=f"{user_name}--->"+msg
                cursor.execute("insert into private_conv values(?,?,?,datetime(\'now\', \'localtime\'),?)",(user_name,teacher_name,msg,course_code,))
                self.conn.commit()
                self.send_message("ok",client_sock)
            except Exception as e:
                self.send_message("No",client_sock)
                print(e)
        cursor.close()
        self.home_student(user_name,client_sock)


    def view_gd(self,course_code,client_sock,user_name):
        self.send_message("Please input topic",client_sock)
        topic=self.receive_message(client_sock)[0]
        cursor=self.conn.cursor()
        try:
            cursor.execute("select * from group_discussion where course_code==? and topic==?",(course_code,topic,))
            res=cursor.fetchall()
            if len(res)<=0:
                self.send_message("not",client_sock)
                self.home_student(user_name,client_sock)
                return        
        except Exception as e:
            print(e)
            self.send_message("not",client_sock)
            self.home_student(user_name,client_sock)
            return
        
        
        self.send_message("ok",client_sock)
        self.send_message("input 1 for viewing messages in gd and 2 for adding messages to gd",client_sock)
        v=int(self.receive_message(client_sock)[0])
        sql1="select user_name,message,post_time from group_discussion where course_code == ? and topic == ?"
        sql2='insert into group_discussion("topic","course_code","user_name","message","post_time") values(?,?,?,?,datetime(\'now\', \'localtime\'))'
        if v==1:
            try:
                cursor.execute(sql1,(course_code,topic,))
                res=cursor.fetchall()
                string = "user_name  message  post_time\n"
                for i in res:
                    string+=i[0]+"  "+i[1]+"  "+i[2]+"\n"
                self.send_message(string,client_sock)
                
            except Exception as E:
                print(E)
                self.send_message("Not able to fetch",client_sock)
            
        elif v==2:
            self.send_message("please type message to add to gd",client_sock)
            temp= self.receive_message(client_sock)
            message = temp[0]
            try:
                cursor.execute(sql2,(topic,course_code,user_name,message,))
                self.conn.commit()
                self.send_message("ok",client_sock)
            except Exception as E:
                print(E)
                self.send_message("not ok",client_sock)
        
        cursor.close()
        self.home_student(user_name,client_sock)
        return


    def chat_session_student(self,user_name,course_code,client_sock):
        course_code=int(course_code)
        print("ahbdjsfkn")
        
        if course_code not in self.chat_details:
            self.send_message("nok",client_sock)
            self.send_message("No active chat session",client_sock)
        else:
            self.send_message("ok",client_sock)
            self.send_message("inside chat session",client_sock)
            self.chat_details[course_code]["clients"].append(client_sock)
            self.broadcast("i joined the chat session",client_sock,course_code,user_name)
            while(True):
                print('1')
                message = self.receive_message(client_sock)[0]
                
                if(message == "exit"):
                    self.broadcast("i am leaving the session",client_sock,course_code,user_name)
                    self.chat_details[course_code]["clients"].remove(client_sock)
                elif(message == "showall"):
                    final = ""
                    message = self.chat_details[course_code]["messages"]
                    for i in message:
                        final+=i+"\n"
                    self.send_message(final,client_sock)
                else:
                    self.broadcast(message,client_sock,course_code,user_name)
        self.home_student(user_name,client_sock)
            
    def view_updates(self,user_name,client_sock):

        sql="select * from posts where (select course_code from student_courses where user_name==?) order by add_time desc limit 10"
        cursor=self.conn.cursor()
        try:
            tmp=(user_name,)
            cursor.execute(sql,tmp)
            res=cursor.fetchall()
            print(res)
            string="course_code post_details keyword add_time \n"
            for i in res:
                string+= str(i[1])+" "+i[2]+i[3]+i[4]+"\n"
            self.send_message(string,client_sock)
        except Exception as e:
            print(e)
            self.send_message("Failed to show courses",client_sock)
        cursor.close()
        self.home_student(user_name,client_sock)

    def view_courses_student(self, user_name,client_sock):
        try:
            cursor=self.conn.cursor()
            tmp=(user_name,)
            cursor.execute('select * from student_courses where user_name== ?',tmp)
            res=cursor.fetchall()
            string="course_code course_name\n"
            for i in res:
                string+= str(i[1])+" "+i[2]+"\n"
            self.send_message(string,client_sock)
        except:
            self.send_message("Failed to show courses",client_sock)
        cursor.close()
        self.home_student(user_name,client_sock)

    def enroll_course(self,user_name,client_sock):
        self.send_message("please input course code to register",client_sock)
        course_code = int(self.receive_message(client_sock)[0])
        
        cursor=self.conn.cursor()
        tmp=(course_code,)
        cursor.execute('select * from courses where course_code== ?',tmp)
        
        course_details=cursor.fetchall()
        
        if len(course_details)==0:
            self.send_message("not ok",client_sock)
            self.send_message("No Course Available",client_sock)
            return self.home_student(user_name,client_sock)
        
        teacher = course_details[0][2]
        course_name = course_details[0][1]
        course_code= course_details[0][0]
        try:
            tmp=(user_name,course_code,course_name,)
            cursor.execute('insert into student_courses("user_name","course_code","course_name") values(?,?,?)',tmp)
            self.conn.commit()
            self.send_message("ok",client_sock)
            self.send_message("succefully enrolled to the course",client_sock)
        except Exception as e :
            print(e)
            self.send_message("not ok",client_sock)
            self.send_message("Failed to enroll to the courses",client_sock)
        cursor.close()
        self.home_student(user_name,client_sock)
    
    
        

        # cursor=self.conn.cursor()
        # try:
        #     tmp=(username)
        #     cursor.executemany(f'select * from student_courses where user_name== ?',tmp)
        #     res=cursor.fetchall()
        #     self.send_message("".join(res),client_sock)
        # except:
        #     self.send_message("Failed to show courses",client_sock)

        

        # pass 
    



    # def back_to_home_student(self,username):
    #     pass
    # def back_to_home_teacher(self,username):
    #     pass

    # def add_post(self,username,post,course_code):

    #     pass

    # def view_post_student(self,username,course_code):
    #     pass 

    # def create_assignment(self, user_name,course_code):


    #     pass 

        # self.functions(values[1],values[2])

        
            
            
                
            





    # def connect(self,client_sock):
        # if(first):
        #     msg_rcvd=self.cons_msg(client_sock)
        
        # if(msg_rcvd==1):
        #     if self.register(client_sock):
        #         check  = self.login(client_sock)
        #         if(check[0]==True):
        #             self.functions(client_sock,check[1],check[2])
        #         else:
        #             self.connect(client_sock,first=0)
        #     else:
        #         self.connect(client_sock,first=0)
        # elif msg_rcvd==2:
        #     if(self.login(client_sock)):
        #         self.functions(client_sock)
        #     else:
        #         self.connect(client_sock,first=0,msg_rcvd=2)
        # return

        



    
    # def add_course(self,client_sock):
    #     post,username =client_sock.recv(chunk_size).decode().split(sep)

    # def add_post(self,client_sock):
    #     post,username =client_sock.recv(chunk_size).decode().split(sep)

    #     try:
    #         cursor=self.conn.cursor()

    #     except :
    #         pass
    #     pass


if __name__ == "__main__":
    s=Server()
    
    
    
