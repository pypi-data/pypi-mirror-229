import pandas as pd

class DataProcessing():
    def __init__(self,connection,path_bucket):
        self.cn = connection
        self.raw_data = {}
        self.path_bucket = path_bucket
    
    def load_data(self,data_get):
        for name_file in self.path_bucket.get_list_blobs(only_excel=True):
            for data_strct_key,data_strct_value in data_get.items():
                name_data = data_strct_value["path_data"]
                if name_data in name_file:
                    tag = data_strct_key
                    sheet_index = data_strct_value["sheet_page"]
                    type_format = data_strct_value["type"].split("|")
                    if isinstance(sheet_index,list):
                        if len(sheet_index) > 1:
                            df_start = self.func_load_data(type_format,name_file,self.cn.bucket_path+name_file,sheet_index[0])
                            for pages_sheet in range(1,len(sheet_index)):
                                df_extra = self.func_load_data(type_format,name_file,self.cn.bucket_path+name_file,pages_sheet)
                                df_start = pd.concat([df_start, df_extra],axis=0).reset_index(drop=True)
                            
                            df_start = df_start.rename(columns=lambda x: str(x).replace(' ', '_'))
                            self.raw_data[tag] = [df_start, tag]
                    else:
                        data = self.func_load_data(type_format,name_file,self.cn.bucket_path+name_file,sheet_index)
                        data = data.rename(columns=lambda x: str(x).replace(' ', '_'))
                        self.raw_data[tag] = [ data , tag]

    def get_load_data(self):
        return self.raw_data

    def get_only_data(self,tag):
        return self.raw_data[tag][0]

    def transformation(name_tag):
        def sub_transformation(func):
            def wrapper(self):
                data =  self.get_only_data(name_tag)
                result = func(self, data)
                self.upload_transformation(name_tag,result)
                return result
            return wrapper
        return sub_transformation
    
    def upload_transformation(self,name_tag_data,df_tf):
        data_all = self.get_load_data()
        data_all[name_tag_data][0] = df_tf
    
    def upload_data(self,cx_bigquery):
        data_upload = self.get_load_data()
        cx_bigquery.upload_data(data_upload)
    
    def func_load_data(self,type_format,name_file,path_archive,sheet_page):
        if len(type_format) > 1:
            format_archive = name_file.split("/")[-1].split(".")[-1]
        else:
            format_archive = type_format[0]
                
        if "xlsx" in format_archive:           
            return pd.read_excel(path_archive,sheet_name=sheet_page)
        if "csv" in format_archive:
            return pd.read_csv(path_archive)