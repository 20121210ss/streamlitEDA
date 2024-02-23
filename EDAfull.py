import streamlit as st
from streamlit.components.v1 import html
from ydata_profiling import ProfileReport 
import allVariable
from wordcloud import WordCloud

wordcloud = WordCloud("C:\\Windows\\Fonts\\msyh.ttc")

def EDAfull():
    
    fullreport = st.empty()
    
    with fullreport:
        # 若以生成過報告，則調用生成好的報告
        if allVariable.fullReport is not None:
            html(allVariable.fullReport,height=allVariable.Height,scrolling=True)
        # 否則生成報告
        else:
            reRunEDAfullreport()
            
        # 若user有更動資料集，點選以重新生成報告
    if st.button("生成報告"):
        allVariable.fullReport = None
        with fullreport:
            reRunEDAfullreport()
        
# 完整EDA報告
def reRunEDAfullreport():
    if allVariable.df is not None:
        try:
            # 創建 Profile 報告
            profile = ProfileReport(allVariable.df)
            allVariable.fullReport = profile.to_html()
            html(allVariable.fullReport,height=allVariable.Height,scrolling=True)
        except:
            st.text("完整報告出錯")