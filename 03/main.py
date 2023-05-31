from ftplib import FTP
import os


BASE_DIR = os.path.dirname(os.path.realpath(__file__))

class FtpClient:
    # TODO: Initialize FTP client object
    def __init__(self, host, user, password, port):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.ftp = FTP() 

    # TODO: Connect to FTP server & login
    def connect(self):
        self.ftp.connect(self.host, self.port)
        self.ftp.login(self.user, self.password)
        

    # TODO: Disconnect from FTP server
    def disconnect(self):
        self.ftp.quit()

    # Soal no 1
    # Nama dan versi FTP server
    def getNameAndVersion(self):
        f = self.ftp.getwelcome()
        f = f.split('\n')[0][4:]
        return f

    # Soal no 2
    # Sistem yang diemulasikan FTP server
    def getWelcomeMessage(self):
        ret_msg = self.ftp.getwelcome()
        return ret_msg
    
    # Soal no 3
    # Daftar file di FTP server
    def getListOfFiles(self):
        return self.ftp.nlst()
    
    # Soal no 4
    # Mengunggah file ke FTP server
    def uploadFile(self, filename):
        ret_mesage = self.ftp.storbinary('STOR ' + filename, open(filename, 'rb'))
        return ret_mesage

    # Soal no 5
    # Membuat direktori
    def createDirectory(self, dirname):
        ret_mesage = self.ftp.mkd(dirname)
        return ret_mesage

    # Soal no 6
    # Direktori saat ini di FTP server
    def getCurrentDirectory(self):
        ret_mesage = self.ftp.pwd()
        return ret_mesage
    
    # Soal no 7
    # Mengganti nama direktori
    def renameDirectory(self, oldname, newname):
        ret_message = self.ftp.rename(oldname, newname)
        return ret_message

    # Soal no 8
    # Menghapus direktori
    def removeDirectory(self, dirname):
        ret_message = self.ftp.rmd(dirname)
        return ret_message
        

if __name__ == '__main__':
    # TODO: Read FTP server configuration from ftp.conf
    with open(os.path.join(BASE_DIR, 'ftp.conf')) as config_file:
        config = dict(line.strip().split('=') for line in config_file)

    HOST = config.get("host")
    USER = config.get("user")
    PASS = config.get("pass")
    PORT = config.get("port")

    ftp = FtpClient(HOST, USER, PASS, PORT)
    ftp.connect()

    print(ftp.getNameAndVersion())
    print(ftp.getWelcomeMessage())
    print(ftp.getListOfFiles())
    print(ftp.uploadFile('samplefile.txt'))
    print(ftp.createDirectory('test'))
    print(ftp.getCurrentDirectory())
    print(ftp.renameDirectory('test', 'test2'))
    print(ftp.removeDirectory('test2'))
