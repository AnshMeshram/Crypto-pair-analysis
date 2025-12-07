import os
import time
from datetime import datetime, timedelta, timezone

import pandas as pd
import plotly.graph_objs as go
import streamlit as st

from analytics import (compute_ols_hedge, df_to_csv_bytes, rolling_zscore,
                       resample_ohlc, run_adf, ticks_to_df)
from backend import BinanceIngest
from data_store import get_datastore


st.set_page_config(layout="wide", page_title="Real-time Pair Analytics")

DB_PATH = os.path.join(os.path.dirname(__file__), "ticks.db")


@st.cache_resource
def get_ingest_instance(default_symbols):
    # returns a BinanceIngest instance without starting it
    bi = BinanceIngest(default_symbols, db_path=DB_PATH)
    return bi


@st.cache_data(ttl=1)
def load_ticks(symbols, minutes=60):
    ds = get_datastore(DB_PATH)
    end_ts = int(time.time() * 1000)
    start_ts = int((datetime.now(timezone.utc) - timedelta(minutes=minutes)).timestamp() * 1000)
    rows = ds.get_ticks(symbols, start_ts=start_ts, end_ts=end_ts)
    # rows returned as (ts, symbol, price, qty)
    return ticks_to_df(rows)


def main():
    st.title("Real-time Pair Analytics Prototype")
    col1, col2 = st.columns([1, 3])

    with col1:
        st.header("Controls")
        default_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
        ingest = get_ingest_instance(default_symbols)
        # Start/Stop ingest controls
        ingest_col1, ingest_col2 = st.columns([1, 1])
        with ingest_col1:
            if st.button("Start Ingest"):
                ingest.start()
                st.success("Ingest started")
        with ingest_col2:
            if st.button("Stop Ingest"):
                ingest.stop()
                st.info("Ingest stopped")

        all_symbols = st.multiselect("Symbols (pairs) to view", default_symbols, default=default_symbols)
        timeframe = st.selectbox("Resample timeframe", ["1s", "1min", "5min"], index=0)
        lookback_mins = st.number_input("Load lookback (minutes)", min_value=1, max_value=60*24, value=30)
        rolling_window = st.number_input("Rolling window (bars)", min_value=2, max_value=1000, value=20)
        pair = st.multiselect("Select two symbols for pair analytics (Y, X)", all_symbols, default=all_symbols[:2])
        reg_type = st.selectbox("Regression type", ["OLS"], index=0)
        run_adf_btn = st.button("Run ADF on spread")
        alert_z = st.number_input("Alert z-score threshold", value=2.0, step=0.5)
        export_csv = st.button("Export current resampled CSV")

    with col2:
        st.header("Charts & Stats")
        # If user uploads OHLC CSV, use that for analytics instead of DB resampled ticks
        uploaded = st.file_uploader("Upload OHLC CSV (optional)", type=["csv"])
        if uploaded is not None:
            try:
                uploaded_df = pd.read_csv(uploaded, parse_dates=[0], index_col=0)
                # Expecting columns: open, high, low, close, volume or at least close
                st.success("Uploaded CSV loaded — using it for analytics")
                # create a fake ticks_df from uploaded OHLC by taking the close values and expanding
                if 'close' in uploaded_df.columns:
                    ticks_df = pd.DataFrame({
                        'ts': (uploaded_df.index.astype('int64') // 10**6),
                        'symbol': [all_symbols[0] if all_symbols else 'UPLOADED'] * len(uploaded_df),
                        'price': uploaded_df['close'].values,
                        'qty': [0.0] * len(uploaded_df)
                    })
                else:
                    st.warning('Uploaded CSV missing `close` column; upload a standard OHLC file')
                    ticks_df = load_ticks(all_symbols, minutes=lookback_mins)
            except Exception as e:
                st.error(f"Failed to read uploaded CSV: {e}")
                ticks_df = load_ticks(all_symbols, minutes=lookback_mins)
        else:
            ticks_df = load_ticks(all_symbols, minutes=lookback_mins)
        if ticks_df.empty:
            st.info("No tick data yet — give the ingest a few seconds and ensure symbols are traded on Binance.")
            return

        # Price chart for selected symbols
        price_fig = go.Figure()
        for s in all_symbols:
            try:
                ohlc = resample_ohlc(ticks_df, s, rule=timeframe)
            except Exception:
                ohlc = None
            if ohlc is not None and not ohlc.empty:
                price_fig.add_trace(go.Candlestick(
                    x=ohlc.index, open=ohlc['open'], high=ohlc['high'], low=ohlc['low'], close=ohlc['close'], name=s
                ))
        price_fig.update_layout(height=400, xaxis_rangeslider_visible=False)
        st.plotly_chart(price_fig, width='stretch')

        # Pair analytics
        if len(pair) == 2:
            y_symbol, x_symbol = pair[0], pair[1]
            y_ohlc = resample_ohlc(ticks_df, y_symbol, rule=timeframe)
            x_ohlc = resample_ohlc(ticks_df, x_symbol, rule=timeframe)
            # align close series
            s_y = y_ohlc['close']
            s_x = x_ohlc['close']
            ols = compute_ols_hedge(s_y, s_x)
            if ols is None:
                st.warning("Not enough overlapping data to compute hedge")
            else:
                spread = ols['spread_series']
                z = rolling_zscore(spread, window=rolling_window)
                zname = f"Z({y_symbol}-{ols['beta']:.3f}*{x_symbol})"
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(x=spread.index, y=spread.values, name='spread'))
                fig2.add_trace(go.Scatter(x=z.index, y=z.values, name=zname, yaxis='y2'))
                fig2.update_layout(
                    yaxis=dict(title='Spread'),
                    yaxis2=dict(title='Z-score', overlaying='y', side='right'),
                    height=350
                )
                st.plotly_chart(fig2, width='stretch')

                # stats and ADF
                colA, colB = st.columns(2)
                with colA:
                    st.metric("Hedge beta", f"{ols['beta']:.6f}")
                    st.metric("Intercept", f"{ols['intercept']:.6f}")
                    st.metric("Latest spread", f"{spread.dropna().iloc[-1]:.6f}")
                with colB:
                    st.metric("Z-score (latest)", f"{z.dropna().iloc[-1]:.3f}" if not z.dropna().empty else "n/a")
                    if run_adf_btn:
                        adf_res = run_adf(spread)
                        if adf_res:
                            st.write("ADF p-value:", adf_res['pvalue'])
                        else:
                            st.write("ADF: insufficient data")

                # Alerts
                if not z.dropna().empty:
                    latest_z = float(z.dropna().iloc[-1])
                    if abs(latest_z) >= alert_z:
                        st.error(f"Alert: |z| >= {alert_z} (z={latest_z:.2f})")

                # CSV export
                if export_csv:
                    # join OHLCs
                    joined = pd.concat([s_y.rename(f"close_{y_symbol}"), s_x.rename(f"close_{x_symbol}"), spread.rename('spread'), z.rename('zscore')], axis=1)
                    csv_bytes = df_to_csv_bytes(joined)
                    st.download_button("Download CSV", data=csv_bytes, file_name=f"pair_{y_symbol}_{x_symbol}.csv")

        else:
            st.info("Select exactly two symbols for pair analytics")

        # show recent ticks table
        st.subheader("Recent ticks (sample)")
        # If ticks_df was constructed from uploaded OHLC, show a small resampled table
        if not ticks_df.empty:
            try:
                # If ts is datetime-like, convert for display
                if pd.api.types.is_datetime64_any_dtype(ticks_df['ts']):
                    display_df = ticks_df.copy()
                else:
                    display_df = ticks_df.copy()
                    display_df['ts'] = pd.to_datetime(display_df['ts'], unit='ms')
                st.dataframe(display_df.sort_values('ts', ascending=False).head(200))
            except Exception:
                st.dataframe(ticks_df.head(200))
        else:
            st.write('No ticks to display yet.')


if __name__ == "__main__":
    main()
