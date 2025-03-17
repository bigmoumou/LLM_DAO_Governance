import warnings
warnings.simplefilter("ignore", ResourceWarning)

from subgrounds import Subgrounds
from datetime import datetime
import pandas as pd
import pytz
import time

sg = Subgrounds()
api_key = 'input_your_api_key_here'
url_postfix = 'input_your_subgraph_id_here'

def timestamp_to_utc(timestamp):
    utc_time = datetime.fromtimestamp(timestamp, pytz.UTC)
    return utc_time.strftime('%Y-%m-%d %H:%M:%S UTC')

def fetch_protocol_metrics_treasury(start_timestamp=None, end_timestamp=None):
    subgraph = sg.load_subgraph(f'https://gateway.thegraph.com/api/{api_key}/subgraphs/id/{url_postfix}')
    
    # create query
    where_clause = {}
    if start_timestamp is not None:
        where_clause['timestamp_gte'] = start_timestamp
    if end_timestamp is not None:
        where_clause['timestamp_lt'] = end_timestamp
    
    treasuryAssets = subgraph.Query.treasuryAssets(
        first=1000,           # get 1000 records at a time
        where=where_clause,   # time range condition
        orderBy="timestamp",  # sort by timestamp
        orderDirection="asc"  # ascending order
    )

    result = sg.query([
        treasuryAssets.id,
        treasuryAssets.timestamp,
        treasuryAssets.token,
        treasuryAssets.tokenBalance
    ])

    return result

def get_treasury_assets():
    # intialize start time to 2021-10-01 (KlimaDAO launch date)
    start_time = int(datetime(2021, 10, 1, tzinfo=pytz.UTC).timestamp())
    # set end time to current time
    end_time = int(datetime.now(pytz.UTC).timestamp())
    # set time interval to 90 days
    interval = 90 * 24 * 60 * 60
    
    final_data = [[], [], [], []]
    batch = 1
    
    current_start = start_time
    while current_start < end_time:
        current_end = min(current_start + interval, end_time)
        print(f'\nfetching data from batch {batch}...')
        print(f"time range: from {timestamp_to_utc(current_start)} to {timestamp_to_utc(current_end)}")
        
        # fetch data from subgraph
        metrics = fetch_protocol_metrics_treasury(current_start, current_end)

        if len(metrics[0]) > 0:
            final_data[0].extend(metrics[0])
            final_data[1].extend(metrics[1])
            final_data[2].extend(metrics[2])
            final_data[3].extend(metrics[3])
            print(f'successfully fetched {len(metrics[0])} records')
        else:
            print('no data fetched')
        
        # update current_start
        current_start = current_end
        batch += 1
        
        # add a delay to avoid hitting the rate limit
        time.sleep(1)

    # save data to csv file
    if len(final_data[0]) > 0:
        print('\nsaving data to csv file...')
        df = pd.DataFrame({
            'id': final_data[0], 
            'timestamp': final_data[1], 
            'token': final_data[2], 
            'tokenBalance': final_data[3]
        })

        mapping = {
            '0x251ca6a70cbd93ccd7039b6b708d4cb9683c266c': 'NBO/KLIMA',    # 912
            '0x9803c7ae526049210a1725f7487af26fe2c24614': 'BCT/KLIMA',    # 899
            '0x1e67124681b402064cd0abe8ed1b5c79d2e02f64': 'BCT/USDC',     # 899
            '0x2b3ecb0991af0498ece9135bcd04013d7993110c': 'UBO',          # 912
            '0xaa7dbd1598251f856c12f63557a4c4397c253cea': 'MCO2',         # 899
            '0x5400a05b8b45eaf9105315b4f2e31f806ab706de': 'UBO/KLIMA',    # 912
            '0xb2d0d5c86d933b0acefe9b95bec160d514d152e1': 'NCT/KLIMA',    # 899
            '0xd838290e877e0188a4a44700463419ed96c16107': 'NCT',          # 899
            '0x5786b267d35f9d011c4750e0b0ba584e1fdbead1': 'KLIMA/USDC.e', # 912
            '0x64a3b8ca5a7e406a78e660ae10c7563d9153a739': 'MCO2/KLIMA',   # 912
            '0x82b37070e43c1ba0ea9e2283285b674ef7f1d4e2': 'CCO2',         # 899
            '0x6bca3b77c1909ce1a4ba1a20d1103bde8d222e48': 'NBO',          # 912
            '0x2791bca1f2de4661ed88a30c99a7a9449aa84174': 'USDC.e',       # 912
            '0x4e78011ce80ee02d2c3e649fb657e45898257815': 'Klima',        # 912
            '0x2f800db0fdb5223b3c3f354886d907a671414a7f': 'BCT'           # 912
        }
        df['token_name'] = df['token'].map(mapping)

        df.to_csv('protocol_metrics_treasury_all.csv', index=False)
        print(f'totally get {len(final_data[0])} records')
    else:
        print('no data fetched')

if __name__ == "__main__":
    get_treasury_assets()
