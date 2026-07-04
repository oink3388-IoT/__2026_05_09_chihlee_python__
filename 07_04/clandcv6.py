import dash
from dash import dcc, html, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import pandas as pd
import yfinance as yf
import twstock
import plotly.graph_objects as go
import numpy as np

# ==========================================
# 1. 初始化全台股票選單資料
# ==========================================
print("正在初始化全台股票資料...")
stock_options = []
stock_names = {} 

for code, info in twstock.codes.items():
    if info.type in ['股票', 'ETF']:
        label_text = f"{code} {info.name}"
        stock_options.append({"label": label_text, "value": code})
        stock_names[code] = info.name

stock_options = sorted(stock_options, key=lambda x: x['label'])

# ==========================================
# 2. 建立 Dash 應用程式
# ==========================================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "台股相關係數分析"

BG_COLOR = "#0D0E12"      
CARD_COLOR = "#14151A"    
TEXT_MUTED = "#A0A5B5"    
CHIP_COLOR = "#2A263F"    

app.layout = html.Div(
    style={"backgroundColor": BG_COLOR, "minHeight": "100vh", "padding": "30px", "fontFamily": "Microsoft JhengHei, sans-serif"},
    children=[
        dbc.Container([
            # 標題區塊
            html.Div([
                html.H2("📊 台股相關係數分析", style={"color": "white", "fontWeight": "bold", "margin": "0"}),
                html.P("搜尋股票 ➔ 點選「加入」 ➔ 選取 2~4 檔後自動 analysis", style={"color": TEXT_MUTED, "fontSize": "14px", "marginTop": "8px"})
            ], style={"marginBottom": "25px"}),
            
            # 搜尋輸入框
            html.Div([
                dcc.Dropdown(
                    id="stock-search-dropdown",
                    options=stock_options,
                    placeholder="🔍 輸入股票代碼或名稱...",
                    style={"backgroundColor": CARD_COLOR, "color": "white", "border": "1px solid #2A2B30", "borderRadius": "8px"},
                    clearable=True
                )
            ], style={"marginBottom": "20px"}, className="custom-dropdown"),
            
            # 已選取 Chips 標籤列
            html.Div([
                html.Span("📌 已選取", style={"color": TEXT_MUTED, "marginRight": "15px", "fontWeight": "bold", "fontSize": "15px"}),
                html.Div(id="chips-container", style={"display": "inline-flex", "flexWrap": "wrap", "gap": "10px"})
            ], style={"marginBottom": "15px", "display": "flex", "alignItems": "center"}),
            
            # 狀態提示文字
            html.Div(id="status-message", style={"color": TEXT_MUTED, "fontSize": "14px", "marginBottom": "25px"}),
            
            # 下方圖表區塊
            dbc.Row([
                # 左：相關係數表
                dbc.Col([
                    html.Div([
                        html.H5("📋 相關係數表", style={"color": "#FFCC66", "fontWeight": "bold", "marginBottom": "15px"}),
                        html.Div(id="table-output")
                    ], style={"backgroundColor": CARD_COLOR, "borderRadius": "12px", "padding": "20px", "height": "460px", "border": "1px solid #1E2026", "overflow": "auto"})
                ], md=6),
                
                # 右：熱力圖
                dbc.Col([
                    html.Div([
                        html.H5("🎨 熱力圖", style={"color": "#FFCC66", "fontWeight": "bold", "marginBottom": "15px"}),
                        dcc.Graph(id="heatmap-output", style={"height": "380px"}, config={"displayModeBar": False})
                    ], style={"backgroundColor": CARD_COLOR, "borderRadius": "12px", "padding": "20px", "height": "460px", "border": "1px solid #1E2026"})
                ], md=6)
            ])
            
        ], fluid=True, style={"maxWidth": "1200px"})
    ]
)

# 狀態儲存，預設加入 2330
app.layout.children.append(dcc.Store(id="selected-stocks-store", data=["2330"]))

# ==========================================
# 3. 互動邏輯控制 (Callbacks)
# ==========================================

@app.callback(
    Output("selected-stocks-store", "data"),
    Output("stock-search-dropdown", "value"),
    Input("stock-search-dropdown", "value"),
    Input({"type": "delete-btn", "index": dash.dependencies.ALL}, "n_clicks"),
    State("selected-stocks-store", "data")
)
def handle_stock_selection(selected_value, delete_clicks, current_stocks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_stocks, no_update
        
    triggered_id = ctx.triggered[0]["prop_id"]
    
    if "stock-search-dropdown" in triggered_id and selected_value:
        if selected_value not in current_stocks and len(current_stocks) < 4:
            current_stocks.append(selected_value)
        return current_stocks, "" 
        
    elif "delete-btn" in triggered_id:
        import json
        triggered_info = json.loads(triggered_id.split(".")[0])
        stock_to_remove = triggered_info["index"]
        if stock_to_remove in current_stocks:
            current_stocks.remove(stock_to_remove)
        return current_stocks, no_update
        
    return current_stocks, no_update


@app.callback(
    Output("chips-container", "children"),
    Output("status-message", "children"),
    Output("table-output", "children"),
    Output("heatmap-output", "figure"),
    Input("selected-stocks-store", "data")
)
def render_dashboard(current_stocks):
    # 1. 渲染 Chips
    chips = []
    for code in current_stocks:
        name = stock_names.get(code, "")
        chips.append(
            html.Div([
                html.Span(f"{code} {name}", style={"color": "white", "marginRight": "8px", "fontSize": "14px"}),
                html.Button(
                    "×", 
                    id={"type": "delete-btn", "index": code},
                    style={
                        "border": "none", "background": "transparent", "color": "#A0A5B5",
                        "fontSize": "16px", "cursor": "pointer", "padding": "0"
                    }
                )
            ], style={
                "backgroundColor": CHIP_COLOR, "padding": "6px 14px", 
                "borderRadius": "20px", "display": "flex", "alignItems": "center",
                "border": "1px solid #3A3554"
            })
        )
        
    # 2. 處理狀態提示文字
    count = len(current_stocks)
    if count < 2:
        status_text = f"🔍 已選取 {count} 檔 ，再選取 {2 - count} 檔即可自動分析"
    else:
        status_text = f"✅ 已選取 {count} 檔，圖表已自動即時更新"
        
    # 3. 如果不足 2 檔，顯示提示畫面
    if count < 2:
        empty_table = html.Div("請先選取足夠股票", style={"color": "#4A4C56", "fontSize": "16px", "textAlign": "center", "marginTop": "150px"})
        
        empty_heatmap = go.Figure()
        empty_heatmap.add_annotation(
            text="請選擇 2 ~ 4 檔股票",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=18, color="#4A4C56")
        )
        empty_heatmap.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        return chips, status_text, empty_table, empty_heatmap

    # 4. 超過 2 檔，安全連網抓取 yfinance 資料並分析
    yahoo_tickers = [f"{c}.TWO" if twstock.codes[c].market == '上櫃' else f"{c}.TW" for c in current_stocks]
    display_names = [stock_names[c] for c in current_stocks]
    
    data = yf.download(yahoo_tickers, period="1y", interval="1d", progress=False)
    if data.empty:
        return chips, status_text, html.Div("資料下載失敗", style={"color": "red"}), go.Figure()
        
    if isinstance(data.columns, pd.MultiIndex):
        close_data = data['Close']
    else:
        close_data = pd.DataFrame(data['Close'])
        close_data.columns = yahoo_tickers

    returns_df = close_data.pct_change().dropna()
    
    # 對照回中文名稱
    ticker_to_name = {t: stock_names[t.split('.')[0]] for t in yahoo_tickers}
    returns_df = returns_df.rename(columns=ticker_to_name)
    
    available_names = [name for name in display_names if name in returns_df.columns]
    if len(available_names) < 2:
        return chips, status_text, html.Div("有效交易資料不足", style={"color": "orange"}), go.Figure()
        
    returns_df = returns_df[available_names]
    corr_matrix = returns_df.corr().round(4)
    
    # 5. 建立美化 HTML 表格
    table_header = [html.Thead(html.Tr([html.Th("")] + [html.Th(name, style={"color": TEXT_MUTED, "textAlign": "center"}) for name in available_names]))]
    table_rows = []
    for idx, name_row in enumerate(available_names):
        row_cells = [html.Td(name_row, style={"fontWeight": "bold", "color": TEXT_MUTED})]
        for jdx, name_col in enumerate(available_names):
            val = corr_matrix.loc[name_row, name_col]
            is_diagonal = (idx == jdx)
            cell_style = {
                "color": "white" if is_diagonal else "#CCCCCC",
                "fontWeight": "bold" if is_diagonal else "normal",
                "backgroundColor": "#252730" if is_diagonal else "transparent",
                "textAlign": "center",
                "padding": "12px"
            }
            row_cells.append(html.Td(f"{val:.4f}", style=cell_style))
        table_rows.append(html.Tr(row_cells))
        
    html_table = dbc.Table(
        table_header + [html.Tbody(table_rows)],
        bordered=True, hover=False, responsive=True,
        style={"borderColor": "#2A2B30", "backgroundColor": "#141519", "width": "100%", "marginTop": "20px"}
    )
    
    # 6. 建立 Plotly Heatmap 熱力圖 (自訂客製化色彩對照，防止名稱不對而噴錯)
    custom_colorscale = [
        [0.0, "#3B4CC0"],  # 強負相關 (深藍)
        [0.5, "#FFFFFF"],  # 無相關 (純白)
        [1.0, "#B40426"]   # 強正相關 (深紅)
    ]
    
    heatmap_fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=available_names,
        y=available_names,
        colorscale=custom_colorscale,
        zmin=-1, zmax=1,
        text=corr_matrix.values,
        texttemplate="%{text:.3f}",
        textfont={"size": 12, "fontfamily": "Microsoft JhengHei", "color": "black"},
        showscale=True,
        colorbar=dict(thickness=15, len=0.9)
    ))
    
    heatmap_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=10, b=40),
        xaxis=dict(tickfont=dict(color="white", size=12), side="bottom", gridcolor="#2A2B30"),
        yaxis=dict(tickfont=dict(color="white", size=12), gridcolor="#2A2B30", autorange="reverse")
    )
    
    return chips, status_text, html_table, heatmap_fig

# ==========================================
# 4. 啟動伺服器
# ==========================================
if __name__ == "__main__":
    app.index_string = '''
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
            <style>
                .custom-dropdown .Select-control { background-color: #14151A !important; border-color: #2A2B30 !important; height: 45px !important; }
                .custom-dropdown .Select-value-label { color: white !important; line-height: 43px !important; }
                .custom-dropdown .Select-placeholder { line-height: 43px !important; color: #666A78 !important; }
                .custom-dropdown .Select-menu-outer { background-color: #14151A !important; border-color: #2A2B30 !important; }
                .custom-dropdown .VirtualizedSelectOption { background-color: #14151A !important; color: white !important; }
                .custom-dropdown .VirtualizedSelectFocusedOption { background-color: #2A263F !important; color: white !important; }
                .Select-input input { color: white !important; }
            </style>
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
    '''
    app.run(debug=True, port=8050)