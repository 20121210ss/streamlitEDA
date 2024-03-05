import streamlit as st
from streamlit.components.v1 import html
from ydata_profiling import ProfileReport
import re
from wordcloud import WordCloud
import allVariable

wordcloud = WordCloud("C:\\Windows\\Fonts\\msyh.ttc")

def EDAmin():
    
    minreport = st.empty()
    
    with minreport :
        # 若已有各特徵的分析報告
        if allVariable.minReport is not None:
            if allVariable.OneColReport is not None:
                html(allVariable.OneColReport,height=allVariable.Height,scrolling=True)
            # 已有各特徵的分析報告有點選單一欄位，則顯示該特徵欄位的EDA
                if allVariable.selectCol is not None:
                    reRunOneColEDAreport(allVariable.selectCol)
                # 已有報告未選欄位，則調用已有的分析報告
                else:
                    html(allVariable.minReport,height=allVariable.Height,scrolling=True)
                            
        # 若沒有各特徵的分析報告，生成報告    
        else:
            reRunEDAminreport()
                        
    # 若user有更動資料集，點選以重新生成報告
    if st.button("重新生成報告"):
        allVariable.minReport = None
        with minreport :
            reRunEDAminreport()
        
# 單一欄位的EDA報告，欲輸入值為選擇第幾個特徵欄位
def reRunOneColEDAreport(selindex):
    if allVariable.minReport is not None:
        # 使用split方法切割字串，以拆出單一特徵欄位的報告
        sr12 = '''<div class="row spacing">'''
        sr2 = '''<div class=variable>'''
        split_result = allVariable.minReport.split(sr12,2)
        result = split_result[0]+sr12+split_result[-1]
        split_result = result.split(sr2)
        result = split_result[0]+sr2+split_result[selindex]+sr2+split_result[-1]
        allVariable.OneColReport = result
        html(result,height=allVariable.Height,scrolling=True)
        
# 各特徵欄位的EDA報告            
def reRunEDAminreport():
    try:
        if allVariable.df is not None:    
            # 創建 Profile 報告
            profile = ProfileReport(allVariable.df,minimal=True)
            allVariable.minReport = profile.to_html()
            
            # 使用split方法切割字串，僅保留顯示各變數分析的部分
            sr = '''<div class="row header">'''
            split_result = allVariable.minReport.split(sr)
            result = split_result[0]+sr+split_result[2]
            allVariable.minReport = result
            html(result,height=allVariable.Height,scrolling=True)
    except:
        st.text("EDA簡略報告生成有誤")