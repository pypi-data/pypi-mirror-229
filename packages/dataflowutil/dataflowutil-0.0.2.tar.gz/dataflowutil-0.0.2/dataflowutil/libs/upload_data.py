import pandas as pd
from google.oauth2 import service_account
import pandas_gbq
from google.cloud import bigquery
import os
import dataflowutil.config.extra_var as extra_v

class UploadData:
    def __init__(self,connection):
        self.cn = connection
        self.credentials = service_account.Credentials.from_service_account_file(os.path.join(extra_v.PATH_CREDENTIALS, self.cn.credentials_path) ) # Same Credentials Storage Client

    def upload_data(self,raw_data):
        for df_upload,tag in raw_data.values():
            try:

                
                #Replace DTypes and Replace all types Objects to String
                df_upload = df_upload.convert_dtypes()
                for col in df_upload.select_dtypes(include='object'):
                    df_upload[col] = df_upload[col].astype("string") 

                pandas_gbq.to_gbq(df_upload,f"{self.cn.name_db_bigquery}.{tag}", project_id=self.cn.project_id,credentials=self.credentials,if_exists="replace")
                print(f"[SUCCEFULL UPLOAD DATA] : NAME_DATA: {tag} // DB_NAME: {self.cn.name_db_bigquery} // ProjectID: {self.cn.project_id}")
            except:
                import sys
                tipo_excepcion, valor_excepcion, traceback = sys.exc_info()
                print("Tipo de excepción:", tipo_excepcion)
                print("Valor de excepción:", valor_excepcion)
                print("Traceback:", traceback)
                print(f"[ERROR UPLOAD DATA] : NAME_DATA: {tag} // DB_NAME: {self.cn.name_db_bigquery} // ProjectID: {self.cn.project_id}")