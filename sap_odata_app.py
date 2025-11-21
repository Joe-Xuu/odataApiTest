import streamlit as st
import requests
import pandas as pd

# 设置页面配置
st.set_page_config(page_title="SAP OData Tester", layout="wide")

st.title("🛒 SAP S/4HANA Product OData 测试器")
st.markdown("这是一个用于测试 SAP API Business Hub Sandbox 的简单前端。")

# --- 侧边栏：配置区域 ---
with st.sidebar:
    st.header("配置")
    # SAP Sandbox 的 API Key 输入框
    api_key = st.text_input("输入你的 API Key", type="password", help="从 api.sap.com 获取")
    
    # 基础 URL (SAP Sandbox)
    base_url = "https://sandbox.api.sap.com/s4hanacloud/sap/opu/odata/sap/API_PRODUCT_SRV"
    
    # 选择实体集 (Entity Set)
    # A_Product 是物料主数据的核心实体
    entity = st.selectbox("选择实体 (Entity Set)", ["A_Product", "A_ProductDescription", "A_ProductPlant"])
    
    # OData 查询参数
    st.subheader("OData 过滤器")
    top_n = st.number_input("$top (返回前N条)", min_value=1, max_value=100, value=5)
    search_query = st.text_input("搜索产品 (Product ID)", "")

# --- 主逻辑 ---

if st.button("🚀 发送请求"):
    if not api_key:
        st.error("请先在左侧输入 API Key！")
    else:
        # 1. 拼接 OData URL
        # 这里的逻辑是 OData 的核心：通过 URL 参数控制数据
        request_url = f"{base_url}/{entity}?$top={top_n}&$format=json"
        
        # 如果有搜索内容，添加简单的过滤器
        if search_query:
            request_url += f"&$filter=Product eq '{search_query}'"

        st.info(f"正在请求: `{request_url}`")

        # 2. 发送 HTTP 请求
        # SAP Sandbox 要求在 Header 中必须带上 APIKey
        headers = {
            "APIKey": api_key,
            "Accept": "application/json"
        }

        try:
            response = requests.get(request_url, headers=headers)
            
            # 3. 处理响应
            if response.status_code == 200:
                data = response.json()
                
                # OData 的结果通常包裹在 d -> results 中
                results = data.get('d', {}).get('results', [])
                
                if results:
                    st.success(f"成功获取 {len(results)} 条数据！")
                    
                    # 将 JSON 转换为 DataFrame 表格展示
                    df = pd.DataFrame(results)
                    st.dataframe(df, use_container_width=True)
                    
                    # 展示原始 JSON (用于调试)
                    with st.expander("查看原始 JSON 数据"):
                        st.json(results)
                else:
                    st.warning("请求成功，但没有返回任何数据（可能被过滤掉了）。")
            else:
                st.error(f"请求失败: {response.status_code}")
                st.code(response.text)
                
        except Exception as e:
            st.error(f"发生错误: {e}")

# --- OData 小课堂 ---
st.divider()
st.markdown("""
### 💡 OData 常用技巧
* **$top=N**: 只取前 N 条数据。
* **$filter**: 类似于 SQL 的 WHERE。例如 `ProductType eq 'ZFRT'`。
* **$select**: 类似于 SQL 的 SELECT。例如 `$select=Product,ProductType` (只返回这两个字段，减少传输量)。
* **$expand**: 类似于 SQL 的 JOIN。可以在查询 Product 的同时把关联的 Plant 信息也查出来。
""")