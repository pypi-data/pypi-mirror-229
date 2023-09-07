import dataflowutil.libs.load_data as ld
import dataflowutil.libs.load_bucket as lb
import dataflowutil.libs.upload_data as up
import dataflowutil.libs.load_connection as cn

class AppStruct:
    def __init__(self):
        self.cn = cn.LoadConnection()
        self.ld = ld.LoadData(self.cn)
        self.lb = lb.LoadBucket(self.cn)
        self.up = up.UploadData(self.cn)
    
    #Start Load Data Buckets
    def load_data(self,db):
        self.data = db.LoadDB(self.cn,self.lb,self.ld.get_data())
    
    #GET all data load "ConfigData"
    def get_load_data(self):
        get_data = self.data.get_load_data()
        print(get_data)

    #GET only data load "ConfigData"
    def get_only_data(self,tag=""):
        get_data = self.data.get_only_data(tag)
        print(get_data)

    #Upload data to BigQuery
    def upload_load_data(self):
        self.data.upload_data(self.up)

    #Get path list blobs Bucket
    def get_list_blobs(self):
        for name_file in self.lb.get_list_blobs(only_excel=True):
            print(name_file)
    
    #Upload data to Buckets
    def upload_data_buckets(self):
        self.lb.upload_files_bucket()
