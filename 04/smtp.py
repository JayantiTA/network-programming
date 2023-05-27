import smtplib
import sys

#buat log file
class Logger(object):
    def __init__(self, filename="Default.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
#menghapus log sebelumnya        
file_to_delete = open("answer.log",'w')
file_to_delete.close()
file_to_delete = open("error.log",'w')
file_to_delete.close()
sys.stdout = Logger("answer.log")
sys.stderr = Logger("error.log")

fromaddr = "xxx" #email asal
toaddrs  = ["xxx"] #email tujuan
msg_text = "ini adalah test email progjar" #isi email 
subject = "test email"  #subject email

msg = """From: %s\r\nTo: %s\r\nSubject: %s\r\n\

%s
""" % (fromaddr, ", ".join(toaddrs), subject, msg_text) #format email

server = smtplib.SMTP('smtp.office365.com', 587) #server email
server.set_debuglevel(1) #debug
server.starttls() #start tls 
server.login('xxx', 'xxx') #login email
server.sendmail(fromaddr, toaddrs, msg) #kirim email
server.quit() #keluar dari server