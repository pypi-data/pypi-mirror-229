import os
from google.cloud import storage
import dataflowutil.config.extra_var as extra_v
import sys
import pandas as pd

class LoadBucket:
    def __init__(self,connection):
        self.cn = connection
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(extra_v.PATH_CREDENTIALS, self.cn.credentials_path) 
        self.storage_client = storage.Client()
        self.name_bucket = self.cn.bucket_name
        self.data_config = pd.read_csv(extra_v.convert_sheet_url(self.cn.id_upload_data_to_bucket))

    def get_list_blobs(self,only_excel=False):
        list_blobs = []
        for VarFile in self.storage_client.list_blobs(self.name_bucket):
            name_file = VarFile.name
            if only_excel:
                if ".xlsx" in name_file or ".csv" in name_file:
                    list_blobs.append(name_file)
            else:
                list_blobs.append(name_file)
        return list_blobs
        
    
    def upload_files_bucket(self):
        try:
            for index,row in self.data_config.iterrows():
                tag_name = row["DB_NAME"]
                path_data = row["PATH_DATA"]
                upload = os.path.join(extra_v.PATH_UPLOAD_BUCKET, tag_name)
                bucket = self.storage_client.bucket(self.name_bucket)
                blob = bucket.blob(path_data+tag_name)

                blob.upload_from_filename(upload)

                print(f"[SUCCEFULL UPLOAD BUCKET] : Name_Bucket: {self.name_bucket} // Destination: {path_data}")

        except:
            tipo_excepcion, valor_excepcion, traceback = sys.exc_info()
            print("Tipo de excepción:", tipo_excepcion)
            print("Valor de excepción:", valor_excepcion)
            print("Traceback:", traceback)

