import configparser
import dataflowutil.config.extra_var as extra_var

list_connections = [extra_var.CONFIG_NAME_PRODUCTION,extra_var.CONFIG_NAME_TEST]

class LoadConnection():
    def __init__(self):
        self.select_connection = list_connections[extra_var.CONNECTION_VAR]

        self.credentials_path   = str
        self.bucket_path         = str
        self.bucket_name         = str
        self.project_id          = str
        self.name_db_bigquery    = str
        self.id_load_bucket      = str
        self.id_upload_data_to_bucket = str

        self.config = configparser.ConfigParser()
        self.config.read(extra_var.DIRNAME_CREDENTIALS+"/"+self.select_connection)
        self.load_var_connection()

    def load_var_connection(self):
        self.credentials_path    = self.config.get('Config.Credentials', 'credentials_path')
        self.bucket_path         = self.config.get('Config.Bucket', 'bucket_path')
        self.bucket_name         = self.config.get('Config.Bucket', 'bucket_name')
        self.project_id          = self.config.get('Config.BigQuery', 'project_id')
        self.name_db_bigquery    = self.config.get('Config.BigQuery', 'name_db_bigquery')   
        self.id_load_bucket             = self.config.get('Config.SpreadSheets', 'id_load_bucket')
        self.id_upload_data_to_bucket   = self.config.get('Config.SpreadSheets', 'id_upload_data_to_bucket')
    
