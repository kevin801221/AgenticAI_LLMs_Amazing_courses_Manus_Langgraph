import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

class WolframCulinaryAPI:
    def __init__(self, app_id: str):
        self.app_id = app_id
        self.base_url = "http://api.wolframalpha.com/v2/query"

    def query(self, input_text: str) -> dict:
        """執行 Wolfram API 查詢"""
        params = {
            "appid": self.app_id,
            "input": input_text,
            "format": "plaintext,image",
            "output": "json"
        }
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def initialize_session_state():
    """初始化 session state"""
    if 'api' not in st.session_state:
        st.session_state.api = None
    if 'wolfram_api_key' not in st.session_state:
        st.session_state.wolfram_api_key = None

def main():
    st.set_page_config(
        page_title="料理數學小幫手",
        page_icon="🍳",
        layout="wide"
    )

    # 初始化 session state
    initialize_session_state()

    # 側邊欄 API 設置
    if not st.session_state.api:
        with st.sidebar:
            st.header("⚙️ API 設置")
            api_key = st.text_input("輸入 Wolfram API Key:", type="password")
            if api_key:
                st.session_state.wolfram_api_key = api_key
                st.session_state.api = WolframCulinaryAPI(api_key)
                st.success("✅ API Key 設置成功！")
                st.rerun()

    # 主標題
    st.title("🍳 料理數學小幫手")

    # 主要功能標籤頁
    tabs = st.tabs([
        "🥗 營養計算",
        "⚖️ 單位換算",
        "📊 食譜調整",
        "🔍 食材分析"
    ])

    # 營養計算標籤頁
    with tabs[0]:
        st.header("營養計算")
        
        nutrition_type = st.selectbox(
            "選擇計算類型",
            [
                "營養成分分析",
                "每日建議攝取量",
                "飲食需求計算",
                "卡路里計算"
            ]
        )
        
        if nutrition_type == "營養成分分析":
            food_item = st.text_input("輸入食材:", "apple")
            amount = st.number_input("份量 (克):", 1, 1000, 100)
            
            if st.button("計算營養成分", key="calc_nutrition"):
                query = f"nutrition facts {amount}g {food_item}"
                with st.spinner("分析中..."):
                    result = st.session_state.api.query(query)
                    if "queryresult" in result:
                        for pod in result["queryresult"].get("pods", []):
                            with st.expander(pod["title"], expanded=True):
                                for subpod in pod["subpods"]:
                                    if subpod.get("plaintext"):
                                        st.write(subpod["plaintext"])
                                    if "img" in subpod:
                                        st.image(subpod["img"]["src"])

    # 單位換算標籤頁
    with tabs[1]:
        st.header("單位換算")
        
        col1, col2 = st.columns(2)
        with col1:
            from_unit = st.text_input("從:", "1 cup")
        with col2:
            to_unit = st.selectbox(
                "換算至:",
                ["milliliters", "grams", "ounces", "tablespoons", "teaspoons"]
            )
        
        if st.button("換算", key="convert_units"):
            query = f"convert {from_unit} to {to_unit}"
            with st.spinner("換算中..."):
                result = st.session_state.api.query(query)
                if "queryresult" in result:
                    st.success("換算結果：")
                    for pod in result["queryresult"].get("pods", []):
                        if "Result" in pod.get("title", ""):
                            for subpod in pod["subpods"]:
                                st.write(subpod.get("plaintext", ""))

    # 食譜調整標籤頁
    with tabs[2]:
        st.header("食譜調整")
        
        col1, col2 = st.columns(2)
        with col1:
            original_servings = st.number_input("原始份量:", 1, 100, 4)
            target_servings = st.number_input("目標份量:", 1, 100, 6)
        
        with col2:
            ingredient = st.text_area(
                "輸入原始配料 (每行一個):",
                "2 cups flour\n1 cup sugar\n3 eggs"
            )
        
        if st.button("調整配量", key="adjust_recipe"):
            st.success("調整後的配料：")
            
            # 逐行處理配料
            for line in ingredient.split('\n'):
                if line.strip():
                    # 解析數量和單位
                    query = f"scale {line} by {target_servings}/{original_servings}"
                    with st.spinner(f"調整 {line} 中..."):
                        result = st.session_state.api.query(query)
                        if "queryresult" in result:
                            for pod in result["queryresult"].get("pods", []):
                                if "Result" in pod.get("title", ""):
                                    for subpod in pod["subpods"]:
                                        st.write(subpod.get("plaintext", ""))

    # 食材分析標籤頁
    with tabs[3]:
        st.header("食材分析")
        
        food_item = st.text_input("輸入食材:", "tomato")
        
        analysis_options = st.multiselect(
            "選擇分析項目",
            [
                "營養成分",
                "熱量",
                "維生素",
                "礦物質",
                "蛋白質",
                "脂肪",
                "碳水化合物"
            ],
            default=["營養成分", "熱量"]
        )
        
        if st.button("分析", key="analyze_food"):
            query = f"""
            {food_item} detailed analysis:
            - nutritional content
            - vitamins and minerals
            - caloric content
            - protein content
            - health benefits
            """
            
            with st.spinner(f"分析 {food_item} 中..."):
                result = st.session_state.api.query(query)
                if "queryresult" in result:
                    for pod in result["queryresult"].get("pods", []):
                        # 根據選擇的分析項目過濾結果
                        if any(option.lower() in pod.get("title", "").lower() 
                              for option in analysis_options):
                            with st.expander(pod["title"], expanded=True):
                                for subpod in pod["subpods"]:
                                    if subpod.get("plaintext"):
                                        st.write(subpod["plaintext"])
                                    if "img" in subpod:
                                        st.image(subpod["img"]["src"])

if __name__ == "__main__":
    main()