from shiny import reactive, render, ui
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib_fontja
import pandas as pd

CODE_TO_COMPANY = {
    "7203.T": "トヨタ自動車",
    "7974.T": "任天堂",
    "9984.T": "ソフトバンクG"
}


    
    