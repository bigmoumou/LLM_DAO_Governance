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

def fetch_protocol_metrics_supply(min_timestamp=None):
    subgraph = sg.load_subgraph(f'https://gateway.thegraph.com/api/{api_key}/subgraphs/id/{url_postfix}')
    
    where_clause = {}
    if min_timestamp is not None:
        where_clause['timestamp_gt'] = min_timestamp  # Fetch only data with timestamp greater than the last batch's final timestamp
    
    protocol_metrics_query = subgraph.Query.protocolMetrics(
        first=1000,           # Fetch 1000 records per batch
        where=where_clause,   # Add time condition (if any)
        orderBy="timestamp",  # Sort by timestamp
        orderDirection="asc"  # Ascending order
    )

    # Select required fields
    result = sg.query([
        protocol_metrics_query.id,
        protocol_metrics_query.timestamp,
        protocol_metrics_query.klimaCirculatingSupply,
        protocol_metrics_query.sKlimaCirculatingSupply,
        protocol_metrics_query.totalSupply,
        protocol_metrics_query.totalKlimaUnstaked,
        protocol_metrics_query.klimaPrice,
        protocol_metrics_query.marketCap,
        protocol_metrics_query.klimaIndex,
        protocol_metrics_query.treasuryBalanceKLIMA,
        protocol_metrics_query.treasuryBalanceUSDC,
        protocol_metrics_query.treasuryCarbon,
        protocol_metrics_query.treasuryCarbonCustodied,
        protocol_metrics_query.treasuryMarketValue,
        protocol_metrics_query.treasuryUSDCInLP,
        protocol_metrics_query.totalValueLocked,
        protocol_metrics_query.totalKlimaInLP,
        protocol_metrics_query.runwayCurrent,
    ])
    return result

def get_protocol_metrics():
    last_timestamp = None  # Used as pagination condition
    batch = 1
    final_data = [[] for _ in range(18)]

    while True:
        print(f"\nFetching batch {batch} data...")
        # Fetch a batch of data using min_timestamp query
        metrics = fetch_protocol_metrics_supply(last_timestamp)
        
        # If no more data, exit loop
        if len(metrics[0]) == 0:
            print("No more data available")
            break
        else:
            # Append each column's data to final_data
            for i in range(len(final_data)):
                final_data[i].extend(metrics[i])
        
        # Display the time range for this batch
        first_time = timestamp_to_utc(metrics[1][0])
        last_batch_timestamp = metrics[1][-1]
        last_time = timestamp_to_utc(last_batch_timestamp)
        print(f"Successfully fetched {len(metrics[0])} records")
        print(f"Time range: {first_time} to {last_time}")
        
        # Update last_timestamp to the final timestamp of the current batch
        last_timestamp = last_batch_timestamp
        batch += 1
        
        # Add delay to avoid too frequent requests
        time.sleep(1)

    # Save final_data to CSV file
    print('Saving data to CSV file...')
    df = pd.DataFrame({
        'id': final_data[0],
        'timestamp': final_data[1],
        'klimaCirculatingSupply': final_data[2],
        'sKlimaCirculatingSupply': final_data[3],
        'totalSupply': final_data[4],
        'totalKlimaUnstaked': final_data[5],
        'klimaPrice': final_data[6],
        'marketCap': final_data[7],
        'klimaIndex': final_data[8],
        'treasuryBalanceKLIMA': final_data[9],
        'treasuryBalanceUSDC': final_data[10],
        'treasuryCarbon': final_data[11],
        'treasuryCarbonCustodied': final_data[12],
        'treasuryMarketValue': final_data[13],
        'treasuryUSDCInLP': final_data[14],
        'totalValueLocked': final_data[15],
        'totalKlimaInLP': final_data[16],
        'runwayCurrent': final_data[17],
    })

    # Add datetime column: convert timestamp to UTC time
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s', utc=True)
    df.to_csv('protocol_metrics_all.csv', index=False)

if __name__ == "__main__":
    get_protocol_metrics()
