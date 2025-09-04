import os
import json
import time
import requests
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from df_database_models.db_conn import get_rds_db_session, get_aumine_db_session
from df_database_models.models import Source_System, Line_Item, Line_Item_Type, Invoice, broker_portal_error_log
from df_database_models.db_utils import  generate_uuid, convert_timestamps, generate_uuid, query_update_dict, get_record, call_sp
from secrets_manager import get_secret
from datetime import datetime
import pandas as pd
import asyncio
from adf_pyutils.clm_wrapper import common_logger

print("Class job is executing")

## Fetch SQS producer Parameters from aws secret manager
sqs_producer_secret = json.loads(get_secret(
         secret_name=os.environ["SQS_PRODUCER_SECRET_ID"], region_name=os.environ["AWS_REGION"]))
sqs_producer_access_key = sqs_producer_secret["access_key"]
sqs_policy_update_url = os.environ["SQS_POLICY_UPDATE_URL"]

async def log_msg(func,**kwargs):
    await asyncio.to_thread(func,**kwargs)

def call_session_engine(source_system=None, identifier=None):

    if source_system:
        rds_secret_name=os.environ["RDS_SECRETS_MANAGER_ID"]
        region_name=os.environ["AWS_REGION"]
        rds_host_nm=os.environ['RDS_HOST']

        if identifier == 'ref':
            rds_db_nm=os.environ['RDS_REF_DB_NAME']
        elif identifier == 'raw':
            rds_db_nm=os.environ['RDS_RAW_DB_NAME']
        elif identifier == 'refined':
            rds_db_nm=os.environ['RDS_REFINED_DB_NAME']
        else:
            rds_db_nm=os.environ['RDS_DB_NAME']
            

        if source_system.lower() == 'aumine_aff':
            #Calling the Aumine engine to establish a connection to PAS Source System - Aumine_AFF
            aumine_secret_name=os.environ["AUMINE_AFF_SECRETS_MANAGER_ID"]
            aumine_engine=get_aumine_db_session(aumine_secret_name, region_name)

        elif source_system.lower() == 'aumine_aum':
            #Calling the Aumine engine to establish a connection to PAS Source System - Aumine_AUM
            aumine_secret_name=os.environ["AUMINE_AUM_SECRETS_MANAGER_ID"]
            aumine_engine=get_aumine_db_session(aumine_secret_name, region_name)

        #Calling the Db session Object to establish a connection to Data Foundation Schema
        session=get_rds_db_session(rds_secret_name,region_name,rds_host_nm,rds_db_nm)

        return session, aumine_engine

# lookup into aumine aff: read data from lineitem table in Aumine 
# lookup into aumine aff
def lookup_aumine(config=None, id=None):
    source_system = config['source_system']
    if source_system:
        if source_system.lower() in ['aumine_aff','aumine_aum']:
            df = pd.read_sql(f"""
                SELECT 
                li.line_item as df_line_item_id,
                '' as df_invoice_id,
                li.invoice_header as source_invoice_id,
                ih.invoice_no as invoice_number,
                CASE 
                    WHEN LOWER(li.line_item_type) = 'net premium' THEN 'Base Premium'
                    WHEN LOWER(li.line_item_type) IN ('federal excise tax', 'ky local government premium tax', 'municipal tax', 'other taxes / fees / filings', 'prem tax', 'surplus lines tax') THEN 'Tax'
                    WHEN LOWER(li.line_item_type) = 'revenue adjustment' THEN 'Discount'
                    WHEN LOWER(li.line_item_type) IN ('broker fee', 'dental nsdp purchasing group fee', 'dummy', 'engineering fee', 'fee in lieu of commission', 'filing fee', 'finance fee', 'fl insurance guaranty association', 'fl insurance guaranty association emergency assessment', 'fl insurance guaranty association regular assessment', 'fl insurance guaranty association special assessment', 'florida hurricane cat fund', 'in comp fund', 'inspection fee', 'ky firefighters & law enforcement foundation program fund', 'la comp fund', 'levy fee', 'loss control services', 'nj property & liability insurance guaranty fund', 'other fee', 'policy administrative charge', 'pr property and casualty ins. guaranty assc', 'service fee', 'stamp duty', 'stamping fee', 'third party fee') THEN 'Fee'
                    WHEN LOWER(li.line_item_type) IN ('ca surcharge', 'ky basic surcharge', 'ky handling surcharge', 'ky municipal surcharge', 'or surcharge', 'state surcharge', 'va surcharge', 'wa surcharge', 'wv insurance premium surcharge') THEN 'Surcharge'
                    WHEN LOWER(li.line_item_type) IN ('aum commission', 'client commission') THEN 'Commission'  
                END AS line_item_type,
                li.line_item_type as source_line_item_type,
                li.line_item_type as description,
                (li.line_item_amt - li.receivable_paid_amt) AS amount,
                '{source_system}' AS source_system
                FROM 
                Aumine.Line_item AS li
                JOIN Aumine.Invoice_Header ih 
                ON li.invoice_header = ih.invoice_header
                    WHERE  li.line_item = {id}
                    """, con=aumine_engine)
        else:
            df=None
    else:
        df=None

    if(len(df)>0):
        return df.to_dict('records')[0]
    else:
        return None

# Main function to process incoming configuration data
async def consume_lambda(config=None):
    asyncio.create_task(log_msg(common_logger,log_messages='consume lambda function invoking'))
    now = datetime.now()
    start_timestamp = datetime.timestamp(now)
    asyncio.create_task(log_msg(common_logger,log_messages=f'Processing to DB @ {now} | {datetime.timestamp(now)}'))

    try:
        asyncio.create_task(log_msg(common_logger,log_messages='Config',api_response=convert_timestamps(config)))
        config_dicts = config if type(config) is dict else json.loads(str(config))
        if type(config_dicts) == list:
            pass
        else:
            config_dicts = [config_dicts] # Ensure config_dicts is a list
        for config_dict in config_dicts:
            id = config_dict['line_item'] # Get the lineitem from config data 
            source_system = config_dict['source_system'].lower()
            if(id):
                fk_flag = 1
                print("Calling call_session_engine Function ")
                global session, aumine_engine
                session, aumine_engine = call_session_engine(source_system=source_system)

                aumine_lineitem_summary_dict = lookup_aumine(config_dict, id) #define dict for lookup data
                
                if(aumine_lineitem_summary_dict):
                    asyncio.create_task(log_msg(common_logger,log_messages=f'Initial {source_system} Lineitem Summary dict:',api_response=convert_timestamps(aumine_lineitem_summary_dict)))

                    #Fetch Source SyStem Id from Data Foundation
                    source_system = aumine_lineitem_summary_dict.get("source_system")
                    source_system_record = (query.first() if (query := get_record(session,model=Source_System,column_name='source_system',value=source_system)) is not None else None)
                    if source_system_record:
                        aumine_lineitem_summary_dict['df_source_system_id'] = source_system_record.df_source_system_id

                    #Fetch LineItem Type Id from Data Foundation
                    line_item_type = aumine_lineitem_summary_dict.get("line_item_type")
                    line_item_type_record = (query.first() if (query := get_record(session,model=Line_Item_Type,column_name='line_item_type',value=line_item_type)) is not None else None)
                    if line_item_type_record:
                        aumine_lineitem_summary_dict['df_line_item_type_id'] = line_item_type_record.df_line_item_type_id

                    #Assign a variable to source_invoice_id, line_item_id and source_system_id from Dictionary Object
                    source_invoice_id = aumine_lineitem_summary_dict.get("source_invoice_id") 
                    df_line_item_id = aumine_lineitem_summary_dict.get("df_line_item_id") 
                    df_source_system_id = aumine_lineitem_summary_dict.get("df_source_system_id") 
                    invoice_number = aumine_lineitem_summary_dict.get("invoice_number")

                    #Fetch invoice and lineitem data from Data Foundation
                    invoice_record = get_record(session,model=Invoice,column_name='source_invoice_id',value=source_invoice_id,df_source_system_id=df_source_system_id)
                    lineitem_record = get_record(session,model=Line_Item,column_name='df_line_item_id',value=df_line_item_id,df_source_system_id=df_source_system_id)

                    self_invoice = (invoice_record.first() if invoice_record is not None else None)
                    self_lineitem = (lineitem_record.first() if lineitem_record is not None else None)

                    asyncio.create_task(log_msg(common_logger,log_messages=f'self invoice - {self_invoice}'))
                    asyncio.create_task(log_msg(common_logger,log_messages=f'self lineitem - {self_lineitem}'))
                    asyncio.create_task(log_msg(common_logger,log_messages=f'Changed {source_system} Aumine Lineitem Summary dict:',api_response=convert_timestamps(aumine_lineitem_summary_dict)))
                    
                    fk_flag = 1
                    if(self_invoice is None):
                        asyncio.create_task(log_msg(common_logger,log_messages='Invoice does not exist in Data Foundation'))
                        aumine_lineitem_summary_dict['df_invoice_id'] = generate_uuid(
                            str(aumine_lineitem_summary_dict['source_invoice_id'] or '') + 
                            str(aumine_lineitem_summary_dict['invoice_number'] or ''), 
                            df_source_system_id
                        )
                        session.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
                        fk_flag = 0
                        asyncio.create_task(log_msg(common_logger,log_messages='FK disabled'))
                    else:
                        asyncio.create_task(log_msg(common_logger,log_messages='invoice exists in Data Foundation'))
                        aumine_lineitem_summary_dict['df_invoice_id']=self_invoice.df_invoice_id
                    if (self_lineitem is None):
                        asyncio.create_task(log_msg(common_logger,log_messages='Lineitem does not exist in Data Foundation'))
                        asyncio.create_task(log_msg(common_logger,log_messages='Aumine Lineitem Summary dict Insert',api_response=convert_timestamps(aumine_lineitem_summary_dict)))
                        session.add(Line_Item.from_dict(cls=Line_Item, d=aumine_lineitem_summary_dict))
                        session.commit()
                        if fk_flag == 0:
                            session.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
                            session.commit()
                            fk_flag = 1
                            asyncio.create_task(log_msg(common_logger,log_messages='FK enabled'))
                        asyncio.create_task(log_msg(common_logger,log_messages=f'Inserted to DB @ {now} | {datetime.timestamp(now)}'))
                    else:
                        asyncio.create_task(log_msg(common_logger,log_messages='Lineitem exists in Data Foundation'))
                        asyncio.create_task(log_msg(common_logger,log_messages='Aumine Lineitem Summary dict Update',api_response=convert_timestamps(aumine_lineitem_summary_dict)))
                        lineitem_record.update(query_update_dict(obj=Line_Item, dict=aumine_lineitem_summary_dict))
                        asyncio.create_task(log_msg(common_logger,log_messages=f'Updated in DB @ {now} | {datetime.timestamp(now)}'))
                        session.commit() 
            else:
                    error_log = {
                        "df_line_item_id" : id,
                        "error_message" : "No record found after lookup" 
                    }
                    asyncio.create_task(log_msg(common_logger,log_messages='No record found after lookup'))
        now = datetime.now()
        end_timestamp = datetime.timestamp(now)
        asyncio.create_task(log_msg(common_logger,log_messages=f'execution_time: {end_timestamp} - {start_timestamp}'))
    except SQLAlchemyError as e:
        asyncio.create_task(log_msg(common_logger,log_messages='Error',api_response=e))
        session.rollback()
        raise e


def handle(event, context):
    start_time = time.time()
    print("Handle function is called")
    for record in event['Records']:
        payload = record["body"]
        asyncio.run(consume_lambda(config=payload))
    end_time = time.time()
    return {
        "execution_time_sec": end_time - start_time 
    }

if __name__ == '__main__':
    handle({'Records': [{'body': '{"line_item":"1003093977"}'}]}, None)
    # handle({'Records': [{'body': '[{ "source_policy_id": "2002569486", "parent_policy_id": "2002254485", "policy_type": "renewal"}]'}]}, None)
    # handle({'Records': [{'body': '[{"source_policy_id":"2002573640"},{"source_policy_id":"2002573647"},{"source_policy_id":"2002573649"}]'}]}, None)
