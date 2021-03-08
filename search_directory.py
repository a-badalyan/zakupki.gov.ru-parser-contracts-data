import ftplib

ftp = ftplib.FTP()
ftp.connect('ftp.zakupki.gov.ru')
ftp.login('free', 'free')
ftp.cwd('/fcs_regions/Marij_El_Resp/contracts')
directory_list = ftp.nlst()
for directory in directory_list:
    if not directory[-3:] == 'zip':
        print(directory)