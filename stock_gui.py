# -*- coding: utf-8 -*-
"""
Stock Quantitative Analysis GUI v3.0 - BaoStock Real Data
Features: K-line chart, MA/RSI/MACD/KDJ indicators, Buy/Sell signals, Backtest
         Crosshair sync across all subplots, Signal notifications
"""

import tkinter as tk
from tkinter import ttk, messagebox
import baostock as bs
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import FancyBboxPatch
import datetime
import threading

# ========== Stock name mapping ==========
STOCK_NAMES = {
    "002285": "\u4e16\u8054\u884c", "000001": "\u5e73\u5b89\u94f6\u884c", "000002": "\u4e07\u79d1A",
    "000063": "\u4e2d\u5174\u901a\u8baf", "000100": "TCL\u79d1\u6280", "000333": "\u7f8e\u7684\u96c6\u56e2",
    "000338": "\u6f4d\u67f4\u52a8\u529b", "000425": "\u5f90\u5de5\u673a\u68b0", "000538": "\u4e91\u5357\u767d\u836f",
    "000568": "\u6cf8\u5dde\u8001\u7a96", "000596": "\u53e4\u4e95\u8d21\u9152", "000625": "\u957f\u5b89\u6c7d\u8f66",
    "000651": "\u683c\u529b\u7535\u5668", "000661": "\u957f\u6625\u9ad8\u65b0", "000725": "\u4eac\u4e1c\u65b9A",
    "000768": "\u4e2d\u822a\u897f\u98de", "000776": "\u5e7f\u53d1\u8bc1\u5238", "000783": "\u957f\u6c5f\u8bc1\u5238",
    "000786": "\u5317\u65b0\u5efa\u6750", "000800": "\u4e00\u6c7d\u89e3\u653e", "000858": "\u4e94\u7cae\u6db2",
    "000876": "\u65b0\u5e0c\u671b", "000895": "\u53cc\u6c47\u53d1\u5c55", "000898": "\u97a6\u94a2\u80a1\u4efd",
    "000938": "\u7d2b\u5149\u80a1\u4efd", "000963": "\u534e\u4e1c\u533b\u836f", "000977": "\u6d6a\u6f6e\u4fe1\u606f",
    "001289": "\u534e\u5f3a\u5317\u65b9", "002007": "\u534e\u5170\u753b", "002024": "\u82cf\u5b81\u6613\u8d2d",
    "002049": "\u7d2b\u5149\u56fd\u5fae", "002120": "\u97e6\u5c14\u80a1\u4efd", "002142": "\u5b81\u6ce2\u94f6\u884c",
    "002179": "\u4e2d\u822a\u5149\u7535", "002230": "\u79d1\u5927\u8baf\u98de", "002236": "\u5927\u534e\u80a1\u4efd",
    "002241": "\u6b4c\u5c14\u80a1\u4efd", "002271": "\u4e1c\u65b9\u96e8\u8679", "002304": "\u6d0b\u6cb3\u80a1\u4efd",
    "002352": "\u987a\u4e30\u63a7\u80a1", "002415": "\u6d77\u5eb7\u5a01\u89c6", "002460": "\u8d63\u950b\u9502\u4e1a",
    "002475": "\u7acb\u8baf\u7cbe\u5bc6", "002493": "\u8363\u76db\u77f3\u6cb9", "002555": "\u4e09\u4e03\u4e92\u5a31",
    "002594": "\u6bd4\u4e9a\u8fea", "002601": "\u9f99\u864e\u80a1\u4efd", "002607": "\u4e2d\u516c\u6559\u80b2",
    "002709": "\u5929\u8d50\u6750\u6599", "002714": "\u7267\u539f\u80a1\u4efd", "002736": "\u56fd\u4fe1\u8bc1\u5238",
    "002812": "\u6069\u6377\u80a1\u4efd", "002841": "\u89c6\u6e90\u80a1\u4efd", "003816": "\u4e2d\u56fd\u5e7f\u6838",
    "300003": "\u4e50\u666e\u533b\u7597", "300014": "\u4f0d\u80e1\u836f", "300015": "\u7231\u5c14\u773c\u79d1",
    "300033": "\u540c\u82b1\u987a", "300059": "\u4e1c\u65b9\u8d22\u5bcc", "300124": "\u6c47\u5ddd\u6280\u672f",
    "300274": "\u9633\u5149\u7535\u6e90", "300308": "\u4e2d\u96c6\u7535\u5b50", "300315": "\u5146\u76ca\u521b\u65b0",
    "300347": "\u6cf0\u683c\u5fae", "300394": "\u5929\u8d50\u6750\u6599", "300408": "\u4e09\u73af\u96c6\u56e2",
    "300413": "\u8292\u679c\u8d85\u5a92", "300433": "\u84dd\u601d\u667a\u8054", "300454": "\u6df1\u4fe1\u670d",
    "300496": "\u4e2d\u79d1\u521b\u8fbe", "300498": "\u6e29\u6c0f\u80a1\u4efd", "300502": "\u65b0\u6613\u76db",
    "300750": "\u5b81\u5fb7\u65f6\u4ee3", "300760": "\u8fc8\u745e\u533b\u7597", "300782": "\u5353\u80dc\u5fae",
    "600000": "\u6d66\u53d1\u94f6\u884c", "600009": "\u4e0a\u6d77\u673a\u573a", "600010": "\u5305\u94a2\u80a1\u4efd",
    "600011": "\u534e\u80fd\u56fd\u9645", "600016": "\u6c11\u751f\u94f6\u884c", "600018": "\u4e0a\u6d77\u96c6\u88c5",
    "600019": "\u5b9d\u94a2\u80a1\u4efd", "600023": "\u6d59\u80fd\u7535\u529b", "600028": "\u4e2d\u56fd\u77f3\u5316",
    "600029": "\u5357\u65b9\u822a\u7a7a", "600030": "\u4e2d\u4fe1\u8bc1\u5238", "600031": "\u4e09\u4e00\u91cd\u5de5",
    "600036": "\u62db\u5546\u94f6\u884c", "600048": "\u4fdd\u5229\u53d1\u5c55", "600050": "\u4e2d\u56fd\u8054\u901a",
    "600061": "\u56fd\u6295\u7535\u529b", "600066": "\u5b87\u901a\u5ba2\u8f66", "600085": "\u540c\u4ec1\u5802",
    "600089": "\u7279\u53d8\u7535\u5de5", "600104": "\u4e0a\u6c7d\u96c6\u56e2", "600109": "\u56fd\u91d1\u8bc1\u5238",
    "600111": "\u5317\u65b9\u534e\u521b", "600115": "\u4e1c\u65b9\u822a\u7a7a", "600118": "\u4e2d\u56fd\u536b\u661f",
    "600150": "\u4e2d\u56fd\u8239\u8236", "600161": "\u5929\u5766\u751f\u7269", "600176": "\u4e2d\u56fd\u5de8\u77f3",
    "600177": "\u96c5\u6208\u5c14", "600183": "\u751f\u76ca\u79d1\u6280", "600196": "\u590d\u661f\u533b\u836f",
    "600201": "\u751f\u7269\u80a1\u4efd", "600219": "\u5357\u5c71\u94dd\u4e1a", "600233": "\u5706\u901a\u901f\u9012",
    "600276": "\u6052\u745e\u533b\u836f", "600309": "\u4e07\u534e\u5316\u5b66", "600325": "\u534e\u53d1\u80a1\u4efd",
    "600346": "\u6052\u529b\u77f3\u5316", "600352": "\u6d59\u9f99\u5316\u7ea4", "600362": "\u6c5f\u897f\u94dc\u4e1a",
    "600369": "\u897f\u5357\u8bc1\u5238", "600383": "\u91d1\u5730\u96c6\u56e2", "600390": "\u4e94\u77ff\u8d44\u672c",
    "600398": "\u6d77\u6f9c\u4e4b\u5bb6", "600406": "\u56fd\u7535\u5357\u745e", "600415": "\u5c0f\u5546\u54c1\u57ce",
    "600426": "\u534e\u9c81\u6052\u5347", "600436": "\u7247\u4ed4\u762a", "600438": "\u901a\u5a01\u80a1\u4efd",
    "600460": "\u571f\u5170\u5fae", "600486": "\u626c\u519c\u5316\u5de5", "600489": "\u4e2d\u91d1\u9ec4\u91d1",
    "600498": "\u706b\u7130\u7535\u5b50", "600519": "\u8d35\u5dde\u8305\u53f0", "600521": "\u534e\u6d77\u533b\u836f",
    "600535": "\u5929\u58eb\u529b", "600536": "\u4e2d\u56fd\u8f6f\u4ef6", "600547": "\u5c71\u4e1c\u9ec4\u91d1",
    "600570": "\u6052\u751f\u7535\u5b50", "600585": "\u6d77\u87ba\u6c34\u6ce5", "600587": "\u65b0\u534e\u533b\u7597",
    "600588": "\u7528\u53cb\u7f51\u7edc", "600590": "\u5929\u58eb\u529b", "600596": "\u65b0\u5b89\u80a1\u4efd",
    "600600": "\u9752\u5c9b\u5564\u9152", "600606": "\u7eff\u5730\u63a7\u80a1", "600637": "\u767e\u89c6\u97f3",
    "600690": "\u6d77\u5c14\u667a\u5bb6", "600705": "\u4e2d\u822a\u4ea7\u878d", "600745": "\u95f2\u8d35\u4fe1\u606f",
    "600795": "\u56fd\u7535\u7535\u529b", "600809": "\u6c7d\u9152", "600837": "\u6d77\u901a\u8bc1\u5238",
    "600845": "\u5b9d\u4fe1\u8f6f\u4ef6", "600848": "\u81ea\u4eea\u5316", "600859": "\u738b\u5e9c\u4e95",
    "600860": "\u4eac\u4e1c\u65b9A", "600887": "\u4f0a\u5229\u80a1\u4efd", "600893": "\u822a\u53d1\u52a8\u529b",
    "600895": "\u5f20\u6c5f\u9ad8\u79d1", "600900": "\u957f\u6c5f\u7535\u529b", "600905": "\u4e09\u5ce1\u80fd\u6e90",
    "600919": "\u6c5f\u82cf\u94f6\u884c", "600926": "\u675c\u957f\u57ce", "600941": "\u4e2d\u56fd\u79fb\u52a8",
    "601006": "\u5927\u79e6\u94c1\u8def", "601009": "\u5357\u4eac\u94f6\u884c", "601012": "\u9686\u57fa\u7eff\u80fd",
    "601021": "\u6625\u79cb\u822a\u7a7a", "601066": "\u4e2d\u4fe1\u5efa\u6295", "601088": "\u4e2d\u56fd\u795e\u534e",
    "601099": "\u592a\u5e73\u6d0b", "601111": "\u4e2d\u56fd\u56fd\u822a", "601117": "\u4e2d\u56fd\u5316\u5de5",
    "601127": "\u8d5b\u529b\u65af", "601138": "\u5de5\u4e1f\u5bcc\u80a1\u4efd", "601166": "\u5174\u4e1a\u94f6\u884c",
    "601211": "\u56fd\u6cf0\u541b\u5b89", "601225": "\u6c11\u751f\u94f6\u884c", "601228": "\u4e0a\u6d77\u519c\u5546\u884c",
    "601236": "\u7ea2\u5854\u8bc1\u5238", "601238": "\u5e7f\u6c7d\u96c6\u56e2", "601288": "\u519c\u4e1a\u94f6\u884c",
    "601318": "\u4e2d\u56fd\u5e73\u5b89", "601328": "\u4ea4\u901a\u94f6\u884c", "601336": "\u65b0\u534e\u4fdd\u9669",
    "601390": "\u4e2d\u56fd\u4e2d\u94c1", "601398": "\u5de5\u5546\u94f6\u884c", "601601": "\u4e2d\u56fd\u592a\u4fdd",
    "601628": "\u4e2d\u56fd\u4eba\u5bff", "601633": "\u957f\u57ce\u6c7d\u8f66", "601668": "\u4e2d\u56fd\u5efa\u7b51",
    "601669": "\u4e2d\u56fd\u7535\u5efa", "601688": "\u534e\u6cf0\u8bc1\u5238", "601689": "\u62d6\u62c9\u673a",
    "601696": "\u4e2d\u94f6\u8bc1\u5238", "601698": "\u4e2d\u56fd\u536b\u901a", "601728": "\u4e2d\u56fd\u7535\u4fe1",
    "601766": "\u4e2d\u56fd\u4e2d\u8f66", "601788": "\u5149\u5927\u8bc1\u5238", "601799": "\u661f\u5b87\u80a1\u4efd",
    "601808": "\u4e2d\u6d77\u6cb9\u670d", "601816": "\u4eac\u6caa\u9ad8\u94c1", "601825": "\u6c5f\u82cf\u519c\u5546\u884c",
    "601838": "\u6210\u90fd\u94f6\u884c", "601857": "\u4e2d\u56fd\u77f3\u6cb9", "601877": "\u6b63\u6cf0\u7535\u5668",
    "601878": "\u6d59\u8bc1\u8bc1\u5238", "601881": "\u4e2d\u56fd\u94f6\u6cb3", "601888": "\u4e2d\u56fd\u4e2d\u514d",
    "601899": "\u7d2b\u91d1\u77ff\u4e1a", "601900": "\u5357\u65b9\u8bc1\u5238", "601919": "\u4e2d\u8fdc\u6d77\u63a7",
    "601939": "\u5efa\u8bbe\u94f6\u884c", "601985": "\u4e2d\u56fd\u6838\u7535", "601988": "\u4e2d\u56fd\u94f6\u884c",
    "601989": "\u4e2d\u56fd\u91cd\u5de5", "601995": "\u4e2d\u91d1\u516c\u53f8", "601998": "\u4e2d\u4fe1\u94f6\u884c",
    "603000": "\u4eba\u6c11\u7f51", "603019": "\u4e2d\u79d1\u6d66\u6307", "603160": "\u6c47\u9876\u79d1\u6280",
    "603259": "\u836f\u660e\u5eb7\u5fb7", "603288": "\u6d77\u5929\u5473\u7cbe", "603369": "\u4eca\u4e16\u7f18",
    "603501": "\u97e6\u5c14\u80a1\u4efd", "603799": "\u534e\u53cb\u94b4\u4e1a", "603833": "\u6b27\u6d3e\u5bb6\u5c45",
    "603899": "\u666e\u5c14\u53f8\u79d1", "603986": "\u5146\u521b\u80a1\u4efd", "605117": "\u5fb7\u4e1a\u80a1\u4efd",
    "605499": "\u4e1c\u543e\u7f8e", "605589": "\u5723\u8bfa\u80a1\u4efd", "688001": "\u534e\u5174\u6e90\u521b",
    "688005": "\u5bb9\u767e\u7279", "688012": "\u4e2d\u5fae\u516c\u53f8", "688036": "\u4f20\u97f3\u5065\u5eb7",
    "688111": "\u91d1\u5c71\u529e\u516c", "688126": "\u6caa\u78a7\u4fe1\u606f", "688187": "\u65f6\u4ee3\u7535\u6c14",
    "688256": "\u5170\u5c9a\u751f\u7269", "688271": "\u8054\u5f71\u533b\u7597", "688303": "\u5927\u5168\u7535\u5b50",
    "688396": "\u534e\u5cf0\u6d4b\u63a7", "688561": "\u5947\u5b89\u4fe1\u606f", "688599": "\u5929\u5408\u5149\u80fd",
    "688690": "\u7eb3\u8baf\u7cbe\u5bc6", "688981": "\u4e2d\u661f\u5149\u901a",
}


def get_bs_code(stock_input):
    """Convert user input to BaoStock code format"""
    stock_input = stock_input.strip()
    if stock_input.startswith("sh.") or stock_input.startswith("sz."):
        return stock_input, stock_input[3:]
    if stock_input.isdigit():
        code = stock_input
        if code.startswith("6") or code.startswith("68"):
            return "sh." + code, code
        else:
            return "sz." + code, code
    for code, name in STOCK_NAMES.items():
        if stock_input in name or name.startswith(stock_input):
            if code.startswith("6"):
                return "sh." + code, code
            else:
                return "sz." + code, code
    return None, None


class StockAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("\u80a1\u7968\u91cf\u5316\u5206\u6790\u7cfb\u7edf v3.0 - BaoStock")
        self.root.geometry("1400x850")
        self.root.configure(bg="#1a1a2e")
        self.root.minsize(1400, 800)
        
        self.df = None
        self.signals_df = None
        self.trades = []
        self.backtest_result = None
        
        # Crosshair lines for all subplots
        self.cursor_vlines = []
        self.cursor_hlines = []  # 水平线列表，每个子图一个
        self.cursor_hline = None
        self.cursor_text = None
        self.cursor_info_box = None
        self.axes_list = []
        
        self.setup_styles()
        self.create_widgets()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        self.bg_dark = "#1a1a2e"
        self.bg_medium = "#16213e"
        self.bg_light = "#0f3460"
        self.accent = "#e94560"
        self.accent2 = "#00b4d8"
        self.text_white = "#ffffff"
        self.text_gray = "#a0a0b0"
        self.buy_color = "#ff4444"
        self.sell_color = "#00cc66"
        self.gold_color = "#ffd700"
        
        style.configure("Dark.TFrame", background=self.bg_dark)
        style.configure("Medium.TFrame", background=self.bg_medium)
        style.configure("Dark.TLabel", background=self.bg_dark, foreground=self.text_white, font=("Microsoft YaHei", 10))
        style.configure("Title.TLabel", background=self.bg_dark, foreground=self.accent2, font=("Microsoft YaHei", 14, "bold"))
        style.configure("Info.TLabel", background=self.bg_medium, foreground=self.text_white, font=("Consolas", 10))
        style.configure("Buy.TLabel", background=self.bg_medium, foreground=self.buy_color, font=("Consolas", 10, "bold"))
        style.configure("Sell.TLabel", background=self.bg_medium, foreground=self.sell_color, font=("Consolas", 10, "bold"))
        style.configure("Accent.TButton", background=self.accent, foreground=self.text_white, font=("Microsoft YaHei", 11, "bold"), padding=(20, 8))
        style.map("Accent.TButton", background=[("active", "#ff6b81")])
        style.configure("Dark.TEntry", fieldbackground=self.bg_light, foreground=self.text_white, insertcolor=self.text_white)
        style.configure("Treeview", background=self.bg_medium, foreground=self.text_white, fieldbackground=self.bg_medium, font=("Consolas", 9))
        style.configure("Treeview.Heading", background=self.bg_light, foreground=self.text_white, font=("Microsoft YaHei", 9, "bold"))
        style.map("Treeview", background=[("selected", self.accent)])
    
    def create_widgets(self):
        # ========== Top Bar ==========
        top_frame = tk.Frame(self.root, bg=self.bg_medium, height=60)
        top_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        top_frame.pack_propagate(False)
        
        tk.Label(top_frame, text="[STOCK] \u80a1\u7968\u91cf\u5316\u5206\u6790\u7cfb\u7edf v3.0", bg=self.bg_medium, fg=self.accent2, font=("Microsoft YaHei", 16, "bold")).pack(side=tk.LEFT, padx=15)
        
        tk.Label(top_frame, text="\u8f93\u5165\u80a1\u7968\u4ee3\u7801/\u540d\u79f0:", bg=self.bg_medium, fg=self.text_white, font=("Microsoft YaHei", 11)).pack(side=tk.LEFT, padx=(30, 5))
        
        self.stock_var = tk.StringVar(value="002285")
        self.entry = tk.Entry(top_frame, textvariable=self.stock_var, font=("Consolas", 14), width=12,
                             bg=self.bg_light, fg=self.text_white, insertbackground=self.text_white,
                             relief=tk.FLAT, highlightthickness=2, highlightcolor=self.accent2)
        self.entry.pack(side=tk.LEFT, padx=5, pady=10)
        self.entry.bind("<Return>", lambda e: self.analyze())
        
        tk.Label(top_frame, text="\u65f6\u95f4:", bg=self.bg_medium, fg=self.text_white, font=("Microsoft YaHei", 11)).pack(side=tk.LEFT, padx=(20, 5))
        self.time_var = tk.StringVar(value="6M")
        time_options = [("3M", "3M"), ("6M", "6M"), ("1Y", "1Y"), ("2Y", "2Y")]
        for text, val in time_options:
            rb = tk.Radiobutton(top_frame, text=text, variable=self.time_var, value=val,
                               bg=self.bg_medium, fg=self.text_white, selectcolor=self.bg_light,
                               activebackground=self.bg_medium, activeforeground=self.accent2,
                               font=("Microsoft YaHei", 10))
            rb.pack(side=tk.LEFT, padx=3)
        
        btn = tk.Button(top_frame, text="\u5206\u6790", command=self.analyze,
                       bg=self.accent, fg=self.text_white, font=("Microsoft YaHei", 12, "bold"),
                       relief=tk.FLAT, padx=25, pady=3, cursor="hand2",
                       activebackground="#ff6b81", activeforeground=self.text_white)
        btn.pack(side=tk.LEFT, padx=15)
        
        self.status_label = tk.Label(top_frame, text="", bg=self.bg_medium, fg=self.text_gray, font=("Microsoft YaHei", 9))
        self.status_label.pack(side=tk.RIGHT, padx=15)
        
        # ========== Main Content ==========
        # Main container with grid layout
        main_container = tk.Frame(self.root, bg=self.bg_dark)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        main_container.grid_columnconfigure(0, weight=1)  # Left expands
        main_container.grid_columnconfigure(1, weight=0)  # Right fixed
        main_container.grid_rowconfigure(0, weight=1)
        
        # Left: Chart (expandable)
        left_frame = tk.Frame(main_container, bg=self.bg_dark)
        left_frame.grid(row=0, column=0, sticky="nsew")
        
        self.fig = Figure(figsize=(10, 7), facecolor=self.bg_dark)
        self.canvas = FigureCanvasTkAgg(self.fig, master=left_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize empty chart (don't call show_placeholder to avoid layout issues)
        self.fig.set_facecolor(self.bg_dark)
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(self.bg_dark)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        self.canvas.draw()
        
        # Right: Info Panel (fixed width)
        right_frame = tk.Frame(main_container, bg=self.bg_medium, width=280)
        right_frame.grid(row=0, column=1, sticky="ns")
        right_frame.grid_propagate(False)
        
        # Stock info
        self.info_frame = tk.Frame(right_frame, bg=self.bg_medium)
        self.info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.stock_name_label = tk.Label(self.info_frame, text="-- \u8bf7\u8f93\u5165\u80a1\u7968\u4ee3\u7801 --", bg=self.bg_medium, fg=self.accent2, font=("Microsoft YaHei", 11, "bold"))
        self.stock_name_label.pack(anchor=tk.W, pady=(5, 0))
        
        self.stock_price_label = tk.Label(self.info_frame, text="", bg=self.bg_medium, fg=self.text_white, font=("Consolas", 16, "bold"))
        self.stock_price_label.pack(anchor=tk.W)
        
        self.stock_change_label = tk.Label(self.info_frame, text="", bg=self.bg_medium, fg=self.text_gray, font=("Microsoft YaHei", 9))
        self.stock_change_label.pack(anchor=tk.W, pady=(0, 5))
        
        tk.Frame(right_frame, bg=self.bg_light, height=1).pack(fill=tk.X, padx=10, pady=5)
        
        # Current indicators - grid layout (3 columns, resizable)
        tk.Label(right_frame, text=">> \u5f53\u524d\u6307\u6807", bg=self.bg_medium, fg=self.accent2, font=("Microsoft YaHei", 9, "bold")).pack(anchor=tk.W, padx=10, pady=(3, 2))
        
        self.indicators_frame = tk.Frame(right_frame, bg=self.bg_medium)
        self.indicators_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        # Configure grid weights for resizing
        for col in range(3):
            self.indicators_frame.columnconfigure(col, weight=1)
        
        self.ind_labels = {}
        indicators_list = [
            ("MA5", "#ff9800"), ("MA10", "#2196f3"), ("MA20", "#9c27b0"),
            ("MA60", "#607d8b"), ("RSI", "#ff5722"), ("MACD", "#4caf50"),
            ("K", "#e91e63"), ("D", "#00bcd4"), ("J", "#ffeb3b")
        ]
        
        for idx, (name, color) in enumerate(indicators_list):
            row = idx // 3
            col = idx % 3
            self.indicators_frame.rowconfigure(row, weight=1)
            
            # Card-like frame for each indicator
            card = tk.Frame(self.indicators_frame, bg=self.bg_light, padx=5, pady=5)
            card.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            
            tk.Label(card, text=name, bg=self.bg_light, fg=color, font=("Microsoft YaHei", 8, "bold")).pack(anchor=tk.CENTER)
            lbl = tk.Label(card, text="--", bg=self.bg_light, fg=self.text_white, font=("Consolas", 9, "bold"))
            lbl.pack(anchor=tk.CENTER)
            self.ind_labels[name] = lbl
        
        tk.Frame(right_frame, bg=self.bg_light, height=1).pack(fill=tk.X, padx=10, pady=5)
        
        # Signal summary
        tk.Label(right_frame, text=">> \u4fe1\u53f7\u6982\u89c8", bg=self.bg_medium, fg=self.accent2, font=("Microsoft YaHei", 9, "bold")).pack(anchor=tk.W, padx=10, pady=(3, 2))
        
        self.signal_summary_frame = tk.Frame(right_frame, bg=self.bg_medium)
        self.signal_summary_frame.pack(fill=tk.X, padx=10)
        
        self.current_signal_label = tk.Label(self.signal_summary_frame, text="--", bg=self.bg_medium, fg=self.text_gray, font=("Microsoft YaHei", 14, "bold"))
        self.current_signal_label.pack(anchor=tk.W, pady=2)
        
        self.signal_detail_label = tk.Label(self.signal_summary_frame, text="", bg=self.bg_medium, fg=self.text_gray, font=("Microsoft YaHei", 8))
        self.signal_detail_label.pack(anchor=tk.W)
        
        tk.Frame(right_frame, bg=self.bg_light, height=1).pack(fill=tk.X, padx=10, pady=5)
        
        # Backtest result - grid layout (2 columns, resizable)
        tk.Label(right_frame, text=">> \u56de\u6d4b\u7ed3\u679c", bg=self.bg_medium, fg=self.gold_color, font=("Microsoft YaHei", 9, "bold")).pack(anchor=tk.W, padx=10, pady=(3, 2))
        
        self.backtest_frame = tk.Frame(right_frame, bg=self.bg_medium)
        self.backtest_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        # Configure grid weights
        for col in range(2):
            self.backtest_frame.columnconfigure(col, weight=1)
        
        self.backtest_labels = {}
        backtest_items = [
            ("\u521d\u59cb\u8d44\u91d1", "#ff9800"), ("\u6700\u7ec8\u8d44\u4ea7", "#2196f3"),
            ("\u603b\u6536\u76ca", "#4caf50"), ("\u6536\u76ca\u7387", "#e91e63"),
            ("\u4ea4\u6613\u6b21\u6570", "#9c27b0"), ("\u80dc\u7387", "#00bcd4")
        ]
        
        for idx, (name, color) in enumerate(backtest_items):
            row = idx // 2
            col = idx % 2
            self.backtest_frame.rowconfigure(row, weight=1)
            
            card = tk.Frame(self.backtest_frame, bg=self.bg_light, padx=5, pady=5)
            card.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            
            tk.Label(card, text=name, bg=self.bg_light, fg=color, font=("Microsoft YaHei", 8, "bold")).pack(anchor=tk.CENTER)
            lbl = tk.Label(card, text="--", bg=self.bg_light, fg=self.text_white, font=("Consolas", 9, "bold"))
            lbl.pack(anchor=tk.CENTER)
            self.backtest_labels[name] = lbl
        
        tk.Frame(right_frame, bg=self.bg_light, height=1).pack(fill=tk.X, padx=10, pady=5)
        
        # Signal list
        tk.Label(right_frame, text=">> \u4fe1\u53f7\u5217\u8868", bg=self.bg_medium, fg=self.accent2, font=("Microsoft YaHei", 9, "bold")).pack(anchor=tk.W, padx=10, pady=(3, 2))
        
        tree_frame = tk.Frame(right_frame, bg=self.bg_medium)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.tree = ttk.Treeview(tree_frame, columns=("date", "type", "price", "reason"), show="headings", height=12)
        self.tree.heading("date", text="\u65e5\u671f")
        self.tree.heading("type", text="\u7c7b\u578b")
        self.tree.heading("price", text="\u4ef7\u683c")
        self.tree.heading("reason", text="\u539f\u56e0")
        self.tree.column("date", width=70)
        self.tree.column("type", width=40)
        self.tree.column("price", width=50)
        self.tree.column("reason", width=110)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def show_placeholder(self):
        # Clear figure without destroying axes
        for ax in self.fig.axes:
            ax.remove()
        self.fig.set_facecolor(self.bg_dark)
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(self.bg_dark)
        ax.text(0.5, 0.5, "\u8f93\u5165\u80a1\u7968\u4ee3\u7801\u5f00\u59cb\u5206\u6790\n\n\u652f\u6301\u4ee3\u7801/\u540d\u79f0\u641c\u7d22\n\u5982: 002285 \u6216 \u4e16\u8054\u884c",
               transform=ax.transAxes, ha="center", va="center", fontsize=18, color=self.text_gray, fontfamily="Microsoft YaHei")
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        self.canvas.draw()
    
    def analyze(self):
        stock_input = self.stock_var.get().strip()
        if not stock_input:
            messagebox.showwarning("\u63d0\u793a", "\u8bf7\u8f93\u5165\u80a1\u7968\u4ee3\u7801\u6216\u540d\u79f0")
            return
        self.status_label.config(text="\u6b63\u5728\u83b7\u53d6\u6570\u636e...")
        self.root.update()
        threading.Thread(target=self._do_analyze, args=(stock_input,), daemon=True).start()
    
    def _do_analyze(self, stock_input):
        try:
            bs_code, code = get_bs_code(stock_input)
            if bs_code is None:
                self.root.after(0, lambda: messagebox.showerror("\u9519\u8bef", "\u672a\u627e\u5230\u80a1\u7968\uff1a" + stock_input))
                return
            
            time_map = {"3M": 90, "6M": 180, "1Y": 365, "2Y": 730}
            days = time_map.get(self.time_var.get(), 180)
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=days)
            
            lg = bs.login()
            if lg.error_code != "0":
                self.root.after(0, lambda: messagebox.showerror("\u9519\u8bef", "BaoStock\u767b\u5f55\u5931\u8d25"))
                return
            
            rs = bs.query_history_k_data_plus(bs_code,
                "date,open,high,low,close,volume,amount,turn,pctChg",
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                frequency="d")
            
            data_list = []
            while rs.error_code == "0" and rs.next():
                data_list.append(rs.get_row_data())
            
            bs.logout()
            
            if len(data_list) < 30:
                self.root.after(0, lambda: messagebox.showerror("\u9519\u8bef", "\u6570\u636e\u4e0d\u8db3\uff0c\u8bf7\u5c1d\u8bd5\u66f4\u957f\u7684\u65f6\u95f4\u8303\u56f4"))
                return
            
            df = pd.DataFrame(data_list, columns=["date","open","high","low","close","volume","amount","turn","pctChg"])
            for col in ["open","high","low","close","volume","amount","turn","pctChg"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            df = df.dropna(subset=["close"]).reset_index(drop=True)
            
            self.df = df
            stock_name = STOCK_NAMES.get(code, "")
            
            self._calc_indicators()
            self._gen_signals()
            self._run_backtest()
            
            self.root.after(0, lambda: self._update_ui(code, stock_name))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("\u9519\u8bef", str(e)))
            self.root.after(0, lambda: self.status_label.config(text="\u5206\u6790\u5931\u8d25"))
    
    def _calc_indicators(self):
        df = self.df
        close = df["close"]
        
        for period in [5, 10, 20, 60]:
            df[f"MA{period}"] = close.rolling(period).mean()
        
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs_val = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs_val))
        
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        df["DIF"] = ema12 - ema26
        df["DEA"] = df["DIF"].ewm(span=9).mean()
        df["MACD"] = (df["DIF"] - df["DEA"]) * 2
        
        low_9 = df["low"].rolling(9).min()
        high_9 = df["high"].rolling(9).max()
        rsv = ((close - low_9) / (high_9 - low_9) * 100).fillna(50)
        df["K"] = rsv.ewm(com=2).mean()
        df["D"] = df["K"].ewm(com=2).mean()
        df["J"] = 3 * df["K"] - 2 * df["D"]
        
        df["BOLL_MID"] = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        df["BOLL_UP"] = df["BOLL_MID"] + 2 * std20
        df["BOLL_DN"] = df["BOLL_MID"] - 2 * std20
    
    def _gen_signals(self):
        df = self.df
        signals = []
        
        for i in range(len(df)):
            if i < 60:
                signals.append({"signal": "HOLD", "reason": ""})
                continue
            
            ma5 = df.iloc[i]["MA5"]
            ma10 = df.iloc[i]["MA10"]
            ma20 = df.iloc[i]["MA20"]
            rsi = df.iloc[i]["RSI"]
            dif = df.iloc[i]["DIF"]
            dea = df.iloc[i]["DEA"]
            k = df.iloc[i]["K"]
            j = df.iloc[i]["J"]
            price = df.iloc[i]["close"]
            
            ma5_prev = df.iloc[i-1]["MA5"]
            ma10_prev = df.iloc[i-1]["MA10"]
            dif_prev = df.iloc[i-1]["DIF"]
            dea_prev = df.iloc[i-1]["DEA"]
            
            sig = "HOLD"
            reason = ""
            
            if ma5_prev <= ma10_prev and ma5 > ma10 and price > ma20:
                sig = "BUY"
                reason = "MA5\u91d1\u53c9\u4e0a\u7a7fMA10"
            elif rsi < 25:
                sig = "BUY"
                reason = f"RSI\u4e25\u91cd\u8d85\u5356({rsi:.0f})"
            elif rsi < 30 and rsi > 0:
                sig = "BUY"
                reason = f"RSI\u8d85\u5356({rsi:.0f})"
            elif k < 20 and j < 0:
                sig = "BUY"
                reason = f"KDJ\u8d85\u5356(K={k:.0f},J={j:.0f})"
            elif dif_prev <= dea_prev and dif > dea and dif < 0:
                sig = "BUY"
                reason = "MACD\u4f4e\u4f4d\u91d1\u53c9"
            elif ma5_prev >= ma10_prev and ma5 < ma10:
                sig = "SELL"
                reason = "MA5\u6b7b\u53c9\u4e0b\u7a7fMA10"
            elif rsi > 80:
                sig = "SELL"
                reason = f"RSI\u4e25\u91cd\u8d85\u4e70({rsi:.0f})"
            elif rsi > 70:
                sig = "SELL"
                reason = f"RSI\u8d85\u4e70({rsi:.0f})"
            elif k > 85 and j > 95:
                sig = "SELL"
                reason = f"KDJ\u8d85\u4e70(K={k:.0f},J={j:.0f})"
            elif dif_prev >= dea_prev and dif < dea and dif > 0:
                sig = "SELL"
                reason = "MACD\u9ad8\u4f4d\u6b7b\u53c9"
            
            signals.append({"signal": sig, "reason": reason})
        
        df["signal"] = [s["signal"] for s in signals]
        df["reason"] = [s["reason"] for s in signals]
        self.signals_df = df
    
    def _run_backtest(self):
        """Run backtest simulation and store results"""
        df = self.df
        cash = 100000.0
        shares = 0
        trades = []
        cost = 0
        
        for i in range(len(df)):
            row = df.iloc[i]
            if row["signal"] == "BUY" and shares == 0:
                buy_price = row["close"]
                shares = int(cash / buy_price / 100) * 100
                if shares == 0:
                    continue
                cost = shares * buy_price
                cash -= cost
                trades.append({"type": "BUY", "date": row["date"], "price": buy_price, "shares": shares, "amount": cost})
            elif row["signal"] == "SELL" and shares > 0:
                sell_price = row["close"]
                proceeds = shares * sell_price
                cash += proceeds
                profit = proceeds - cost
                trades.append({"type": "SELL", "date": row["date"], "price": sell_price, "shares": shares, "amount": proceeds, "profit": profit})
                shares = 0
        
        last_price = df.iloc[-1]["close"]
        final_val = cash + shares * last_price
        profit = final_val - 100000
        pct_ret = (final_val / 100000 - 1) * 100
        
        # Calculate win rate
        win_count = sum(1 for t in trades if t["type"] == "SELL" and t.get("profit", 0) > 0)
        sell_count = sum(1 for t in trades if t["type"] == "SELL")
        win_rate = (win_count / sell_count * 100) if sell_count > 0 else 0
        
        self.trades = trades
        self.backtest_result = {
            "initial": 100000,
            "final": final_val,
            "profit": profit,
            "pct_ret": pct_ret,
            "trade_count": len([t for t in trades if t["type"] == "SELL"]),
            "win_rate": win_rate,
            "trades": trades
        }
    
    def _update_ui(self, code, name):
        df = self.df
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        display_name = f"{name} ({code})" if name else f"({code})"
        self.stock_name_label.config(text=display_name)
        
        price = latest["close"]
        self.stock_price_label.config(text=f"{price:.2f}")
        
        pct = latest["pctChg"] if not pd.isna(latest["pctChg"]) else ((price - prev["close"]) / prev["close"] * 100)
        change_color = self.buy_color if pct >= 0 else self.sell_color
        arrow = "\u2191" if pct >= 0 else "\u2193"
        self.stock_change_label.config(text=f"{arrow} {abs(pct):.2f}%  |  {df.iloc[0]['date']} ~ {latest['date']}", fg=change_color)
        
        for ind in ["MA5", "MA10", "MA20", "MA60", "RSI", "MACD", "K", "D", "J"]:
            val = latest.get(ind)
            if pd.notna(val):
                self.ind_labels[ind].config(text=f"{val:.2f}")
                if ind == "RSI":
                    self.ind_labels[ind].config(fg=self.buy_color if val < 30 else (self.sell_color if val > 70 else self.text_white))
                elif ind == "MACD":
                    self.ind_labels[ind].config(fg=self.buy_color if val > 0 else self.sell_color)
                elif ind == "J":
                    self.ind_labels[ind].config(fg=self.buy_color if val < 0 else (self.sell_color if val > 100 else self.text_white))
                else:
                    self.ind_labels[ind].config(fg=self.text_white)
            else:
                self.ind_labels[ind].config(text="--")
        
        cur_sig = latest["signal"]
        cur_reason = latest["reason"]
        if cur_sig == "BUY":
            self.current_signal_label.config(text="\u25b2 \u5efa\u8bae\u4e70\u5165", fg=self.buy_color)
        elif cur_sig == "SELL":
            self.current_signal_label.config(text="\u25bc \u5efa\u8bae\u5356\u51fa", fg=self.sell_color)
        else:
            self.current_signal_label.config(text="-- \u89c2\u671b", fg="#ffaa00")
        
        self.signal_detail_label.config(text=cur_reason if cur_reason else "\u65e0\u660e\u786e\u4fe1\u53f7")
        
        # Update backtest results
        if self.backtest_result:
            bt = self.backtest_result
            self.backtest_labels["\u521d\u59cb\u8d44\u91d1"].config(text=f"{bt['initial']:,.0f}")
            self.backtest_labels["\u6700\u7ec8\u8d44\u4ea7"].config(text=f"{bt['final']:,.0f}")
            profit_color = self.buy_color if bt['profit'] >= 0 else self.sell_color
            self.backtest_labels["\u603b\u6536\u76ca"].config(text=f"{bt['profit']:+,.0f}", fg=profit_color)
            self.backtest_labels["\u6536\u76ca\u7387"].config(text=f"{bt['pct_ret']:+.2f}%", fg=profit_color)
            self.backtest_labels["\u4ea4\u6613\u6b21\u6570"].config(text=f"{bt['trade_count']} \u7b14")
            self.backtest_labels["\u80dc\u7387"].config(text=f"{bt['win_rate']:.1f}%")
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        sig_df = df[df["signal"].isin(["BUY", "SELL"])].tail(30)
        for _, row in sig_df.iterrows():
            tag = "buy" if row["signal"] == "BUY" else "sell"
            self.tree.insert("", tk.END, values=(row["date"], row["signal"], f"{row['close']:.2f}", row["reason"]), tags=(tag,))
        self.tree.tag_configure("buy", foreground=self.buy_color)
        self.tree.tag_configure("sell", foreground=self.sell_color)
        
        # Auto-adjust tree column widths based on content
        self.tree.column("date", width=85, minwidth=70)
        self.tree.column("type", width=45, minwidth=35)
        self.tree.column("price", width=55, minwidth=45)
        self.tree.column("reason", width=140, minwidth=100)
        
        self._draw_chart()
        self._show_signal_notification()
        
        self.status_label.config(text=f"\u5206\u6790\u5b8c\u6210 | {len(df)}\u65e5\u6570\u636e | BaoStock")
    
    def _show_signal_notification(self):
        """Show notification popup for latest signal"""
        if self.df is None or len(self.df) < 2:
            return
        
        latest = self.df.iloc[-1]
        prev = self.df.iloc[-2]
        
        # Check if latest or previous day has a signal
        for idx, row in [("\u4eca\u65e5", latest), ("\u6628\u65e5", prev)]:
            if row["signal"] in ["BUY", "SELL"]:
                sig_type = "\u4e70\u5165\u4fe1\u53f7" if row["signal"] == "BUY" else "\u5356\u51fa\u4fe1\u53f7"
                color = self.buy_color if row["signal"] == "BUY" else self.sell_color
                icon = "\u25b2" if row["signal"] == "BUY" else "\u25bc"
                
                msg = f"{icon} {idx}{sig_type}\n\n"
                msg += f"\u80a1\u7968: {self.stock_name_label.cget('text')}\n"
                msg += f"\u65e5\u671f: {row['date']}\n"
                msg += f"\u4ef7\u683c: {row['close']:.2f}\n"
                msg += f"\u539f\u56e0: {row['reason']}\n\n"
                
                if self.backtest_result:
                    bt = self.backtest_result
                    msg += f"\u56de\u6d4b\u6536\u76ca\u7387: {bt['pct_ret']:+.2f}%\n"
                    msg += f"\u5386\u53f2\u80dc\u7387: {bt['win_rate']:.1f}%"
                
                self.root.after(500, lambda m=msg, c=color: self._create_notification(m, c))
                break
    
    def _create_notification(self, message, color):
        """Create a notification popup window"""
        notif = tk.Toplevel(self.root)
        notif.title("\u4ea4\u6613\u4fe1\u53f7\u63d0\u9192")
        notif.geometry("350x200+{}+{}".format(self.root.winfo_x() + 100, self.root.winfo_y() + 100))
        notif.configure(bg=self.bg_medium)
        notif.overrideredirect(True)
        notif.attributes("-topmost", True)
        
        # Border frame
        border = tk.Frame(notif, bg=color, padx=2, pady=2)
        border.pack(fill=tk.BOTH, expand=True)
        
        inner = tk.Frame(border, bg=self.bg_medium)
        inner.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(inner, text=message, bg=self.bg_medium, fg=self.text_white,
                font=("Microsoft YaHei", 11), justify=tk.LEFT, padx=15, pady=15).pack(fill=tk.BOTH, expand=True)
        
        # Auto close after 5 seconds
        notif.after(5000, notif.destroy)
    
    def _draw_chart(self):
        df = self.df
        
        # Reuse existing axes if available, otherwise create new ones
        if not hasattr(self, 'axes_list') or len(self.axes_list) != 5:
            self.fig.clear()
            # Create subplots: K-line + Volume + RSI + MACD + KDJ
            gs = self.fig.add_gridspec(5, 1, height_ratios=[4, 1, 1, 1, 1], hspace=0.03)
            
            ax_kline = self.fig.add_subplot(gs[0])
            ax_vol = self.fig.add_subplot(gs[1], sharex=ax_kline)
            ax_rsi = self.fig.add_subplot(gs[2], sharex=ax_kline)
            ax_macd = self.fig.add_subplot(gs[3], sharex=ax_kline)
            ax_kdj = self.fig.add_subplot(gs[4], sharex=ax_kline)
            
            self.axes_list = [ax_kline, ax_vol, ax_rsi, ax_macd, ax_kdj]
        else:
            # Clear existing axes
            for ax in self.axes_list:
                ax.clear()
            ax_kline, ax_vol, ax_rsi, ax_macd, ax_kdj = self.axes_list
        for ax in self.axes_list:
            ax.set_facecolor("#0d1117")
            ax.tick_params(colors=self.text_gray, labelsize=8)
            for spine in ax.spines.values():
                spine.set_color("#30363d")
            ax.yaxis.label.set_color(self.text_gray)
        
        dates = pd.to_datetime(df["date"])
        x = np.arange(len(dates))
        
        # ===== K-line Chart =====
        for i in range(len(df)):
            row = df.iloc[i]
            o, h, l, c = row["open"], row["high"], row["low"], row["close"]
            color = self.buy_color if c >= o else self.sell_color
            
            ax_kline.plot([i, i], [l, h], color=color, linewidth=0.8)
            body_bottom = min(o, c)
            body_height = abs(c - o)
            rect = FancyBboxPatch((i - 0.35, body_bottom), 0.7, max(body_height, 0.005),
                                  boxstyle="square,pad=0", facecolor=color, edgecolor=color, linewidth=0.5)
            ax_kline.add_patch(rect)
        
        # MA lines
        for period, color, alpha in [(5, "#ff9800", 0.9), (10, "#2196f3", 0.9), (20, "#9c27b0", 0.8), (60, "#607d8b", 0.6)]:
            col = f"MA{period}"
            if col in df.columns:
                ax_kline.plot(x, df[col], color=color, linewidth=1.0, alpha=alpha, label=f"MA{period}")
        
        # Bollinger Bands
        if "BOLL_UP" in df.columns:
            ax_kline.plot(x, df["BOLL_UP"], color="#555555", linewidth=0.5, linestyle="--", alpha=0.5)
            ax_kline.plot(x, df["BOLL_DN"], color="#555555", linewidth=0.5, linestyle="--", alpha=0.5)
            ax_kline.fill_between(x, df["BOLL_UP"], df["BOLL_DN"], alpha=0.05, color="gray")
        
        # Buy/Sell markers
        buy_df = df[df["signal"] == "BUY"]
        sell_df = df[df["signal"] == "SELL"]
        
        if len(buy_df) > 0:
            buy_x = [df.index.get_loc(idx) for idx in buy_df.index]
            buy_y = buy_df["low"].values * 0.98
            ax_kline.scatter(buy_x, buy_y, marker="^", color=self.buy_color, s=120, zorder=5, edgecolors="white", linewidths=0.5, label="\u4e70\u5165")
        
        if len(sell_df) > 0:
            sell_x = [df.index.get_loc(idx) for idx in sell_df.index]
            sell_y = sell_df["high"].values * 1.02
            ax_kline.scatter(sell_x, sell_y, marker="v", color=self.sell_color, s=120, zorder=5, edgecolors="white", linewidths=0.5, label="\u5356\u51fa")
        
        ax_kline.legend(loc="upper left", fontsize=8, facecolor="#0d1117", edgecolor="#30363d", labelcolor=self.text_gray, ncol=6)
        ax_kline.set_ylabel("\u4ef7\u683c", fontfamily="Microsoft YaHei", fontsize=9)
        # Light horizontal grid lines only (no prominent vertical lines)
        ax_kline.grid(True, alpha=0.12, color="#30363d", linestyle="-", linewidth=0.5)
        plt.setp(ax_kline.get_xticklabels(), visible=False)
        
        # ===== Volume =====
        for i in range(len(df)):
            row = df.iloc[i]
            color = self.buy_color if row["close"] >= row["open"] else self.sell_color
            ax_vol.bar(i, row["volume"], color=color, alpha=0.7, width=0.7)
        ax_vol.set_ylabel("VOL", fontfamily="Microsoft YaHei", fontsize=8)
        # Light horizontal grid lines only (no prominent vertical lines)
        ax_vol.grid(True, alpha=0.12, color="#30363d", linestyle="-", linewidth=0.5)
        plt.setp(ax_vol.get_xticklabels(), visible=False)
        
        # ===== RSI =====
        ax_rsi.plot(x, df["RSI"], color="#ff9800", linewidth=1.0)
        ax_rsi.axhline(y=70, color=self.sell_color, linestyle="--", linewidth=0.5, alpha=0.7)
        ax_rsi.axhline(y=30, color=self.buy_color, linestyle="--", linewidth=0.5, alpha=0.7)
        ax_rsi.fill_between(x, 70, df["RSI"], where=df["RSI"] >= 70, alpha=0.15, color=self.sell_color)
        ax_rsi.fill_between(x, 30, df["RSI"], where=df["RSI"] <= 30, alpha=0.15, color=self.buy_color)
        ax_rsi.set_ylabel("RSI", fontsize=8)
        ax_rsi.set_ylim(0, 100)
        # Light horizontal grid lines only (no prominent vertical lines)
        ax_rsi.grid(True, alpha=0.12, color="#30363d", linestyle="-", linewidth=0.5)
        plt.setp(ax_rsi.get_xticklabels(), visible=False)
        
        # ===== MACD =====
        ax_macd.plot(x, df["DIF"], color="#ff9800", linewidth=1.0, label="DIF")
        ax_macd.plot(x, df["DEA"], color="#2196f3", linewidth=1.0, label="DEA")
        
        macd_colors = [self.buy_color if v >= 0 else self.sell_color for v in df["MACD"]]
        ax_macd.bar(x, df["MACD"], color=macd_colors, alpha=0.6, width=0.7)
        ax_macd.axhline(y=0, color=self.text_gray, linewidth=0.5)
        ax_macd.set_ylabel("MACD", fontsize=8)
        ax_macd.legend(loc="upper left", fontsize=7, facecolor="#0d1117", edgecolor="#30363d", labelcolor=self.text_gray)
        # Light horizontal grid lines only (no prominent vertical lines)
        ax_macd.grid(True, alpha=0.12, color="#30363d", linestyle="-", linewidth=0.5)
        plt.setp(ax_macd.get_xticklabels(), visible=False)
        
        # ===== KDJ =====
        ax_kdj.plot(x, df["K"], color="#ff9800", linewidth=1.0, label="K")
        ax_kdj.plot(x, df["D"], color="#2196f3", linewidth=1.0, label="D")
        ax_kdj.plot(x, df["J"], color="#9c27b0", linewidth=1.0, label="J")
        ax_kdj.axhline(y=80, color=self.sell_color, linestyle="--", linewidth=0.5, alpha=0.5)
        ax_kdj.axhline(y=20, color=self.buy_color, linestyle="--", linewidth=0.5, alpha=0.5)
        ax_kdj.fill_between(x, 80, 100, alpha=0.1, color=self.sell_color)
        ax_kdj.fill_between(x, 0, 20, alpha=0.1, color=self.buy_color)
        ax_kdj.set_ylabel("KDJ", fontsize=8)
        ax_kdj.set_ylim(0, 100)
        ax_kdj.legend(loc="upper left", fontsize=7, facecolor="#0d1117", edgecolor="#30363d", labelcolor=self.text_gray)
        # Light horizontal + subtle X-axis grid lines (no prominent vertical lines)
        ax_kdj.grid(True, alpha=0.12, color="#30363d", linestyle="-", linewidth=0.5)
        ax_kdj.grid(True, which='major', axis='x', alpha=0.15, color="#30363d", linestyle="-", linewidth=0.3)
        
        # X-axis date labels
        tick_step = max(1, len(dates) // 10)
        tick_positions = x[::tick_step]
        tick_labels = [d.strftime("%m/%d") for d in dates[::tick_step]]
        ax_kdj.set_xticks(tick_positions)
        ax_kdj.set_xticklabels(tick_labels, rotation=30, fontsize=7)
        
        self.fig.subplots_adjust(left=0.06, right=0.98, top=0.97, bottom=0.05)
        
        # ===== Sync Crosshair =====
        self._setup_sync_crosshair()
        
        self.canvas.draw()
        
    def _setup_sync_crosshair(self):
        """Setup synchronized crosshair (horizontal + vertical lines) across all subplots.
        
        Lines are mouse-following: hlines follow mouse Y, vlines follow mouse X.
        Events registered only once to avoid duplicates.
        """
        # Reset crosshair references - ax.clear() handles old artist cleanup
        self.cursor_hlines = []
        self.cursor_vlines = []
        self.cursor_price_text = None
        self.cursor_info_box = None

        # One horizontal line + one vertical line per subplot
        for ax in self.axes_list:
            hline = ax.axhline(y=0, color='#ffcc00', linewidth=1.0, alpha=0.9)
            vline = ax.axvline(x=0, color='#ffcc00', linewidth=1.0, alpha=0.9)
            hline.set_visible(False)
            vline.set_visible(False)
            self.cursor_hlines.append(hline)
            self.cursor_vlines.append(vline)

        # Price annotation at cursor position (on main K-line chart)
        self.cursor_price_text = self.axes_list[0].text(
            0.5, 0.02, "", transform=self.axes_list[0].transAxes,
            fontsize=10, color='#ffcc00', fontweight='bold',
            ha='center', va='bottom',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#1a1a2e', edgecolor='#ffcc00', alpha=0.95)
        )
        self.cursor_price_text.set_visible(False)

        # Info box showing data details (bottom-left of main chart)
        self.cursor_info_box = self.axes_list[0].text(
            0.02, 0.02, "", transform=self.axes_list[0].transAxes,
            fontsize=9, color="white", verticalalignment="bottom",
            horizontalalignment="left",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#1a1a2e",
                     edgecolor="#00b4d8", alpha=0.95, linewidth=1.5)
        )
        self.cursor_info_box.set_visible(False)

        # Register mouse events only ONCE
        if not getattr(self, '_crosshair_connected', False):
            self.canvas.mpl_connect("motion_notify_event", self._on_mouse_move_sync)
            self.canvas.mpl_connect("axes_leave_event", self._on_mouse_leave_sync)
            self._crosshair_connected = True

    def _on_mouse_move_sync(self, event):
        """Handle mouse movement - move crosshair lines to follow the mouse in real time."""
        # Guard: check all prerequisites
        if self.df is None:
            self._hide_sync_crosshair()
            return
        if event.xdata is None or event.ydata is None or event.inaxes is None:
            self._hide_sync_crosshair()
            return
        if not hasattr(self, 'axes_list') or not self.axes_list:
            self._hide_sync_crosshair()
            return

        # Check if mouse is in any of our tracked axes
        is_tracked = any(event.inaxes is ax for ax in self.axes_list)
        if not is_tracked:
            self._hide_sync_crosshair()
            return

        x = event.xdata
        y = event.ydata

        # Both horizontal AND vertical lines visible in ALL subplots
        for i, (hline, vline) in enumerate(zip(self.cursor_hlines, self.cursor_vlines)):
            vline.set_xdata([x, x])
            vline.set_visible(True)
            # Horizontal line: visible in all subplots, follows mouse Y
            hline.set_ydata([y, y])
            hline.set_visible(True)

        # Index into dataframe for data lookup
        x_idx = int(round(x))
        if 0 <= x_idx < len(self.df):
            row = self.df.iloc[x_idx]
            close_price = float(row['close'])

            # Price annotation: X=date label, Y=close price
            date_str = str(row['date'])[:10] if 'date' in row else ''
            self.cursor_price_text.set_text(f"\u2022 {close_price:.2f}")
            self.cursor_price_text.set_position((x, close_price))
            self.cursor_price_text.set_visible(True)

            # Info box
            info = f"\u6708/{date_str[5:]}\n"
            info += f"O:{row['open']:.2f} H:{row['high']:.2f}\n"
            info += f"L:{row['low']:.2f} C:{row['close']:.2f}\n"
            vol = row.get('volume', 0) / 10000
            info += f"VOL:{vol:.0f}\u4e07"
            if pd.notna(row.get('MA5')):
                info += f"\nMA5:{row['MA5']:.2f}"
            if pd.notna(row.get('RSI')):
                info += f" RSI:{row['RSI']:.1f}"
            if pd.notna(row.get('K')):
                info += f"\nK:{row['K']:.1f} D:{row['D']:.1f} J:{row['J']:.1f}"
            if pd.notna(row.get('MACD')):
                info += f"\nMACD:{row['MACD']:.3f}"
            if row.get('signal') == 'BUY':
                info += f"\n\u25b2 \u4e70\u5165: {row.get('reason','')}"
            elif row.get('signal') == 'SELL':
                info += f"\n\u25bc \u5356\u51fa: {row.get('reason','')}"

            self.cursor_info_box.set_text(info)
            self.cursor_info_box.set_visible(True)
        else:
            self.cursor_price_text.set_visible(False)
            self.cursor_info_box.set_visible(False)

        self.canvas.draw_idle()

    def _on_mouse_leave_sync(self, event):
        self._hide_sync_crosshair()

    def _hide_sync_crosshair(self):
        """Hide all crosshair elements."""
        if self.cursor_price_text:
            self.cursor_price_text.set_visible(False)
        if self.cursor_info_box:
            self.cursor_info_box.set_visible(False)
        for hline in self.cursor_hlines:
            hline.set_visible(False)
        for vline in self.cursor_vlines:
            vline.set_visible(False)
        if self.canvas:
            self.canvas.draw_idle()


def main():
    import matplotlib
    matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial"]
    matplotlib.rcParams["axes.unicode_minus"] = False
    
    root = tk.Tk()
    app = StockAnalyzer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
