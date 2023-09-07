import pandas as pd
import dataflowutil.config.extra_var as extra_v

class LoadData:
    def __init__(self,connection):
        self.cn = connection
        self.list_data = {}
        self.data = pd.read_csv(extra_v.convert_sheet_url(self.cn.id_load_bucket))
        self.load_data()

    def load_data(self):
        for index,row in self.data.iterrows():
            tag_name = row["TAG / DB_NAME"]
            path_data = row["PATH_DATA"]
            sheet_page = row["SHEET_PAGE"]
            type_data = row["TYPE"]

            if isinstance(sheet_page,str):
                if "-" in sheet_page:
                    split_sheets = sheet_page.split("-")
                    sheet_page = [int(new_sheets) for new_sheets in split_sheets]
                else:
                    sheet_page = int(sheet_page)
                    
            self.list_data[tag_name] = {
                "path_data" : path_data,
                "sheet_page" : sheet_page,
                "type" :  extra_v.type_archives[type_data]
            }
        
    def get_data(self):
        return self.list_data


