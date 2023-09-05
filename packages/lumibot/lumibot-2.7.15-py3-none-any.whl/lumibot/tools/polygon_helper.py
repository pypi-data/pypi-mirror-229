import os
import time
from datetime import date, datetime, timedelta, timezone

import pandas as pd
import polygon
from polygon import RESTClient

from lumibot import LUMIBOT_CACHE_FOLDER, LUMIBOT_DEFAULT_TIMEZONE
from lumibot.entities import Asset

WAIT_TIME = 60


def get_next_date(date, timespan, num_points):
    if timespan == "minute":
        delta = timedelta(minutes=num_points)
    elif timespan == "hour":
        delta = timedelta(hours=num_points)
    else:  # assuming 'day'
        delta = timedelta(days=num_points)

    return date + delta


def get_price_data_from_polygon(
    api_key: str,
    asset: Asset,
    start: datetime,
    end: datetime,
    timespan: str = "minute",
    has_paid_subscription: bool = False,
    quote_asset: Asset = None,
):
    print(f"\nGetting pricing data for {asset} / {quote_asset} from Polygon...")

    df_all = None
    df_csv = None

    LUMIBOT_POLYGON_CACHE_FOLDER = os.path.join(LUMIBOT_CACHE_FOLDER, "polygon")
    cache_filename = f"{asset.asset_type}_{asset.symbol}_{timespan}.csv"

    # If It's an option then also add the expiration date, strike price and right to the filename
    if asset.asset_type == "option":
        if asset.expiration is None:
            raise ValueError(
                f"Expiration date is required for option {asset} but it is None"
            )

        # Make asset.expiration datetime into a string like "YYMMDD"
        expiry_string = asset.expiration.strftime("%y%m%d")

        cache_filename = f"{asset.asset_type}_{asset.symbol}_{expiry_string}_{asset.strike}_{asset.right}_{timespan}.csv"

    cache_file = os.path.join(LUMIBOT_POLYGON_CACHE_FOLDER, cache_filename)

    # Check if we already have data for this asset in the csv file
    if os.path.exists(cache_file):
        df_csv = pd.read_csv(cache_file, index_col="datetime")
        df_csv.index = pd.to_datetime(df_csv.index)
        df_csv = df_csv.sort_index()
        csv_start = df_csv.index[0]
        csv_end = df_csv.index[-1]

        # Check if the index is already timezone aware
        if df_csv.index.tzinfo is None:
            # Set the timezone to UTC
            df_csv.index = df_csv.index.tz_localize("UTC")

        # Check if we have data for the full range
        if csv_start <= start and csv_end >= end:
            # TODO: Also check if we are missing data in the middle of the range
            return df_csv

        # Check if we have data for the start date
        if csv_start <= start:
            cur_start = csv_end
        else:
            cur_start = start

        df_all = df_csv.copy()
    else:
        cur_start = start

    # Get the data from Polygon
    first_iteration = True
    last_cur_start = None
    earliest_date_requested = None
    while True:
        # Check if df_all exists and is not empty
        if df_all is not None and len(df_all) > 0:
            # Check if we need to get more data
            last_row = df_all.iloc[-1]
            first_row = df_all.iloc[0]

            # Check if we have all the data we need
            if last_row.name >= end and first_row.name <= start:
                # TODO: Also check if we are missing data in the middle of the range
                # We have all the data we need, break out of the loop
                break
            elif last_row.name <= cur_start and not first_iteration:
                # Polygon doesn't have any more data for this asset, break out of the loop
                break
            # If it's an option then we need to check if the last row is past the expiration date
            elif (
                asset.asset_type == "option"
                and last_row.name.date() >= asset.expiration
                and first_row.name <= start
            ):
                # We have all the data we need, break out of the loop
                break
            else:
                # We need to get more data. Update cur_start and then get more data
                # TODO: Also check if we are missing data in the middle of the range
                if earliest_date_requested is None or start < earliest_date_requested:
                    cur_start = start
                else:
                    cur_start = last_row.name

                # If we don't have a paid subscription, we need to wait 1 minute between requests because of
                # the rate limit
                if not has_paid_subscription and not first_iteration:
                    print(
                        f"\nSleeping {WAIT_TIME} seconds getting pricing data for {asset} from Polygon because "
                        f"we don't have a paid subscription and we don't want to hit the rate limit. If you want to "
                        f"avoid this, you can get a paid subscription at https://polygon.io/pricing and "
                        f"set `polygon_has_paid_subscription=True` when starting the backtest.\n"
                    )
                    time.sleep(WAIT_TIME)

        # Make sure we are not in an endless loop
        if last_cur_start is not None and last_cur_start == cur_start and not first_iteration:
            # We already got data for this date, break out of the loop
            break
        last_cur_start = cur_start

        # RESTClient connection for Polygon Stock-Equity API; traded_asset is standard
        polygon_client = RESTClient(api_key)

        # We need to subtract 1 minute because of a bug in polygon - does this exist in polygon-api-client?
        poly_start = cur_start - timedelta(minutes=1)
        poly_end = end

        # Update earliest_date_requested
        if earliest_date_requested is None or earliest_date_requested > poly_start:
            earliest_date_requested = poly_start

        # Crypto Asset for Backtesting
        if asset.asset_type == "crypto":
            quote_asset_symbol = quote_asset.symbol if quote_asset else "USD"
            symbol = f"X:{asset.symbol}{quote_asset_symbol}"

        # Stock-Equity Asset for Backtesting
        elif asset.asset_type == "stock":
            symbol = asset.symbol

        # Forex Asset for Backtesting
        elif asset.asset_type == "forex":
            # If quote_asset is None, throw an error
            if quote_asset is None:
                raise ValueError(
                    f"quote_asset is required for asset type {asset.asset_type}"
                )

            symbol = f"C:{asset.symbol}{quote_asset.symbol}"

        # Option Asset for Backtesting
        elif asset.asset_type == "option":
            # TODO: First check if last_row.name is past the expiration date. If so, break out of the loop or something (this will save us a lot of time)

            # Query for the historical Option Contract ticker backtest is looking for
            contracts = list(polygon_client.list_options_contracts(
                underlying_ticker=asset.symbol,
                expiration_date=asset.expiration,
                contract_type=asset.right.lower(),
                strike_price=asset.strike,
                expired=True,  # Needed so BackTest can look at old contracts to find the ticker we need
                limit=10,
            ))

            # If no contracts are found, break out of the loop
            if len(contracts) == 0:
                break

            symbol = contracts[0].ticker

            # poly_start = cur_start - timedelta(days=4)  # Subtract 4 days because options data can be very sparse
            # poly_end = end + timedelta(days=4)  # Add 4 days because options data can be very sparse

        else:
            raise ValueError(f"Unsupported asset type for polygon: {asset.asset_type}")

        try:
            result = polygon_client.get_aggs(
                ticker=symbol,
                from_=poly_start,  # polygon-api-client docs say 'from' but that is a reserved word in python
                to=poly_end,
                # In Polygon, multiplier is the number of "timespans" in each candle, so if you want 5min candles
                # returned you would set multiplier=5 and timespan="minute". This is very different from the
                # asset.multiplier setting for option contracts.
                multiplier=1,
                timespan=timespan,
            )
        except Exception as e:
            print(f"Error getting data from Polygon: {e}")
            return None

        df = pd.DataFrame(result)

        # Check if we got data from Polygon
        if df is not None and len(df) > 0:
            # Rename columns
            df = df.rename(
                columns={
                    "o": "open",
                    "h": "high",
                    "l": "low",
                    "c": "close",
                    "v": "volume",
                }
            )

            # Create a datetime column and set it as the index
            timestamp_col = "t" if "t" in df.columns else "timestamp"
            df = df.assign(datetime=pd.to_datetime(df[timestamp_col], unit="ms"))
            df = df.set_index("datetime")

            # Set the timezone to UTC
            df.index = df.index.tz_localize("UTC")

            if df_all is None:
                df_all = df
            else:
                df_all = pd.concat([df_all, df])

            # Sort the index
            df_all = df_all.sort_index()

        else:
            break

        first_iteration = False

    if df_all is None or len(df_all) == 0:
        return None

    # Remove any duplicate rows
    df_all = df_all[~df_all.index.duplicated(keep="first")]

    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)

    # Check if df_all is different from df_csv (if df_csv exists)
    if df_csv is not None and len(df_csv) > 0:
        # Check if the dataframes are the same
        if df_csv.equals(df_all):
            # They are the same, return df_csv
            return df_csv

    # Save the data to a csv file
    df_all.to_csv(cache_file)

    return df_all
