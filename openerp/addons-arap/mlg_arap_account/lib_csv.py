# -*- encoding: utf-8 -*-
import csv
import glob
import os
import re
import collections
import shutil
import ntpath
import time
import codecs
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class csv_ultilities():
    
    _csv_pattern = "[\S]*\.csv"
    
    #Function to move list of files to directory
    #Input filesArray: list of files   
    #Input des_directory: name of folder   
    #Output: list of files 
    def _moveFiles(self, filesArray, des_directory):
        des_directory = des_directory +'/'+ time.strftime("%Y-%m-%d")
        if not os.path.exists(des_directory):
            os.makedirs(des_directory)
            
        unmoved_files = []   
        for file in filesArray:
            filename = ntpath.basename(file)
            des_file_path = des_directory + "/" + filename
            try:
                shutil.move(file, des_file_path)
                #print "File Moved"
            except:
                #print "Cannot Move file"
                unmoved_files.append(file)
                
        if unmoved_files:
            msg = "Dear All,\n\nAn error occurs when trying to move the file to: " + des_directory + "\nPlease check the following files:\n"
            for unmoved_file in unmoved_files:
                msg = msg + unmoved_file + "\n"
            msg = msg + "\n\nThank you"
            
            # will call sendEmail(self, msg, "ARAP Import Error")
    
    #Function to validate header file
    #Input headers: headers of file
    #Input path_file_name: full path file name
    #Output: return True or False      
         
    def _validate_file(self, path_file_name=None, headers=[]):
        if not path_file_name or not re.match(self._csv_pattern, path_file_name) or not os.path.isfile(path_file_name):
            return False
        
        with open(path_file_name) as csvfile:
            reader = csv.reader(csvfile)
            csv_header = list(reader.next())
            if not sorted(headers) == sorted(csv_header):
                return False
#            for row in reader:
#                if not len(headers) == len(list(row)):
#                    return False
        return True
    
    #Function to list out the file with the given extenstion
    #Input folder_name: name of folder   
    #Output: list of files 
    def _read_files_folder(self, folder_name=None):
        
        path = os.path.normpath(os.path.join(folder_name, '*.csv'))
        list = glob.glob(path)
        list.sort()
      
        return list
    
    #Function to read content of a file
    #Input file_name: full path file name
    #Output: list of objects (hashes)
    def _read_file(self, file_name=None):
        
        result = []
        
        with codecs.open(file_name, encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            result = list(reader)
        
#            result = []
#            for row in reader:
#                tmp_dict = {}
#                for column, value in row.iteritems():
#                    tmp_dict.setdefault(column, value)
#                result.append(tmp_dict)
                        
        return result
    

            
    #Function to write content to a file
    #Input content: the content need to write to file
    #Input headers: headers of file
    #Input path_file_name: full path file name
    #Output: return True or False      
    def _write_file(self, content, headers, path_file_name=None ):
    
       result = False 
       
       if content and len(content) > 0:
     
           if not sorted(headers) == sorted(list(content[0])):
               return False
#           for row in content:
#               if not len(headers) == len(list(row)):
#                   return False
           
           with open(path_file_name, 'wb+') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                writer.writerows(content)
                #for row in content:
                #    writer.writerow({k:v.encode('utf8') for k,v in row.items()}) 
                return True

       return result


################################Test Function######################################################################################
    #Function to test "read files in a folder"
    def _test_files_in_folder(self):
      
        headers = ['Code', 'Name', 'Value']
        folder_name = "/home/quocto/testcsvfile"
     
        #Check folders
        if not os.path.exists(folder_name):
            # will call sendEmail(self, "Dear All,\n\nThe Bao_Hiem folder cannot be found on ARAP Server, please check\n\nThank you", "ARAP Import Error")
            print "Folder doesn't exist!"
            return{}
                   
            ListOfFiles = self._read_files_folder(folder_name)    
        
        valid_files = []   
        invalid_files = []   
        
        for file in ListOfFiles:
            if not self._validate_file(file, headers):
                invalid_files.append(file)
            else:
                valid_files.append(file)
     
        print "Files are valid!"
        print valid_files
        print "Files are invalid!"
        print invalid_files
    
   #Function to test "read content of a file"
    def _test_read_file(self):
        
        headers = ['Code', 'Name', 'Value']
        path_file_name = "/home/phung11764/FU_0102 Ket Xuat Phieu Chi 7.1.csv"
      
#         if not self._validate_file(path_file_name, headers):
#             # will call sendEmail(self, "Dear All,\n\nFile is ivalid format, please check\n\nThank you", "ARAP Import Error")
#             print "File is invalid format file or not existed"
#             return False
      
        result = self._read_file(path_file_name)
        for r in result:
            print r
            
    #Function to test "write content to file"
    def _test_write_file(self):
      
        headers = ['Code', 'Name', 'Value']
        path_file_name =  "/home/quocto/testcsvfile/test_file.csv"  
       
        content = [{'Code': '1', 'Name': 'khoa', 'Value': 'xx'}, 
                 {'Code': '2', 'Name': 'khoi', 'Value': 'yy'}, 
                 {'Code': '3', 'Name': 'quoc', 'Value': 'zz'}, 
                 {'Code': '4', 'Name': 'thi', 'Value': 'mm'}, 
                 {'Code': '5', 'Name': 'nhan', 'Value': 'll'}]
       
     
       
        if self._write_file( content,  headers, path_file_name ):
            print "File wrote successfully!"
        else:
            print "File wrote unsuccessfully!"
            
    #Function to test "move files"
    def _test_move_files(self):
        
        list_of_file_names = ["/home/quocto/testcsvfile/test_file1.csv", "/home/quocto/testcsvfile/test_file2.csv"]
        des_directory = "/home/quocto/testcsvfile/Done"
      
        self._moveFiles(list_of_file_names, des_directory)
         
            
# csvUti = csv_ultilities()
#csvUti._test_files_in_folder()
# csvUti._test_read_file()
#csvUti._test_write_file()
# csvUti._test_move_files()




