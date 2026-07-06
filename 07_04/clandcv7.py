import random

import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import twstock
import yfinance as yf
from dash import ALL, Input, Output, State, dcc, html, no_update


MAX_SELECTED = 4
PERIOD = "1y"

BG_COLOR = "#0D0E12"
CARD_COLOR = "#15171D"
TEXT_MUTED = "#A0A5B5"
ACCENT = "#FFCC66"
GOOD = "#47D18C"
BAD = "#FF6B6B"


# ==========================================
# 1. 股票清單與基本工具
# ==========================================

def build_stock_universe():
    stocks = {}

    for code, info in twstock.codes.items():
        if info.type in ("股票", "ETF") and info.market in ("上市", "上櫃"):
            suffix = "TWO" if info.market == "上櫃" else "TW"
            stocks[code] = {
                "name": info.name,
                "market": info.market,
                "symbol": f"{code}.{suffix}",
                "label": f"{code} {info.name}",
            }

    return dict(sorted(stocks.items()))


STOCKS = build_stock_universe()
STOCK_OPTIONS = [
    {"label": item["label"], "value": code}
    for code, item in STOCKS.items()
]


def random_codes():
    pool = list(STOCKS.keys())
    return random.sample(pool, k=min(MAX_SELECTED, len(pool)))


def empty_figure(message):
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=18, color="#555A68"),
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=10, r=10, t=10, b=10),
    )
    return fig


# ==========================================
# 2. 資料下載與分析
# ==========================================

def extract_close_data(raw, symbols):
    if raw is None or raw.empty:
        return pd.DataFrame(), "Yahoo Finance 沒有回傳資料。"

    if isinstance(raw.columns, pd.MultiIndex):
        level0 = list(raw.columns.get_level_values(0))
        level1 = list(raw.columns.get_level_values(1))

        if "Close" in level0:
            close = raw["Close"].copy()
        elif "Close" in level1:
            close = raw.xs("Close", axis=1, level=1).copy()
        else:
            return pd.DataFrame(), "下載資料缺少 Close 收盤價欄位。"
    else:
        if "Close" not in raw.columns:
            return pd.DataFrame(), "下載資料缺少 Close 收盤價欄位。"
        close = pd.DataFrame(raw["Close"])
        close.columns = symbols[:1]

    return close, None


def download_close_prices(codes):
    valid_codes = [code for code in codes if code in STOCKS]
    symbols = [STOCKS[code]["symbol"] for code in valid_codes]
    symbol_to_label = {
        STOCKS[code]["symbol"]: STOCKS[code]["label"]
        for code in valid_codes
    }

    if len(symbols) < 2:
        return pd.DataFrame(), "至少需要 2 檔股票才能比較。"

    try:
        raw = yf.download(
            symbols,
            period=PERIOD,
            interval="1d",
            auto_adjust=False,
            progress=False,
            group_by="column",
            threads=True,
        )
    except Exception as exc:
        return pd.DataFrame(), f"資料下載失敗：{type(exc).__name__}: {exc}"

    close, error = extract_close_data(raw, symbols)
    if error:
        return pd.DataFrame(), error

    close = close.rename(columns=symbol_to_label)
    close = close.apply(pd.to_numeric, errors="coerce")
    close = close.dropna(axis=1, how="all").ffill()

    usable_columns = [
        col
        for col in close.columns
        if close[col].notna().sum() >= 30
    ]
    close = close[usable_columns].dropna(how="all")

    if close.shape[1] < 2:
        return pd.DataFrame(), "有效交易資料少於 2 檔，請重新隨機抽樣。"

    close = close.dropna()
    if close.empty or len(close) < 30:
        return pd.DataFrame(), "共同交易資料不足，請重新隨機抽樣。"

    return close, None


def calculate_metrics(close):
    returns = close.pct_change().dropna()
    if returns.empty:
        return returns, pd.DataFrame()

    cumulative = (1 + returns).cumprod()
    drawdown = cumulative / cumulative.cummax() - 1
    days = max(len(returns), 1)

    total_return = close.iloc[-1] / close.iloc[0] - 1
    annual_return = (1 + total_return) ** (252 / days) - 1
    annual_volatility = returns.std() * np.sqrt(252)
    risk_return_ratio = annual_return / annual_volatility.replace(0, np.nan)
    max_drawdown = drawdown.min()

    metrics = pd.DataFrame(
        {
            "總報酬": total_return,
            "年化報酬": annual_return,
            "年化波動": annual_volatility,
            "風險報酬比": risk_return_ratio,
            "最大回撤": max_drawdown,
        }
    ).replace([np.inf, -np.inf], np.nan)

    return returns, metrics


# ==========================================
# 3. 畫面元件
# ==========================================

def pct_text(value):
    return "-" if pd.isna(value) else f"{value:.2%}"


def number_text(value):
    return "-" if pd.isna(value) else f"{value:.2f}"


def metric_table(metrics):
    rows = []
    metrics = metrics.sort_values(
        "風險報酬比",
        ascending=False,
        na_position="last",
    )

    for name, row in metrics.iterrows():
        return_color = GOOD if row["總報酬"] >= 0 else BAD
        dd_color = BAD if row["最大回撤"] <= -0.2 else TEXT_MUTED

        rows.append(
            html.Tr(
                [
                    html.Td(name, style={"fontWeight": "700", "color": "white"}),
                    html.Td(pct_text(row["總報酬"]), style={"color": return_color}),
                    html.Td(pct_text(row["年化報酬"]), style={"color": return_color}),
                    html.Td(pct_text(row["年化波動"]), style={"color": TEXT_MUTED}),
                    html.Td(number_text(row["風險報酬比"]), style={"color": ACCENT}),
                    html.Td(pct_text(row["最大回撤"]), style={"color": dd_color}),
                ]
            )
        )

    return dbc.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("股票"),
                        html.Th("總報酬"),
                        html.Th("年化報酬"),
                        html.Th("年化波動"),
                        html.Th("風險報酬比"),
                        html.Th("最大回撤"),
                    ]
                )
            ),
            html.Tbody(rows),
        ],
        bordered=False,
        hover=True,
        responsive=True,
        style={"color": TEXT_MUTED, "fontSize": "14px", "margin": "0"},
    )


def performance_figure(close):
    normalized = close / close.iloc[0] * 100
    fig = go.Figure()
    palette = ["#FFCC66", "#47D18C", "#5AA9FF", "#FF6B6B"]

    for idx, col in enumerate(normalized.columns):
        fig.add_trace(
            go.Scatter(
                x=normalized.index,
                y=normalized[col],
                mode="lines",
                name=col,
                line=dict(width=2.8, color=palette[idx % len(palette)]),
                hovertemplate=(
                    "%{x|%Y-%m-%d}<br>"
                    "%{y:.2f}<extra>%{fullData.name}</extra>"
                ),
            )
        )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=30, r=20, t=20, b=35),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(color="white"),
        ),
        xaxis=dict(gridcolor="#2A2D36", tickfont=dict(color=TEXT_MUTED)),
        yaxis=dict(
            title=dict(text="起始日 = 100", font=dict(color=TEXT_MUTED)),
            gridcolor="#2A2D36",
            tickfont=dict(color=TEXT_MUTED),
        ),
        hovermode="x unified",
    )
    return fig


def heatmap_figure(returns):
    corr = returns.corr().round(3)
    fig = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=list(corr.columns),
            y=list(corr.index),
            colorscale=[
                [0, "#4267B2"],
                [0.5, "#F5F7FA"],
                [1, "#B72A3A"],
            ],
            zmin=-1,
            zmax=1,
            hovertemplate=(
                "%{y}<br>%{x}<br>"
                "相關係數：%{z:.3f}<extra></extra>"
            ),
            colorbar=dict(
                thickness=14,
                len=0.86,
                tickfont=dict(color=TEXT_MUTED),
            ),
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=70, r=20, t=15, b=65),
        xaxis=dict(tickfont=dict(color="white", size=11), side="bottom"),
        yaxis=dict(tickfont=dict(color="white", size=11), autorange="reversed"),
    )
    return fig


def chip(code):
    label = STOCKS.get(code, {}).get("label", code)

    return html.Div(
        [
            html.Span(label, style={"color": "white", "fontSize": "14px"}),
            html.Button(
                "x",
                id={"type": "delete-btn", "index": code},
                n_clicks=0,
                title="移除",
                style={
                    "border": "0",
                    "background": "transparent",
                    "color": TEXT_MUTED,
                    "fontSize": "16px",
                    "lineHeight": "16px",
                    "cursor": "pointer",
                },
            ),
        ],
        style={
            "display": "inline-flex",
            "alignItems": "center",
            "gap": "8px",
            "backgroundColor": "#272331",
            "border": "1px solid #3B344A",
            "borderRadius": "8px",
            "padding": "7px 10px",
        },
    )


# ==========================================
# 4. Dash App Layout
# ==========================================

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True,
)
app.title = "台股四檔隨機比較"

app.layout = html.Div(
    [
        dcc.Store(id="selected-stocks-store", data=random_codes()),
        dbc.Container(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.H2(
                                    "台股四檔隨機比較",
                                    style={
                                        "color": "white",
                                        "fontWeight": "800",
                                        "margin": 0,
                                    },
                                ),
                                html.P(
                                    "隨機抽樣比較近一年績效、風險、最大回撤與相關係數。",
                                    style={
                                        "color": TEXT_MUTED,
                                        "margin": "8px 0 0",
                                        "fontSize": "14px",
                                    },
                                ),
                            ]
                        ),
                        dbc.Button(
                            "重新隨機抽 4 檔",
                            id="random-btn",
                            n_clicks=0,
                            color="warning",
                            style={"fontWeight": "700"},
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justifyContent": "space-between",
                        "alignItems": "center",
                        "gap": "18px",
                        "marginBottom": "22px",
                    },
                ),
                html.Div(
                    [
                        dcc.Dropdown(
                            id="stock-search-dropdown",
                            options=STOCK_OPTIONS,
                            placeholder="搜尋代碼或名稱，加入比較清單",
                            clearable=True,
                            style={"color": "#111"},
                        ),
                        html.Div(
                            id="status-message",
                            style={
                                "color": TEXT_MUTED,
                                "fontSize": "14px",
                                "marginTop": "10px",
                            },
                        ),
                    ],
                    style={
                        "backgroundColor": CARD_COLOR,
                        "border": "1px solid #252833",
                        "borderRadius": "8px",
                        "padding": "16px",
                        "marginBottom": "16px",
                    },
                ),
                html.Div(
                    id="chips-container",
                    style={
                        "display": "flex",
                        "flexWrap": "wrap",
                        "gap": "10px",
                        "marginBottom": "18px",
                    },
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    html.H5(
                                        "績效走勢",
                                        style={
                                            "color": ACCENT,
                                            "fontWeight": "800",
                                            "marginBottom": "10px",
                                        },
                                    ),
                                    dcc.Loading(
                                        dcc.Graph(
                                            id="performance-output",
                                            style={"height": "390px"},
                                            config={"displayModeBar": False},
                                        )
                                    ),
                                ],
                                style={
                                    "backgroundColor": CARD_COLOR,
                                    "border": "1px solid #252833",
                                    "borderRadius": "8px",
                                    "padding": "16px",
                                },
                            ),
                            lg=7,
                        ),
                        dbc.Col(
                            html.Div(
                                [
                                    html.H5(
                                        "核心指標",
                                        style={
                                            "color": ACCENT,
                                            "fontWeight": "800",
                                            "marginBottom": "10px",
                                        },
                                    ),
                                    dcc.Loading(html.Div(id="table-output")),
                                ],
                                style={
                                    "backgroundColor": CARD_COLOR,
                                    "border": "1px solid #252833",
                                    "borderRadius": "8px",
                                    "padding": "16px",
                                    "minHeight": "430px",
                                },
                            ),
                            lg=5,
                        ),
                    ],
                    className="g-3",
                ),
                html.Div(
                    [
                        html.H5(
                            "相關係數熱力圖",
                            style={
                                "color": ACCENT,
                                "fontWeight": "800",
                                "marginBottom": "10px",
                            },
                        ),
                        dcc.Loading(
                            dcc.Graph(
                                id="heatmap-output",
                                style={"height": "420px"},
                                config={"displayModeBar": False},
                            )
                        ),
                    ],
                    style={
                        "backgroundColor": CARD_COLOR,
                        "border": "1px solid #252833",
                        "borderRadius": "8px",
                        "padding": "16px",
                        "marginTop": "16px",
                    },
                ),
                html.P(
                    "資料來源：Yahoo Finance。此工具用於量化觀察，不構成投資建議。",
                    style={
                        "color": "#6F7482",
                        "fontSize": "12px",
                        "marginTop": "16px",
                    },
                ),
            ],
            fluid=True,
            style={"maxWidth": "1220px"},
        ),
    ],
    style={
        "backgroundColor": BG_COLOR,
        "minHeight": "100vh",
        "padding": "28px",
        "fontFamily": "Microsoft JhengHei, Arial, sans-serif",
    },
)


# ==========================================
# 5. Callbacks
# ==========================================

@app.callback(
    Output("selected-stocks-store", "data"),
    Output("stock-search-dropdown", "value"),
    Input("random-btn", "n_clicks"),
    Input("stock-search-dropdown", "value"),
    Input({"type": "delete-btn", "index": ALL}, "n_clicks"),
    State("selected-stocks-store", "data"),
    prevent_initial_call=True,
)
def update_selection(random_clicks, selected_value, delete_clicks, current_codes):
    ctx = dash.callback_context
    current_codes = list(current_codes or [])

    if not ctx.triggered:
        return current_codes, no_update

    trigger = ctx.triggered[0]["prop_id"]

    if trigger.startswith("random-btn"):
        return random_codes(), None

    if trigger.startswith("stock-search-dropdown") and selected_value:
        if selected_value not in current_codes:
            current_codes = (current_codes + [selected_value])[-MAX_SELECTED:]
        return current_codes, None

    if "delete-btn" in trigger:
        import json

        code = json.loads(trigger.split(".")[0])["index"]
        current_codes = [item for item in current_codes if item != code]
        return current_codes, no_update

    return current_codes, no_update


@app.callback(
    Output("chips-container", "children"),
    Output("status-message", "children"),
    Output("table-output", "children"),
    Output("performance-output", "figure"),
    Output("heatmap-output", "figure"),
    Input("selected-stocks-store", "data"),
)
def render_dashboard(current_codes):
    try:
        current_codes = [
            code
            for code in (current_codes or [])
            if code in STOCKS
        ]
        chips = [chip(code) for code in current_codes]

        if len(current_codes) < 2:
            message = f"目前 {len(current_codes)} 檔。至少需要 2 檔，最多保留 4 檔。"
            empty_table = html.Div(
                "請加入更多股票。",
                style={
                    "color": TEXT_MUTED,
                    "textAlign": "center",
                    "padding": "120px 0",
                },
            )
            return (
                chips,
                message,
                empty_table,
                empty_figure("請至少選擇 2 檔"),
                empty_figure("請至少選擇 2 檔"),
            )

        close, error = download_close_prices(current_codes)
        if error:
            error_box = html.Div(
                error,
                style={
                    "color": BAD,
                    "padding": "80px 0",
                    "textAlign": "center",
                },
            )
            return (
                chips,
                f"已選取 {len(current_codes)} 檔。",
                error_box,
                empty_figure(error),
                empty_figure(error),
            )

        returns, metrics = calculate_metrics(close)
        if returns.empty or metrics.empty:
            message = "可計算的報酬資料不足，請重新隨機抽樣。"
            error_box = html.Div(
                message,
                style={
                    "color": BAD,
                    "padding": "80px 0",
                    "textAlign": "center",
                },
            )
            return (
                chips,
                message,
                error_box,
                empty_figure(message),
                empty_figure(message),
            )

        best_name = metrics["風險報酬比"].idxmax()
        worst_dd = metrics["最大回撤"].idxmin()
        status = (
            f"已完成近一年比較。"
            f"風險報酬比最佳：{best_name}；"
            f"最大回撤最深：{worst_dd}。"
        )

        return (
            chips,
            status,
            metric_table(metrics),
            performance_figure(close),
            heatmap_figure(returns),
        )

    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        message = f"程式已攔截例外，請重新隨機抽樣。錯誤摘要：{error}"
        error_box = html.Div(
            message,
            style={
                "color": BAD,
                "padding": "80px 0",
                "textAlign": "center",
            },
        )
        return (
            [],
            message,
            error_box,
            empty_figure("資料處理發生錯誤"),
            empty_figure("資料處理發生錯誤"),
        )


if __name__ == "__main__":
    app.run(debug=True, port=8050)
