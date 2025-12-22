import streamlit as st
import json
import os
import sys
import subprocess
import glob
import datetime
import pandas as pd
import uuid
from file_genarator import FileGenerator

PRESET_KEYWORDS = ["卡套", "桌墊", "福袋", "影印", "亞英", "美英", "簡中", "只有書", "損卡"]

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
        
        # Remove _gui_id from shopping_cart items before saving to file
        if "shopping_cart" in json_obj and isinstance(json_obj["shopping_cart"], list):
            for item in json_obj["shopping_cart"]:
                item.pop("_gui_id", None)

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
    card_id = card_id.replace(" ", "-")
    return card_id

# --- Sidebar ---
st.sidebar.title("🃏 YGO Scraper")
st.sidebar.markdown("---")

page = st.sidebar.radio("功能切換", ["🗂️ 專案管理", "📝 編輯購物車", "📊 查看結果"])

if page == "🗂️ 專案管理":
    st.title("🗂️ 專案管理")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("新建專案")
        if st.button("➕ 建立新購買專案", use_container_width=True):
            fg = FileGenerator()
            new_path = fg.create_project_environment()
            st.session_state['current_project_path'] = new_path
            st.session_state['cart_json_content'] = load_cart_json(new_path)
            st.success(f"已建立新專案: {os.path.basename(new_path)}")
            st.rerun()

    with col2:
        st.subheader("載入專案")
        project_list = get_project_list()
        
        current_selection = 0
        if st.session_state['current_project_path']:
             current_name = os.path.basename(st.session_state['current_project_path'])
             if current_name in project_list:
                 current_selection = project_list.index(current_name)
        
        def on_project_select():
            selected_name = st.session_state.project_selector
            if selected_name:
                path = os.path.abspath(os.path.join("data", selected_name))
                st.session_state['current_project_path'] = path
                st.session_state['cart_json_content'] = load_cart_json(path)

        st.selectbox(
            "選擇現有專案", 
            options=project_list,
            index=current_selection,
            key="project_selector",
            on_change=on_project_select
        )
        
        if st.session_state['current_project_path']:
             st.success(f"已載入: {os.path.basename(st.session_state['current_project_path'])}")

    st.markdown("---")
    if st.session_state['current_project_path']:
        st.info(f"🟢 目前運作專案: **{os.path.basename(st.session_state['current_project_path'])}**")
        st.caption(f"路徑: `{st.session_state['current_project_path']}`")
    else:
        st.warning("🔴 目前尚未選擇任何專案")

    # Show recent summaries
    st.subheader("歷史專案概覽")
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
    
    current_path = st.session_state['current_project_path']
    if not current_path:
        st.warning("請先至「專案管理」建立或選擇一個專案。")
        st.stop()

    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("設定與選購")
        
        try:
            cart_data = json.loads(st.session_state['cart_json_content'])
        except:
            cart_data = {"global_settings": {}, "shopping_cart": []}
            
        # --- Global Settings ---
        with st.container(border=True):
            st.markdown("#### ⚙️ 全域設定")
            gs = cart_data.get("global_settings", {})
            
            # 1. Shipping & Min Purchase
            c1, c2 = st.columns(2)
            with c1:
                default_shipping = st.number_input("預設運費", value=gs.get("default_shipping_cost", 60), step=10)
            with c2:
                min_purchase = st.number_input("賣家低消", value=gs.get("min_purchase_limit", 0), step=50)

            # 2. Exclude Keywords
            current_keywords = gs.get("global_exclude_keywords", [])
            all_options = sorted(list(set(PRESET_KEYWORDS + current_keywords)))
            
            exclude_keywords = st.multiselect(
                "排除關鍵字 (可自行輸入新增)",
                options=all_options,
                default=current_keywords,
                help="選擇或輸入想要排除的商品關鍵字"
            )
            
            # 3. Seller Blacklist
            st.markdown("**賣家黑名單**")
            current_sellers = gs.get("global_exclude_seller", [])
            
            def add_seller():
                val = st.session_state.new_seller_input.strip()
                if val and val not in current_sellers:
                    current_sellers.append(val)
                    st.session_state.new_seller_input = "" 
            
            st.text_input(
                "新增黑名單賣家 ID", 
                key="new_seller_input", 
                placeholder="輸入 ID 後按 Enter 新增", 
                on_change=add_seller
            )
            
            if current_sellers:
                st.caption("已排除賣家 (點擊 x 移除):")
                updated_sellers = st.multiselect(
                    "已排除賣家清單",
                    options=current_sellers,
                    default=current_sellers,
                    label_visibility="collapsed"
                )
                exclude_sellers = updated_sellers
            else:
                exclude_sellers = []

        # --- Shopping Cart ---
        st.markdown("#### 🛒 購物車")
        cart_items = cart_data.get("shopping_cart", [])

        # Assign unique IDs for UI tracking if missing
        for item in cart_items:
            if "_gui_id" not in item:
                item["_gui_id"] = str(uuid.uuid4())

        if st.button("➕ 新增卡片", type="primary", use_container_width=True):
            cart_items.append({
                "card_name_zh": "",
                "required_amount": 3,
                "target_ids": [],
                "_gui_id": str(uuid.uuid4())
            })
            # Update data (keep _gui_id for internal consistency)
            cart_data["shopping_cart"] = cart_items
            st.session_state['cart_json_content'] = json.dumps(cart_data, ensure_ascii=False, indent=4)
            st.rerun()

        items_to_remove_ids = []
        
        for i, item in enumerate(cart_items):
            item_id = item["_gui_id"]
            with st.container(border=True):
                h1, h2 = st.columns([5, 1])
                with h1:
                     st.caption(f"Card #{i+1}")
                with h2:
                    if st.button("🗑️", key=f"del_btn_{item_id}", help="刪除此卡片"):
                        items_to_remove_ids.append(item_id)

                c_name = st.text_input("卡片名稱 (中文)", value=item.get("card_name_zh", ""), key=f"name_{item_id}")
                c_amount = st.number_input("數量", min_value=1, value=item.get("required_amount", 3), key=f"amt_{item_id}")
                
                current_ids_list = item.get("target_ids", [])
                current_ids_str = ", ".join(current_ids_list)
                
                new_ids_str = st.text_area(
                    "卡片編號 (空格自動轉連字號, 逗號分隔)", 
                    value=current_ids_str,
                    key=f"ids_{item_id}",
                    height=68,
                    help="例如: QCAC-JP010, TTP1-JPB08"
                )
                
                raw_ids = [x.strip() for x in new_ids_str.split(",")]
                processed_ids = []
                for rid in raw_ids:
                    if rid:
                        fmt = rid.upper().replace(" ", "-")
                        processed_ids.append(fmt)
                
                # Update item reference (in-place)
                item["card_name_zh"] = c_name
                item["required_amount"] = c_amount
                item["target_ids"] = processed_ids

        if items_to_remove_ids:
            # Filter out deleted items by ID
            cart_items = [item for item in cart_items if item["_gui_id"] not in items_to_remove_ids]
            
            # Update data (keep _gui_id)
            cart_data["shopping_cart"] = cart_items
            cart_data["global_settings"] = {
                "default_shipping_cost": default_shipping,
                "min_purchase_limit": min_purchase,
                "global_exclude_keywords": exclude_keywords,
                "global_exclude_seller": exclude_sellers
            }
            st.session_state['cart_json_content'] = json.dumps(cart_data, ensure_ascii=False, indent=4)
            st.rerun()

        # Prepare Clean Data Object for JSON Preview (Remove _gui_id)
        # We keep _gui_id in the session state JSON to maintain stable keys for UI components.
        # It is only stripped when saving to file or downloading.
        
        cart_data["global_settings"] = {
            "default_shipping_cost": default_shipping,
            "min_purchase_limit": min_purchase,
            "global_exclude_keywords": exclude_keywords,
            "global_exclude_seller": exclude_sellers
        }
        cart_data["shopping_cart"] = cart_items
        
        # Sync to Session State JSON string only (UI responsiveness)
        updated_json_str = json.dumps(cart_data, ensure_ascii=False, indent=4)
        if updated_json_str != st.session_state['cart_json_content']:
             st.session_state['cart_json_content'] = updated_json_str
             # No file save here!

        # --- Execution Section ---
        st.markdown("---")
        st.subheader("🚀 執行計算")
        
        if st.button("💾 儲存設定並開始計算", type="primary", use_container_width=True):
            # 1. Save to file NOW
            save_cart_json(current_path, st.session_state['cart_json_content'])
            st.toast("設定已儲存，開始執行...")
            
            # 2. Execute Workflow
            progress_bar = st.progress(0)
            status_text = st.empty()
            log_expander = st.expander("查看執行日誌", expanded=True)
            log_area = log_expander.empty()
            logs = []

            def run_command(command, description):
                status_text.text(f"正在執行: {description}...")
                logs.append(f"--- {description} ---")
                log_area.text("\n".join(logs))
                try:
                    result = subprocess.run(
                        command, 
                        cwd=os.getcwd(), 
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

            # Workflow Steps
            progress_bar.progress(10)
            cart_path = os.path.join(current_path, "cart.json")
            csv_path = os.path.join(current_path, "ruten_data.csv")
            
            if run_command([sys.executable, "scraper.py", "--cart", cart_path, "--output", csv_path], "爬蟲模組"):
                progress_bar.progress(40)
                clean_csv_path = os.path.join(current_path, "cleaned_ruten_data.csv")
                
                if run_command([sys.executable, "clean_csv.py", "--input", csv_path, "--output", clean_csv_path, "--cart", cart_path], "資料清理"):
                    progress_bar.progress(70)
                    log_path = os.path.join(current_path, "caculate.log")
                    plan_path = os.path.join(current_path, "plan.json")
                    
                    if run_command([sys.executable, "caculator.py", "--cart", cart_path, "--input_csv", clean_csv_path, "--output_log", log_path, "--output_json", plan_path], "最佳化計算"):
                        progress_bar.progress(100)
                        status_text.text("✅ 計算完成！")
                        st.balloons()
                        st.success("請前往「📊 查看結果」頁籤查看報告")

    with col2:
        st.subheader("JSON 預覽")
        st.caption("左側編輯將即時同步至此 (尚未存檔)")
        
        # Create a clean copy for download (remove _gui_id)
        download_content = st.session_state['cart_json_content']
        try:
            download_json = json.loads(download_content)
            if "shopping_cart" in download_json and isinstance(download_json["shopping_cart"], list):
                for item in download_json["shopping_cart"]:
                    item.pop("_gui_id", None)
            download_content = json.dumps(download_json, ensure_ascii=False, indent=4)
        except:
            pass # Use original content if parse fails

        st.download_button(
             label="📥 下載 JSON",
             data=download_content,
             file_name="cart.json",
             mime="application/json",
             use_container_width=True
        )
        
        json_content = st.text_area(
            "JSON Editor", 
            value=st.session_state['cart_json_content'],
            height=800,
            label_visibility="collapsed"
        )
        
        # If user edits JSON manually, we update session state but NOT file
        if json_content != st.session_state['cart_json_content']:
            try:
                json.loads(json_content) # Validate
                st.session_state['cart_json_content'] = json_content
                st.toast("JSON 已更新 (未存檔)")
                st.rerun()
            except json.JSONDecodeError:
                st.error("無效的 JSON 格式")

elif page == "📊 查看結果":
    st.title("📊 最佳購買方案")
    
    current_path = st.session_state['current_project_path']
    if not current_path:
        st.warning("請先至「專案管理」建立或選擇一個專案。")
        st.stop()
        
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

        except json.JSONDecodeError:
            st.error("plan.json 格式錯誤")
        except Exception as e:
            st.error(f"讀取結果時發生錯誤: {e}")