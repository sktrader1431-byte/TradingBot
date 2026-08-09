from datetime import datetime
from dhanhq import DhanContext, dhanhq
import pandas as pd
import time

client_id = '1100477972'
access_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzg2Mjk0MzM4LCJpYXQiOjE3ODYyMDc5MzgsInRva2VuQ29uc3VtZXJUeXBlIjoiU0VMRiIsIndlYmhvb2tVcmwiOiIiLCJkaGFuQ2xpZW50SWQiOiIxMTAwNDc3OTcyIn0.MtXvWja1_6VvllpadxA5GZjmQZfJ4v-nLmoVp3WKtrzy9xKllBRmatQn5Tm39DfyGrt8RALjRJuYLkoK20skKw'

dhan_context = DhanContext(client_id, access_token)
dhan = dhanhq(dhan_context)

print('🚀 Ultimate All-in-One Live Trading Bot Suru Jhala Ahe...')

while True:
  try:
    today_date = datetime.now().strftime('%Y-%m-%d')

    response = dhan.intraday_minute_data(
        security_id='13',
        exchange_segment='IDX_I',
        instrument_type='INDEX',
        from_date=today_date,
        to_date=today_date,
    )

    # डेटा रिकामा आहे का किंवा मार्केट बंद आहे का हे तपासणे
    if (
        'data' not in response
        or not response['data']
        or not response['data'].get('close')
    ):
      print(
          f'[{datetime.now().strftime("%H:%M:%S")}] ⚠️ Market Band ahe kinva'
          ' aaj data uplabdh nahi (Weekend / Holiday).'
      )
      time.sleep(60)
      continue

    res_data = response['data']
    df = pd.DataFrame({
        'open': res_data['open'],
        'high': res_data['high'],
        'low': res_data['low'],
        'close': res_data['close'],
        'volume': res_data['volume'],
    })

    def calculate_rsi(data, window=14):
      delta = data['close'].diff()
      gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
      loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
      return 100 - (100 / (1 + (gain / loss)))


    df['RSI'] = calculate_rsi(df)
    df['EMA_20'] = df['close'].ewm(span=20, adjust=False).mean()

    current_price = df['close'].iloc[-1]
    latest_rsi = df['RSI'].iloc[-1]
    latest_ema = df['EMA_20'].iloc[-1]

    dynamic_resistance = df['high'].iloc[-15:].max()
    dynamic_support = df['low'].iloc[-15:].min()

    put_writer_support = dynamic_support
    call_writer_resistance = dynamic_resistance

    price_range = call_writer_resistance - put_writer_support
    middle_zone = put_writer_support + (price_range / 2)
    is_sideways = (45 <= latest_rsi <= 55) and (
        abs(current_price - middle_zone) < (price_range * 0.3)
    )

    final_signal = 'HOLD (थांबा, योग्य मोमेंटमची वाट बघा)'

    if is_sideways:
      final_signal = 'NO TRADE 🛑 (Market Side-ways ahe)'
    elif current_price <= (put_writer_support * 1.003) and latest_rsi < 42:
      final_signal = 'STRONG BUY 🟢 (Support Javal + Oversold)'
    elif current_price >= (call_writer_resistance * 0.997) and latest_rsi > 58:
      final_signal = 'STRONG SELL 🔴 (Resistance Javal + Overbought)'
    elif latest_rsi < 30:
      final_signal = 'BUY 🟢 (RSI Oversold)'
    elif latest_rsi > 70:
      final_signal = 'SELL 🔴 (RSI Overbought)'

    current_time = datetime.now().strftime('%H:%M:%S')
    print('==================================================')
    print(f'Time                     : {current_time}')
    print(f'Current Market Price     : {current_price}')
    print(f'Put Writers Support      : {put_writer_support}')
    print(f'Call Writers Resistance  : {call_writer_resistance}')
    print(f'RSI Momentum Value       : {latest_rsi:.2f}')
    print('--------------------------------------------------')
    print(f'ULTIMATE LIVE SIGNAL     :\n{final_signal}')
    print('==================================================')

    time.sleep(60)

  except Exception as e:
    print('Error ala ahe:', e)
    time.sleep(30)