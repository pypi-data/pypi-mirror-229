import requests
from io import StringIO, BytesIO
import datetime, time
import warnings
warnings.filterwarnings('ignore')
import snowflake.connector as sf
from snowflake.connector.pandas_tools import write_pandas
import base64
import logging,json, pygsheets, pandas as pd
import chardet
from zipfile import BadZipFile
import re

import os.path
from dotenv import load_dotenv #code  for env variables

load_dotenv('/mnt/work-related/cart-ds-python/data-automation/locked/Credentials.env') #code  for env variables
user1 = os.getenv('snowflake_python_user')  #code  for env variables
pw1 = os.getenv('snowflake_python_pwd')  # encode_pass() #code  for env variables


# Azure AD app registration credentials

client_id = '0dc13d7a-0592-425b-b408-cf270eb0f9fa'
client_secret = 'c1c8Q~0VNhHkM_gAdgZ-2p4M2Uj~l6ow~9qcZbsn'
tenant_id = '4bbc6d7f-bc90-42d2-993d-de418d471e27'

# SharePoint Online site URL and library name

site_id = 'c48d6e7d-9de8-4767-b589-8d1b6cb5e1c4'
library_name = 'Documents'
drive_id = 'b!fW6NxOidZ0e1iY0bbLXhxCQ-VXsHYFxEnMW52HZ4o1U5MamdNKwASZZ8znxZF74H'

# Authenticate and get an access token
auth_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
    'scope': 'https://graph.microsoft.com/.default'
}
response = requests.post(auth_url, data=data)
access_token = response.json()['access_token']

headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/octet-stream',
}

class get_googlesheets_data:
  def __init__(self,name,sheet):
    global new_columns, old_columns,file
    gc = pygsheets.authorize(service_account_file= '/mnt/snowflake-reports/keys/gdrive_secret.json')

    sh = gc.open(name)
    wks = sh.worksheet_by_title(sheet)
    data = wks.get_as_df()

    new_columns = []
    old_columns = data.columns.tolist()

    for item in old_columns:
      if type(item) == str:
        new_item = item.replace(" ($)","_").replace(" \+ ","_").replace(":","_").replace(" ","_").replace(".","").replace("(","").replace(")","").replace("/","_").replace(",","_").\
        replace("-","_").replace("%","per").replace('unnamed__',"").lstrip('0123456789').replace('unique','a_unique').lower().replace('#','').replace('&','_').replace('___','_').replace('__','_')
        new_columns.append(new_item)
      elif type(item) == datetime.datetime:
        new_item = item.strftime("%b_%Y").lower()
        new_columns.append(new_item)
        
    try: 
      data = data.drop('',axis=1)
    except KeyError:
      pass

    for col in data.columns:
      try:
        data[col] = data[col].astype(str)
      except (ValueError,KeyError):
        continue

    for i in range(len(new_columns)):
      new_columns[i] = new_columns[i].lower()

    data.columns = new_columns

    drop_cols = ['',',','_']
    data = data.drop(drop_cols, axis=1, errors = 'ignore')
    data = data.loc[:,~data.columns.duplicated()]
    new_columns = data.columns.tolist()

    new_columns = data.columns

    sf_cols = []
    sf_tr = []

    for i in range(len(new_columns)):
      new_value = new_columns[i].lower() + ' ' + 'string'
      transform = 'nullif(' + new_columns[i].lower() + ',\'\') as ' + new_columns[i].lower()        # + ' ' + 'string'
      sf_cols.append(new_value)
      sf_tr.append(transform)

    sf_query = "\n,".join(sf_cols)
    sf_tr_query = "\n,".join(sf_tr)

    return data, sf_query, sf_tr_query


class get_sharepoint_data:
  def __init__(self,search_query,relative_url,date_col,sheet_name,skip_rows):
    global new_columns, old_columns,file,data,df_filtered,df
    
    self.api_url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/items/root:/{relative_url}:/children'
    
    response = requests.get(self.api_url, headers=headers)

    data = response.json()

    # print(data)

    df = pd.DataFrame(data = data['value'].copy())
    cols = df.columns.to_list()
    df_filtered = df[df[cols]['name'].str.lower().str.contains(search_query.lower())].sort_values('lastModifiedDateTime',ascending=False).head(1).reset_index()

    file_name = df_filtered['name'].values[0]
    self.api_url_content = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/items/root:/{relative_url}/{file_name}:/content'

    print(file_name)

  #   df_content = pd.read_csv(StringIO(content_response.text))

    output = StringIO()
    file_n = requests.get(self.api_url_content,headers=headers)

    try:
      output = StringIO()
      data = pd.read_csv(StringIO(file_n.content.decode('utf-8')),skiprows=skip_rows)
    except (UnicodeDecodeError,BadZipFile) as err:
      print(err,'\nNow processing as excel file')
      output = BytesIO()
      dict = pd.read_excel(BytesIO(file_n.content),sheet_name=[sheet_name],engine='openpyxl',skiprows=skip_rows)
      data = dict[sheet_name]

    data['insertion_datetime'] = datetime.datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')
    
    new_columns = []
    old_columns = data.columns.tolist()

    for item in old_columns:
      if type(item) == str:
        new_item = re.sub('^_|_$','',item.replace(" ($)","_").replace('\n','_').replace(" \+ ","_").replace(":","_").replace(" ","_").replace(".","")\
        .replace("(","").replace(")","").replace("/","_").replace(",","_").\
        replace("-","_").replace('__','_').replace('___','_').replace("%","per").replace('unnamed__',"").lstrip('0123456789')\
        .replace('unique','a_unique').lower().replace('#','').replace('?','').replace('^_','').replace('_$',''))
        new_columns.append(new_item)
      elif type(item) == datetime.datetime:
        new_item = item.strftime("%b_%Y").lower()
        new_columns.append(new_item)
        
    try: 
      data = data.drop('',axis=1)
    except KeyError:
      pass

    for col in data.columns:
      try:
        data[col] = data[col].astype(str)
      except (ValueError,KeyError):
        continue

    for i in range(len(new_columns)):
      new_columns[i] = new_columns[i].lower()

    data.columns = new_columns

    drop_cols = ['',',','_']
    data = data.drop(drop_cols, axis=1, errors = 'ignore')
    data = data.loc[:,~data.columns.duplicated()]
    new_columns = data.columns.tolist()

    sf_cols = []
    sf_tr = []

    for i in range(len(new_columns)):
      new_value = new_columns[i].lower() + ' ' + 'string'
      transform = 'nullif(' + new_columns[i].lower() + ',\'nan\') as ' + new_columns[i].lower()        # + ' ' + 'string'
      sf_cols.append(new_value)
      sf_tr.append(transform)

    sf_query = "\n,".join(sf_cols)
    sf_tr_query = "\n,".join(sf_tr)

    return data, sf_query, sf_tr_query


class load_to_snowflake:
  def __init__(self,data,database,schema,role,table_name,sf_query,sf_tr_query):
    print('Table Name: {}'.format(database + '.' + schema + '.' + table_name))
    print('Start: load to Snowflake...')
    data.reset_index(drop=True, inplace=True)
    print('opening snowflake...')

    if 'airbyte' in role.lower():
      warehouse = 'airbyte_warehouse'
    else:
      warehouse = 'cart_dev_compute_wh'

    cnn = sf.connect(
            user= user1,
            password = pw1,
            account = 'og64234.us-central1.gcp',
            warehouse = warehouse,
            database = database,
            role = role,
            schema = schema)
    
    cnn.cursor().execute(
        "CREATE SCHEMA IF NOT EXISTS " + database + "." + schema
    ) 
    
    cnn.cursor().execute(
      "CREATE OR REPLACE TABLE " +
      table_name + "("  + sf_query + ")"
    )

    success, nchunks, nrows, _ = write_pandas(cnn, data, table_name, on_error = "CONTINUE",quote_identifiers=False)
    print(str(success) + ', ' + str(nchunks) + ', ' + str(nrows))

    cnn.cursor().execute(
      "CREATE OR REPLACE TABLE " + table_name + " as" + "\nselect\n" + sf_tr_query + '\nfrom\n' + table_name 
    )

    cnn.close()
    print('Done: Load to Snowflake\n\n')
