import os

CONNECTION_VAR = 1 # 0 = PRODUCTION / 1 = TESTING

DIRNAME_CREDENTIALS = "credentials"
DIRNAME_UPLOAD_BUCKET  = "upload"
CONFIG_NAME_PRODUCTION = "connection_production.ini"
CONFIG_NAME_TEST = "connection_testing.ini"

PATH_CREDENTIALS = os.path.join(os.getcwd(), f"{DIRNAME_CREDENTIALS}")
PATH_UPLOAD_BUCKET = os.path.join(os.getcwd(), f"{DIRNAME_UPLOAD_BUCKET}")

def convert_sheet_url(sheet_id):
    url = f"https://docs.google.com/spreadsheets/d/e/{sheet_id}/pub?output=csv"
    return url

#name - format
type_archives = {
    "xlsx"  : "xlsx",
    "csv"   : "csv",
    "auto"  : "xlsx|csv"
}
