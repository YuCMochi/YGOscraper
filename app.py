import streamlit as st
import json
import os
import sys
import subprocess
import glob
import datetime
import pandas as pd
from file_genarator import FileGenerator

# 設定頁面配置
st.set_page_config(
    page_title="YGO Scraper & Optimizer",
    page_icon="🃏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 初始化 Session State
if 'current_project_path' not in st.session_state:
    st.session_state['current_project_path'] = None
if 'cart_json_content' not in st.session_state:
    st.session_state['cart_json_content'] = ""

def load_cart_json(project_path):
    """讀取專案中的 cart.json"""
    cart_path = os.path.join(project_path, "cart.json")
    if os.path.exists(cart_path):
        with open(cart_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def save_cart_json(project_path, content):
    """儲存 cart.json"""
    cart_path = os.path.join(project_path, "cart.json")
    try:
        # 先驗證是否為有效的 JSON
        json_obj = json.loads(content)
        with open(cart_path, 'w', encoding='utf-8') as f:
            json.dump(json_obj, f, ensure_ascii=False, indent=4)
        return True, "儲存成功"
    except json.JSONDecodeError as e:
        return False, f"JSON 格式錯誤: {e}"
    except Exception as e:
        return False, f"儲存錯誤: {e}"

def get_project_list():
    """取得所有專案列表 (data/ 下的資料夾)"""
    if not os.path.exists("data"):
        return []
    projects = [d for d in os.listdir("data") if os.path.isdir(os.path.join("data", d))]
    # 根據名稱排序 (時間戳記)
    projects.sort(reverse=True)
    return projects

def format_card_id(card_id):
    """格式化卡號: 大寫，自動加入連字號 (如果輸入時沒有)"""
    card_id = card_id.upper().strip()
    # 這裡可以加入更複雜的邏輯，目前簡單轉大寫
    # 如果使用者輸入 QCACJP010 轉成 QCAC-JP010 (這裡假設前四碼是卡包代號)
    # 但卡號規則不一，暫時只做大寫處理，讓使用者自己打連字號比較保險，或者提示使用者
    # 根據 README: "當你輸入空格時，它會自動轉換為連字號 - ... 且全部轉為大寫"
    card_id = card_id.replace(" ", "-")
    return card_id

# --- Sidebar ---
st.sidebar.title("🃏 YGO Scraper")
st.sidebar.markdown("---")

# 專案選擇/建立
st.sidebar.subheader("🗂️ 專案管理")

if st.sidebar.button("➕ 建立新購買專案"):
    fg = FileGenerator()
    new_path = fg.create_project_environment()
    st.session_state['current_project_path'] = new_path
    st.session_state['cart_json_content'] = load_cart_json(new_path)
    st.success(f"已建立新專案: {os.path.basename(new_path)}")
    st.rerun()

project_list = get_project_list()
selected_project = st.sidebar.selectbox(
    "選擇現有專案", 
    options=[""] + project_list,
    index=0 if not st.session_state['current_project_path'] else (project_list.index(os.path.basename(st.session_state['current_project_path'])) + 1 if os.path.basename(st.session_state['current_project_path']) in project_list else 0)
)

if selected_project and selected_project != "":
    path = os.path.abspath(os.path.join("data", selected_project))
    if path != st.session_state['current_project_path']:
        st.session_state['current_project_path'] = path
        st.session_state['cart_json_content'] = load_cart_json(path)
        st.rerun()

current_path = st.session_state['current_project_path']

if current_path:
    st.sidebar.info(f"當前專案:\n{os.path.basename(current_path)}")
else:
    st.sidebar.warning("請先建立或選擇一個專案")

st.sidebar.markdown("---")
page = st.sidebar.radio("功能切換", ["📝 編輯購物車", "🚀 執行計算", "📊 查看結果"])

# --- Main Content ---

if not current_path:
    st.title("👋 歡迎使用 YGO Scraper")
    st.write("請從左側側邊欄建立新專案或是選擇舊有的專案開始。")
    
    # 顯示最近的幾個專案結果預覽 (如果有 plan.json)
    st.subheader("最近的購買方案")
    for proj in project_list[:5]:
        p_path = os.path.join("data", proj, "plan.json")
        if os.path.exists(p_path):
            with open(p_path, 'r', encoding='utf-8') as f:
                try:
                    plan = json.load(f)
                    summary = plan.get('summary', {})
                    st.write(f"**{proj}**: 總金額 ${summary.get('grand_total', 0)} (賣家數: {summary.get('sellers_count', 0)})")
                except:
                    pass

elif page == "📝 編輯購物車":
    st.title("📝 編輯購物清單")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("GUI 編輯")
        
        # 嘗試解析 JSON 以填充 GUI
        try:
            cart_data = json.loads(st.session_state['cart_json_content'])
        except:
            cart_data = {"global_settings": {}, "shopping_cart": []}
            
        # Global Settings
        st.markdown("#### ⚙️ 全域設定")
        gs = cart_data.get("global_settings", {})
        
        default_shipping = st.number_input("預設運費", value=gs.get("default_shipping_cost", 60))
        min_purchase = st.number_input("賣家低消", value=gs.get("min_purchase_limit", 0))
        
        exclude_keywords_str = st.text_input("排除關鍵字 (逗號分隔)", value=",".join(gs.get("global_exclude_keywords", [])))
        exclude_keywords = [k.strip() for k in exclude_keywords_str.split(",") if k.strip()]
        
        exclude_sellers_str = st.text_input("黑名單賣家 (逗號分隔)", value=",".join(gs.get("global_exclude_seller", [])))
        exclude_sellers = [s.strip() for s in exclude_sellers_str.split(",") if s.strip()]
        
        # Shopping Cart
        st.markdown("#### 🛒 商品清單")
        
        cart_items = cart_data.get("shopping_cart", [])
        
        # 新增商品介面
        with st.expander("➕ 新增商品", expanded=True):
            new_name = st.text_input("卡片名稱 (中文)")
            new_amount = st.number_input("所需數量", min_value=1, value=3)
            new_ids_str = st.text_input("卡號 (空格自動轉連字號, 逗號分隔多個)", help="例如: QCAC JP010")
            
            if st.button("加入清單"):
                if new_name and new_ids_str:
                    # 處理卡號格式
                    raw_ids = [x.strip() for x in new_ids_str.split(",")]
                    formatted_ids = [format_card_id(x) for x in raw_ids if x.strip()]
                    
                    new_item = {
                        "card_name_zh": new_name,
                        "required_amount": new_amount,
                        "target_ids": formatted_ids
                    }
                    cart_items.append(new_item)
                    st.success(f"已加入: {new_name}")
                else:
                    st.error("請輸入名稱與卡號")
        
        # 顯示/刪除現有商品
        for i, item in enumerate(cart_items):
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.write(f"**{item.get('card_name_zh')}** x{item.get('required_amount')}")
                    st.caption(f"ID: {', '.join(item.get('target_ids', []))}")
                with c2:
                    if st.button("刪除", key=f"del_{i}"):
                        cart_items.pop(i)
                        st.rerun()

        # 更新 cart_data 物件
        cart_data["global_settings"] = {
            "default_shipping_cost": default_shipping,
            "min_purchase_limit": min_purchase,
            "global_exclude_keywords": exclude_keywords,
            "global_exclude_seller": exclude_sellers
        }
        cart_data["shopping_cart"] = cart_items
        
        # 同步回 JSON 字串
        updated_json_str = json.dumps(cart_data, ensure_ascii=False, indent=4)
        if updated_json_str != st.session_state['cart_json_content']:
             st.session_state['cart_json_content'] = updated_json_str
             save_cart_json(current_path, updated_json_str)

    with col2:
        st.subheader("📄 JSON 原始碼")
        st.caption("可直接在此編輯，左側會同步更新")
        
        json_content = st.text_area(
            "cart.json", 
            value=st.session_state['cart_json_content'],
            height=600
        )
        
        if json_content != st.session_state['cart_json_content']:
            # 驗證 JSON
            try:
                json.loads(json_content) # 嘗試解析
                st.session_state['cart_json_content'] = json_content
                saved, msg = save_cart_json(current_path, json_content)
                if saved:
                    st.toast("已儲存 JSON")
                    st.rerun() # 重整以更新左側
                else:
                    st.error(msg)
            except json.JSONDecodeError:
                st.error("無效的 JSON 格式")

elif page == "🚀 執行計算":
    st.title("🚀 執行自動化流程")
    
    st.info(f"當前專案路徑: {current_path}")
    
    if st.button("開始執行 (爬蟲 -> 清理 -> 計算)", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        log_area = st.empty()
        
        logs = []
        
        def run_command(command, description):
            status_text.text(f"正在執行: {description}...")
            logs.append(f"--- {description} ---")
            log_area.text("\n".join(logs))
            
            try:
                # 使用 subprocess 執行，並即時捕捉輸出 (簡單版，直接等結果)
                result = subprocess.run(
                    command, 
                    cwd=os.getcwd(), # 確保在專案根目錄執行
                    capture_output=True, 
                    text=True,
                    check=True
                )
                logs.append(result.stdout)
                log_area.text("\n".join(logs))
                return True
            except subprocess.CalledProcessError as e:
                logs.append(f"錯誤: {e}")
                logs.append(e.stderr)
                log_area.text("\n".join(logs))
                st.error(f"{description} 失敗！")
                return False

        # 1. Scraper
        progress_bar.progress(10)
        cart_path = os.path.join(current_path, "cart.json")
        csv_path = os.path.join(current_path, "ruten_data.csv")
        
        cmd_scraper = [sys.executable, "scraper.py", "--cart", cart_path, "--output", csv_path]
        if run_command(cmd_scraper, "爬蟲模組 (Scraper)"):
            progress_bar.progress(40)
            
            # 2. Cleaner
            clean_csv_path = os.path.join(current_path, "cleaned_ruten_data.csv")
            cmd_cleaner = [sys.executable, "clean_csv.py", "--input", csv_path, "--output", clean_csv_path, "--cart", cart_path]
            
            if run_command(cmd_cleaner, "資料清理 (Cleaner)"):
                progress_bar.progress(70)
                
                # 3. Calculator
                log_path = os.path.join(current_path, "caculate.log")
                plan_path = os.path.join(current_path, "plan.json")
                cmd_calc = [
                    sys.executable, "caculator.py", 
                    "--cart", cart_path, 
                    "--input_csv", clean_csv_path,
                    "--output_log", log_path,
                    "--output_json", plan_path
                ]
                
                if run_command(cmd_calc, "最佳化計算 (Calculator)"):
                    progress_bar.progress(100)
                    status_text.text("✅ 所有任務執行完成！")
                    st.success("計算完成！請前往「查看結果」頁面。")
                    st.balloons()

elif page == "📊 查看結果":
    st.title("📊 最佳購買方案")
    
    plan_path = os.path.join(current_path, "plan.json")
    
    if not os.path.exists(plan_path):
        st.warning("尚未找到計算結果 (plan.json)。請先執行計算。")
    else:
        try:
            with open(plan_path, 'r', encoding='utf-8') as f:
                plan = json.load(f)
            
            summary = plan.get('summary', {})
            sellers = plan.get('sellers', {})
            
            # 顯示摘要
            c1, c2, c3 = st.columns(3)
            c1.metric("總金額 (含運)", f"${summary.get('grand_total', 0)}")
            c2.metric("商品總額", f"${summary.get('total_items_cost', 0)}")
            c3.metric("總運費", f"${summary.get('total_shipping_cost', 0)}")
            
            st.markdown("---")
            
            st.subheader(f"共需向 {summary.get('sellers_count', 0)} 位賣家購買")
            
            for seller_id, data in sellers.items():
                with st.expander(f"賣家: {seller_id} (小計: ${data.get('items_subtotal', 0)})", expanded=True):
                    items = data.get('items', [])
                    
                    # 轉成 DataFrame 顯示比較漂亮
                    display_data = []
                    for item in items:
                        product_id = item.get('product_id')
                        url = f"https://www.ruten.com.tw/item/show?{product_id}" if product_id else "#"
                        
                        display_data.append({
                            "商品名稱": f"[{item.get('product_name')}]({url})",
                            "搜尋目標": item.get('search_card_name'),
                            "單價": item.get('price'),
                            "購買數量": item.get('buy_qty'),
                            "小計": item.get('price') * item.get('buy_qty')
                        })
                    
                    st.markdown(pd.DataFrame(display_data).to_markdown(index=False))
                    # 注意：st.dataframe 或 st.table 不支援直接 render markdown link，所以上面用 markdown 表格
                    # 或者可以用 column layout 手刻
                    
                    st.write("**商品清單:**")
                    for item in items:
                        product_id = item.get('product_id')
                        url = f"https://www.ruten.com.tw/item/show?{product_id}" if product_id else "#"
                        st.markdown(f"- [{item.get('product_name')}]({url}) | ${item.get('price')} x {item.get('buy_qty')} = ${item.get('price') * item.get('buy_qty')}")

        except json.JSONDecodeError:
            st.error("plan.json 格式錯誤")
        except Exception as e:
            st.error(f"讀取結果時發生錯誤: {e}")
