# import streamlit as st
# from streamlit_image_coordinates import streamlit_image_coordinates
# from PIL import Image, ImageDraw
# import pandas as pd
# from supabase import create_client, Client
# import os

# # --- 1. CONFIG & MARIO THEME ---
# st.set_page_config(layout="wide", page_title="โลก 5ส ของมาริโอ้", page_icon="🍄")

# try:
#     url: str = st.secrets["SUPABASE_URL"]
#     key: str = st.secrets["SUPABASE_KEY"]
#     supabase: Client = create_client(url, key)
# except:
#     st.error("❌ เชื่อมต่อฐานข้อมูลไม่ได้!"); st.stop()

# MASTER_TOOLS = ["ไม้กวาด", "น้ำยา", "ผ้าคลุมกันฝุ่น", "ถุงขยะ", "ถังน้ำ", "แปรงขัดพื้น", "เครื่องดูดฝุ่น", "ไม้ถูพื้น", "ถุงมือ", "หน้ากากกันฝุ่น"]

# st.markdown("""
# <style>
#     @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Kanit:wght@400;700;800&display=swap');
    
#     .stApp { background-color: #5C94FC; font-family: 'Kanit', sans-serif; }
    
#     h1 { 
#         font-family: 'Press Start 2P', cursive; 
#         color: #FFFFFF !important; 
#         text-shadow: 4px 4px 0px #E4000F; 
#         text-align: center; 
#         font-size: 38px !important;
#         margin-bottom: 5px !important;
#     }

#     .stTabs [data-baseweb="tab-list"] { 
#         background-color: #008800; 
#         border: 4px solid #000; 
#         padding: 8px;
#     }
#     .stTabs [data-baseweb="tab"] { 
#         color: white !important; 
#         font-size: 24px !important; 
#         font-weight: 800 !important;
#         padding: 10px 20px !important;
#     }
#     .stTabs [aria-selected="true"] { 
#         background-color: #E4000F !important; 
#     }

#     .how-to-play {
#         background-color: #F8B800;
#         border: 3px solid #000;
#         padding: 15px;
#         border-radius: 10px;
#         margin-top: 10px;
#         font-size: 16px;
#         color: #000;
#         line-height: 1.6;
#         box-shadow: 4px 4px 0px #000;
#     }

#     .stButton > button { 
#         background-color: #F8B800 !important; 
#         border: 3px solid #000 !important; 
#         font-weight: 800 !important; 
#         font-size: 20px !important;
#         box-shadow: 3px 3px 0px #8C5200;
#         margin-bottom: 10px;
#     }
            
#     @media (max-width: 991px) {
#         [data-testid="stHorizontalBlock"] {
#             flex-direction: column !important;
#         }
#     }
# </style>
# """, unsafe_allow_html=True)

# # --- 2. ฟังก์ชันหลัก ---
# def get_all_plans():
#     res = supabase.table("cleaning_plans").select("*").order("created_at", desc=True).execute()
#     return res.data

# def is_inside(x, y, poly):
#     n, inside = len(poly), False
#     if n == 0: return False
#     p1x, p1y = poly[0]
#     for i in range(n + 1):
#         p2x, p2y = poly[i % n]
#         if y > min(p1y, p2y) and y <= max(p1y, p2y) and x <= max(p1x, p2x):
#             if p1y != p2y: xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
#             if p1x == p2x or x <= xinters: inside = not inside
#         p1x, p1y = p2x, p2y
#     return inside

# def is_convex(points):
#     # ฟังก์ชันเช็คว่ารูป 4 จุดนี้ "กางออก" เป็นสี่เหลี่ยม ไม่ใช่รูปนาฬิกาทราย
#     def cross_product(o, a, b):
#         return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    
#     cp = []
#     n = len(points)
#     for i in range(n):
#         cp.append(cross_product(points[i], points[(i+1)%n], points[(i+2)%n]))
    
#     # ถ้าค่า Cross Product มีเครื่องหมายเดียวกันหมด (+ หรือ - ทั้งหมด) แสดงว่าเป็นสี่เหลี่ยมที่นูนสวย
#     return all(x > 0 for x in cp) or all(x < 0 for x in cp)

# # --- 3. DIALOGS ---

# @st.dialog("🚩 สร้างด่านใหม่")
# def create_zone_dialog(points, w, h):
#     st.markdown("### 🍄 สร้างโซนใหม่")
    
#     # --- ส่วนเลือกแผนก (อยู่นอก Form เพื่อให้เลือกแล้วช่องพิมพ์โผล่ทันที) ---
#     dept_options = ["WH", "SH", "TP", "LM", "BD", "EOE", "ENG", "PC", "➕ อื่นๆ (ระบุเอง)..."]
#     d_select = st.selectbox("เลือกแผนก", dept_options)
    
#     custom_dept = ""
#     if d_select == "➕ อื่นๆ (ระบุเอง)...":
#         custom_dept = st.text_input("📝 ระบุชื่อแผนกใหม่")
    
#     # --- ส่วนที่เหลือใช้ Form ตามปกติ ---
#     with st.form("nz"):
#         z = st.text_input("ชื่อด่าน (Zone Name)")
#         staff = st.text_input("ฮีโร่ผู้รับผิดชอบ (Owner)")
        
#         if st.form_submit_button("🔨 เริ่มสร้างด่าน (START)"):
#             # เลือกใช้ชื่อแผนกจากช่องที่พิมพ์ หรือจาก Selectbox
#             final_dept = custom_dept if d_select == "➕ อื่นๆ (ระบุเอง)..." else d_select
            
#             if not z or not final_dept:
#                 st.error("⚠️ โปรดระบุชื่อด่านและแผนกให้ครบถ้วน!")
#             else:
#                 p_pct = [{"x": f"{(p[0]/w)*100}%", "y": f"{(p[1]/h)*100}%"} for p in points]
#                 supabase.table("cleaning_plans").insert({
#                     "zone_name": z, 
#                     "dept": final_dept, 
#                     "responsible_staff": staff,
#                     "coords": {"points": p_pct}, 
#                     "tools": []
#                 }).execute()
                
#                 st.session_state.points = []
#                 st.rerun()

# @st.dialog("⭐️ LEVEL SETTINGS")
# def edit_mission_dialog(item_id):
#     res = supabase.table("cleaning_plans").select("*").eq("id", item_id).execute()
#     if not res.data: return
#     item = res.data[0]
#     t1, t2, t3 = st.tabs(["📊 ข้อมูล", "🎒 อุปกรณ์", "🧨 ลบ"])
#     with t1:
#         with st.form("f1"):
#             u_name = st.text_input("ชื่อด่าน", value=item['zone_name'])
#             u_staff = st.text_input("ฮีโร่", value=item.get('responsible_staff', ''))
#             if st.form_submit_button("อัปเดต"):
#                 supabase.table("cleaning_plans").update({"zone_name": u_name, "responsible_staff": u_staff}).eq("id", item_id).execute()
#                 st.rerun()
#     with t2:
#         st.write("### 🎒 จัดการไอเทม")
#         c1, c2, c3 = st.columns([2, 1, 1])
#         sel = c1.selectbox("เลือก", MASTER_TOOLS + ["➕ พิมพ์เอง..."], key=f"s_{item_id}")
#         final_tool = sel
#         if sel == "➕ พิมพ์เอง...":
#             final_tool = st.text_input("ชื่ออุปกรณ์", key=f"c_{item_id}")
#         qty = c2.number_input("จำนวน", min_value=1, value=1, key=f"q_{item_id}")
#         if c3.button("➕ เก็บ", key=f"a_{item_id}"):
#             current = item.get('tools', [])
#             current.append({"item": final_tool, "amount": int(qty)})
#             supabase.table("cleaning_plans").update({"tools": current}).eq("id", item_id).execute()
#             st.rerun()
#         st.divider()
#         for i, t in enumerate(item.get('tools', [])):
#             col_t, col_b = st.columns([4, 1])
#             col_t.markdown(f"💰 **{t['item']}** x{t['amount']}")
#             if col_b.button("🗑️", key=f"d_{item_id}_{i}"):
#                 item['tools'].pop(i)
#                 supabase.table("cleaning_plans").update({"tools": item['tools']}).eq("id", item_id).execute()
#                 st.rerun()
#     with t3:
#         if st.button("🧨 ยืนยันทำลายด่าน"):
#             supabase.table("cleaning_plans").delete().eq("id", item_id).execute()
#             st.rerun()

# # --- 4. MAIN LAYOUT ---
# st.markdown("<h1>SUPER 5S WORLD</h1>", unsafe_allow_html=True)
# tab_map, tab_score = st.tabs(["🎮 แผนที่ตะลุยด่าน", "🏆 ตารางคะแนนและสรุปผล"])

# all_plans = get_all_plans()

# with tab_map:
#     # สลับเอา col_info ขึ้นก่อนในโค้ด (เพื่อให้ Mobile เห็นก่อน)
#     # แต่บน Desktop มันจะอยู่ซ้าย-ขวา ตามสัดส่วน [1.5, 5]
#     col_info, col_display = st.columns([1.5, 5])
    
#     with col_info:
#         # --- 1. ปุ่มและรูปมาริโอ้ (จะอยู่ด้านบนในมือถือ) ---
#         st.button("🔄 ล้างจุดวาด", on_click=lambda: st.session_state.update({"points": []}), use_container_width=True)
        
#         if os.path.exists("mario.png"):
#             st.image("mario.png", use_container_width=True)
            
#         st.markdown("""
#         <div class="how-to-play">
#             <b>🎮 วิธีเล่น (How to Play)</b><br>
#             1. <b>กำหนดพื้นที่:</b> คลิกบนแผนที่ <b>4 จุด</b> เพื่อวาดกรอบพื้นที่<br>
#             2. <b>แก้ไขข้อมูล/จัดการอุปกรณ์:</b> คลิกที่ <b>กรอบสีแดง</b> <br>
#             3. <b>รีเซ็ต:</b> กด <b>'ล้างจุดวาด'</b> หากต้องการเริ่มใหม่ <br>
#             * <b>'พื้นที่ตั้งชื่อเป็นภาษาอังกฤษเท่านั้น'</b> <br>
#             * <b>'กำหนดพื้นที่ห้ามทับซ้อนกัน'</b> <br>
#             * <b>'กำหนดพื้นที่ต้องเป็นสี่เหลี่ยม'</b>
#         </div>
#         """, unsafe_allow_html=True)

#     with col_display:
#         # --- 2. แผนที่ (จะอยู่ถัดลงมาในมือถือ) ---
#         try:
#             img = Image.open("map.png")
#             w, h = img.size
#             draw = ImageDraw.Draw(img)
            
#             # วาดเส้นและชื่อด่าน (ใช้แบบตัดขอบดำตามที่แก้ไปก่อนหน้า)
#             for p in all_plans:
#                 c = p.get('coords', {}).get('points', [])
#                 if c:
#                     poly = [(float(pt['x'].replace('%',''))*w/100, float(pt['y'].replace('%',''))*h/100) for pt in c]
#                     draw.polygon(poly, outline="#E4000F", width=10)
#                     draw.text(
#                         (poly[0][0], poly[0][1] - 35), 
#                         f" {p['zone_name']}", 
#                         fill="#F8B800", 
#                         font_size=28, 
#                         stroke_width=3, 
#                         stroke_fill="black"
#                     )
            
#             # วาดจุดเหลืองที่กำลังเลือก
#             if "points" not in st.session_state: st.session_state.points = []
#             for p in st.session_state.points:
#                 draw.ellipse((p[0]-15, p[1]-15, p[0]+15, p[1]+15), fill="#F8B800", outline="white")
            
#             # แสดงแผนที่
#             click = streamlit_image_coordinates(img, key="m_map", width=None)
#         except:
#             st.error("ไม่พบไฟล์ map.png")


# # --- 5. LOGIC (จุดที่ต้องแก้) ---
# if click:
#     cx, cy = click["x"], click["y"]
#     if "last_c" not in st.session_state or st.session_state.last_c != (cx, cy):
#         st.session_state.last_c = (cx, cy)
        
#         # เช็คว่าคลิกโดนด่านที่มีอยู่แล้วหรือไม่
#         target = None
#         for p in all_plans:
#             c = p.get('coords', {}).get('points', [])
#             if c:
#                 poly = [(float(pt['x'].replace('%',''))*w/100, float(pt['y'].replace('%',''))*h/100) for pt in c]
#                 if is_inside(cx, cy, poly): target = p; break
        
#         if target: 
#             edit_mission_dialog(target['id'])
#         else:
#             # เพิ่มจุดใหม่เข้าไปในลิสต์
#             st.session_state.points.append((cx, cy))
            
#             # เมื่อครบ 4 จุด ให้ตรวจสอบเบื้องต้น
#             if len(st.session_state.points) == 4:
#                 # 1. เช็คความนูนของรูปทรง (ห้ามเส้นตัดกัน)
#                 if not is_convex(st.session_state.points):
#                     # ใช้ toast เพื่อให้เด้งเตือนทันทีแม้จะ rerun
#                     st.toast("⚠️ เส้นห้ามตัดกัน! วาดใหม่นะมาริโอ้", icon="🧨")
#                     # หน่วงเวลาเล็กน้อย หรือใช้ st.error โดยไม่มี rerun เพื่อให้คนเห็นข้อความ
#                     st.error("⚠️ รูปทรงไม่ถูกต้อง: โปรดวาดเรียงลำดับจุด (เช่น วนตามเข็มนาฬิกา)")
#                     st.session_state.points = [] 
#                     # ไม่ต้องใส่ st.rerun() ตรงนี้ เพื่อให้ Error Message ค้างให้คนอ่าน
#                 else:
#                     # 2. [เพิ่มใหม่] เช็คว่ามีจุดใดจุดหนึ่งไปอยู่ในโซนอื่นที่มีอยู่แล้วไหม
#                     is_overlapping = False
#                     for p_existing in all_plans:
#                         c = p_existing.get('coords', {}).get('points', [])
#                         if c:
#                             # สร้างพื้นที่ของด่านที่มีอยู่แล้ว
#                             poly_existing = [(float(pt['x'].replace('%',''))*w/100, float(pt['y'].replace('%',''))*h/100) for pt in c]
                            
#                             # เช็คจุดใหม่ทั้ง 4 จุด ว่ามีจุดไหนหลุดเข้าไปในด่านเก่าไหม
#                             for new_pt in st.session_state.points:
#                                 if is_inside(new_pt[0], new_pt[1], poly_existing):
#                                     is_overlapping = True
#                                     break
                    
#                     if is_overlapping:
#                         st.error("⚠️ พื้นที่นี้มีเจ้าของแล้ว! ห้ามวาดทับซ้อนกัน")
#                         st.session_state.points = []
#                     else:
#                         # ถ้าผ่านทุกด่าน... สร้างด่านได้!
#                         create_zone_dialog(st.session_state.points, w, h)
#             else: 
#                 st.rerun()


# with tab_score:
#     if all_plans:
#         df = pd.DataFrame([{"ด่าน": p['zone_name'], "ฮีโร่": p.get('responsible_staff'), "อุปกรณ์": ", ".join([f"{x['item']}(x{x['amount']})" for x in p.get('tools', [])])} for p in all_plans])
#         st.dataframe(df, use_container_width=True)


# import streamlit as st
# from streamlit_image_coordinates import streamlit_image_coordinates
# from PIL import Image, ImageDraw
# import pandas as pd
# from supabase import create_client, Client
# import os

# # --- 1. CONFIG & MARIO THEME ---
# st.set_page_config(layout="wide", page_title="โลก 5ส ของมาริโอ้", page_icon="🍄")

# try:
#     url: str = st.secrets["SUPABASE_URL"]
#     key: str = st.secrets["SUPABASE_KEY"]
#     supabase: Client = create_client(url, key)
# except:
#     st.error("❌ เชื่อมต่อฐานข้อมูลไม่ได้! กรุณาเช็ค Secrets"); st.stop()

# # --- 🆕 ตรวจสอบข้อความฝากแจ้งเตือน (Post-Rerun Toast) ---
# if "success_msg" in st.session_state:
#     st.toast(st.session_state.success_msg)
#     del st.session_state.success_msg

# MASTER_TOOLS = ["ไม้กวาด", "น้ำยา", "ผ้าคลุมกันฝุ่น", "ถุงขยะ", "ถังน้ำ", "แปรงขัดพื้น", "เครื่องดูดฝุ่น", "ไม้ถูพื้น", "ถุงมือ", "หน้ากากกันฝุ่น"]

# PRESET_ACTIVITIES = [
#     "สะสาง: แยกของไม่จำเป็นออก",
#     "สะดวก: ตีเส้นแบ่งเขต/ติดป้ายชื่อ",
#     "สะอาด: ปัดหยากไย่และเช็ดพื้น",
#     "สุขลักษณะ: ถ่ายรูป Before & After",
#     "สร้างนิสัย: บันทึกมาตรฐานใหม่"
# ]

# st.markdown("""
# <style>
#     @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Kanit:wght@400;700;800&display=swap');
#     .stApp { background-color: #5C94FC; font-family: 'Kanit', sans-serif; }
#     h1 { font-family: 'Press Start 2P', cursive; color: #FFFFFF !important; text-shadow: 4px 4px 0px #E4000F; text-align: center; font-size: 38px !important; margin-bottom: 5px !important; }
#     .stTabs [data-baseweb="tab-list"] { background-color: #008800; border: 4px solid #000; padding: 8px; }
#     .stTabs [data-baseweb="tab"] { color: white !important; font-size: 20px !important; font-weight: 800 !important; padding: 10px 20px !important; }
#     .stTabs [aria-selected="true"] { background-color: #E4000F !important; }
#     .how-to-play { background-color: #F8B800; border: 3px solid #000; padding: 15px; border-radius: 10px; margin-top: 10px; font-size: 16px; color: #000; line-height: 1.6; box-shadow: 4px 4px 0px #000; }
#     .stButton > button { background-color: #F8B800 !important; border: 3px solid #000 !important; font-weight: 800 !important; font-size: 20px !important; box-shadow: 3px 3px 0px #8C5200; margin-bottom: 10px; }
    
#     /* Responsive for Mobile */
#     @media (max-width: 600px) {
#         h1 { font-size: 20px !important; }
#         .stTabs [data-baseweb="tab"] { font-size: 14px !important; padding: 5px !important; }
#     }
# </style>
# """, unsafe_allow_html=True)

# # --- 2. ฟังก์ชันหลัก ---
# def get_all_plans():
#     res = supabase.table("cleaning_plans").select("*").order("created_at", desc=True).execute()
#     return res.data

# def is_inside(x, y, poly):
#     n, inside = len(poly), False
#     if n == 0: return False
#     p1x, p1y = poly[0]
#     for i in range(n + 1):
#         p2x, p2y = poly[i % n]
#         if y > min(p1y, p2y) and y <= max(p1y, p2y) and x <= max(p1x, p2x):
#             if p1y != p2y: xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
#             if p1x == p2x or x <= xinters: inside = not inside
#         p1x, p1y = p2x, p2y
#     return inside

# def is_convex(points):
#     def cross_product(o, a, b):
#         return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
#     cp = []
#     n = len(points)
#     for i in range(n):
#         cp.append(cross_product(points[i], points[(i+1)%n], points[(i+2)%n]))
#     return all(x > 0 for x in cp) or all(x < 0 for x in cp)

# # --- 3. DIALOGS ---

# @st.dialog("🚩 สร้างด่านใหม่")
# def create_zone_dialog(points, w, h):
#     st.markdown("### 🍄 สร้างโซนใหม่")
#     dept_options = ["WH", "SH", "TP", "LM", "BD", "EOE", "ENG", "PC", "➕ อื่นๆ..."]
#     d_select = st.selectbox("เลือกแผนก", dept_options)
#     custom_dept = st.text_input("📝 ระบุชื่อแผนกใหม่") if d_select == "➕ อื่นๆ..." else ""
    
#     with st.form("nz"):
#         z = st.text_input("ชื่อด่าน (English Only)")
#         staff = st.text_input("ฮีโร่ผู้รับผิดชอบ")
#         if st.form_submit_button("🔨 เริ่มสร้างด่าน"):
#             final_dept = custom_dept if d_select == "➕ อื่นๆ..." else d_select
#             if z and final_dept:
#                 p_pct = [{"x": f"{(p[0]/w)*100}%", "y": f"{(p[1]/h)*100}%"} for p in points]
#                 supabase.table("cleaning_plans").insert({
#                     "zone_name": z, "dept": final_dept, "responsible_staff": staff,
#                     "coords": {"points": p_pct}, "tools": [], "activities": []
#                 }).execute()
#                 st.session_state.points = []
#                 st.session_state.success_msg = f"🏰 สร้างด่าน {z} สำเร็จ!"
#                 st.rerun()

# @st.dialog("⭐️ LEVEL SETTINGS", width="large")
# def edit_mission_dialog(item_id):
#     res = supabase.table("cleaning_plans").select("*").eq("id", item_id).execute()
#     if not res.data: 
#         st.error("ไม่พบข้อมูลด่านนี้")
#         return
#     item = res.data[0]

#     t1, t2, t3, t4 = st.tabs(["📊 ข้อมูลหลัก", "🧹 กิจกรรม (Mission)", "🎒 อุปกรณ์ (Items)", "🧨 ลบด่าน"])
    
#     with t1:
#         with st.form("edit_base_info"):
#             u_name = st.text_input("ชื่อด่าน", value=item['zone_name'])
#             u_staff = st.text_input("ฮีโร่ผู้รับผิดชอบหลัก", value=item.get('responsible_staff', ''))
#             if st.form_submit_button("💾 บันทึกการเปลี่ยนแปลง"):
#                 supabase.table("cleaning_plans").update({"zone_name": u_name, "responsible_staff": u_staff}).eq("id", item_id).execute()
#                 st.session_state.success_msg = "✅ อัปเดตข้อมูลสำเร็จ!"
#                 st.rerun()
    
#     with t2:
#         st.markdown("### 🧹 ภารกิจ Big Cleaning Day")
#         with st.container(border=True):
#             act_sel = st.selectbox("เลือกกิจกรรมแนะนำ", ["➕ พิมพ์เพิ่มเอง..."] + PRESET_ACTIVITIES, key=f"sel_act_{item_id}")
#             custom_act = st.text_input("📝 ระบุกิจกรรม", key=f"ca_input_{item_id}")
#             col_p, col_t = st.columns(2)
#             num_people = col_p.number_input("👥 จำนวนคน", min_value=1, step=1, value=1, key=f"p_input_{item_id}")
#             hrs = col_t.number_input("⏱️ เวลา (ชม.)", min_value=1, step=1, value=1, key=f"h_input_{item_id}")
            
#             if st.button("➕ เพิ่มกิจกรรมเข้าแผน", use_container_width=True, key=f"btn_add_act_{item_id}"):
#                 final_act = custom_act if act_sel == "➕ พิมพ์เพิ่มเอง..." else act_sel
#                 if final_act:
#                     current_acts = item.get('activities', [])
#                     current_acts.append({"name": final_act, "people": int(num_people), "hours": int(hrs)})
#                     supabase.table("cleaning_plans").update({"activities": current_acts}).eq("id", item_id).execute()
#                     st.session_state.success_msg = f"🧹 เพิ่มภารกิจ {final_act} เรียบร้อย!"
#                     st.rerun()

#         st.divider()
#         for i, a in enumerate(item.get('activities', [])):
#             c1, c2, c3, c4 = st.columns([3, 1.5, 1.5, 0.5])
#             c1.write(f"🔹 **{a['name']}**")
#             c2.write(f"👥 {a.get('people', 1)} คน")
#             c3.write(f"⏱️ {a.get('hours', 0)} ชม.")
#             if c4.button("🗑️", key=f"del_act_{item_id}_{i}"):
#                 new_acts = item.get('activities', [])
#                 new_acts.pop(i)
#                 supabase.table("cleaning_plans").update({"activities": new_acts}).eq("id", item_id).execute()
#                 st.session_state.success_msg = "🗑️ ลบกิจกรรมออกแล้ว"
#                 st.rerun()

#     with t3:
#         st.markdown("### 🎒 คลังไอเทมสนับสนุน")
#         c_tool, c_qty, c_btn = st.columns([2, 1, 1])
#         tool_sel = c_tool.selectbox("เลือกไอเทม", MASTER_TOOLS + ["➕ พิมพ์เอง..."], key=f"t_sel_{item_id}")
#         final_tool = st.text_input("ชื่อไอเทมใหม่", key=f"t_cust_{item_id}") if tool_sel == "➕ พิมพ์เอง..." else tool_sel
#         qty = c_qty.number_input("จำนวน", min_value=1, value=1, key=f"t_qty_{item_id}")
        
#         if c_btn.button("➕ เก็บเข้ากระเป๋า", use_container_width=True, key=f"btn_add_tool_{item_id}"):
#             current_tools = item.get('tools', [])
#             current_tools.append({"item": final_tool, "amount": int(qty)})
#             supabase.table("cleaning_plans").update({"tools": current_tools}).eq("id", item_id).execute()
#             st.session_state.success_msg = f"🎒 เก็บ {final_tool} เข้าคลังแล้ว!"
#             st.rerun()
            
#         st.divider()
#         for i, t in enumerate(item.get('tools', [])):
#             col_t, col_b = st.columns([5, 1])
#             col_t.markdown(f"📦 **{t['item']}** x{t['amount']}")
#             if col_b.button("🗑️", key=f"del_t_{item_id}_{i}"):
#                 new_tools = item.get('tools', [])
#                 new_tools.pop(i)
#                 supabase.table("cleaning_plans").update({"tools": new_tools}).eq("id", item_id).execute()
#                 st.session_state.success_msg = "🗑️ นำอุปกรณ์ออกจากคลังแล้ว"
#                 st.rerun()

#     with t4:
#         st.error("⚠️ การลบด่านจะปิดหน้าต่างนี้ทันที")
#         if st.button("🧨 ยืนยันการลบด่าน", use_container_width=True, key=f"del_zone_{item_id}"):
#             supabase.table("cleaning_plans").delete().eq("id", item_id).execute()
#             st.session_state.last_c = None 
#             st.session_state.success_msg = "🧨 ระเบิดด่านทิ้งเรียบร้อย!"
#             st.rerun()

# # --- 4. MAIN LAYOUT ---
# st.markdown("<h1>SUPER 5S WORLD</h1>", unsafe_allow_html=True)
# tab_map, tab_score = st.tabs(["🎮 แผนที่ตะลุยด่าน", "🏆 ตารางคะแนนและสรุปผล"])

# all_plans = get_all_plans()

# with tab_map:
#     col_info, col_display = st.columns([1.5, 5])
#     with col_info:
#         # --- 🔍 ระบบ Zoom Scale ---
#         st.markdown("### 🔍 Zoom Scale")
#         zoom_scale = st.slider("ปรับขนาด (%)", 50, 250, 100, step=10, help="เลื่อนเพื่อขยายแผนที่ให้จิ้มง่ายขึ้น")
#         zoom_factor = zoom_scale / 100
        
#         st.button("🔄 ล้างจุดวาด", on_click=lambda: st.session_state.update({"points": []}), use_container_width=True)
#         if os.path.exists("mario.png"): st.image("mario.png", use_container_width=True)
#         st.markdown("""
#         <div class="how-to-play">
#             <b>🎮 วิธีเล่น (How to Play)</b><br>
#             1. <b>วาด:</b> คลิกบนแผนที่ 4 จุดเพื่อสร้างโซน<br>
#             2. <b>จัดการ:</b> คลิกในกรอบแดงเพื่อเพิ่ม 🎒อุปกรณ์ หรือ 🧹กิจกรรม<br>
#             3. <b>ซูม:</b> ถ้าจิ้มไม่โดน ให้เลื่อน Zoom ด้านบนครับ<br>
#         </div>
#         """, unsafe_allow_html=True)

#     with col_display:
#         try:
#             img = Image.open("map.png")
#             orig_w, orig_h = img.size
#             draw = ImageDraw.Draw(img)
            
#             # วาดโซนทั้งหมด
#             for p in all_plans:
#                 c = p.get('coords', {}).get('points', [])
#                 if c:
#                     poly = [(float(pt['x'].replace('%',''))*orig_w/100, float(pt['y'].replace('%',''))*orig_h/100) for pt in c]
#                     draw.polygon(poly, outline="#E4000F", width=10)
#                     draw.text((poly[0][0], poly[0][1] - 35), f" {p['zone_name']}", fill="#F8B800", font_size=28, stroke_width=3, stroke_fill="black")
            
#             # วาดจุดเหลืองที่กำลังเลือก
#             if "points" not in st.session_state: st.session_state.points = []
#             for p in st.session_state.points:
#                 draw.ellipse((p[0]-15, p[1]-15, p[0]+15, p[1]+15), fill="#F8B800", outline="white")
            
#             # แสดงแผนที่พร้อม Zoom Factor (สำคัญ: key ต้องเปลี่ยนตาม zoom)
#             raw_click = streamlit_image_coordinates(img, key=f"m_map_{zoom_scale}", width=int(orig_w * zoom_factor))
            
#             # แปลงพิกัดกลับเป็นขนาดจริงเพื่อความแม่นยำ
#             click = None
#             if raw_click:
#                 click = {"x": raw_click["x"] / zoom_factor, "y": raw_click["y"] / zoom_factor}
                
#         except: st.error("ไม่พบไฟล์ map.png กรุณาอัปโหลดรูปแผนที่")

# # --- 5. LOGIC ---
# if click:
#     cx, cy = click["x"], click["y"]
#     if "last_c" not in st.session_state or st.session_state.last_c != (cx, cy):
#         st.session_state.last_c = (cx, cy)
#         target = None
#         for p in all_plans:
#             c = p.get('coords', {}).get('points', [])
#             if c:
#                 poly = [(float(pt['x'].replace('%',''))*orig_w/100, float(pt['y'].replace('%',''))*orig_h/100) for pt in c]
#                 if is_inside(cx, cy, poly): 
#                     target = p
#                     break
        
#         if target: 
#             edit_mission_dialog(target['id'])
#             st.stop() 
#         else:
#             st.session_state.points.append((cx, cy))
#             if len(st.session_state.points) == 4:
#                 if not is_convex(st.session_state.points):
#                     st.toast("⚠️ เส้นห้ามตัดกัน!", icon="🧨")
#                     st.session_state.points = [] 
#                     st.rerun()
#                 else:
#                     create_zone_dialog(st.session_state.points, orig_w, orig_h)
#                     st.stop()
#             else:
#                 st.rerun()


# with tab_score:
#     if all_plans:
#         df_data = []
#         for p in all_plans:
#             t_str = ", ".join([f"{x['item']}(x{x['amount']})" for x in p.get('tools', [])])
#             a_str = ", ".join([x['name'] for x in p.get('activities', [])])
#             df_data.append({"ด่าน": p['zone_name'], "ฮีโร่": p.get('responsible_staff'), "อุปกรณ์": t_str, "กิจกรรม": a_str})
#         st.dataframe(pd.DataFrame(df_data), use_container_width=True)



import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image, ImageDraw
import pandas as pd
from supabase import create_client, Client
import os

# --- 1. CONFIG & MARIO THEME ---
st.set_page_config(layout="wide", page_title="โลก 5ส ของมาริโอ้", page_icon="🍄")

@st.cache_resource
def get_supabase():
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()

# แจ้งเตือน Toast
if "success_msg" in st.session_state:
    st.toast(st.session_state.success_msg)
    del st.session_state.success_msg

MASTER_TOOLS = ["ไม้กวาด", "น้ำยา", "ผ้าคลุมกันฝุ่น", "ถุงขยะ", "ถังน้ำ", "แปรงขัดพื้น", "เครื่องดูดฝุ่น", "ไม้ถูพื้น", "ถุงมือ", "หน้ากากกันฝุ่น"]
PRESET_ACTIVITIES = ["สะสาง: แยกของไม่จำเป็นออก", "สะดวก: ตีเส้นแบ่งเขต/ติดป้ายชื่อ", "สะอาด: ปัดหยากไย่และเช็ดพื้น", "สุขลักษณะ: ถ่ายรูป Before & After", "สร้างนิสัย: บันทึกมาตรฐานใหม่"]

# CSS (เดิม)
st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Kanit:wght@400;700;800&display=swap');
    .stApp { background-color: #5C94FC; font-family: 'Kanit', sans-serif; }
    h1 { font-family: 'Press Start 2P', cursive; color: #FFFFFF !important; text-shadow: 4px 4px 0px #E4000F; text-align: center; font-size: 38px !important; }
    .stTabs [data-baseweb="tab-list"] { background-color: #008800; border: 4px solid #000; padding: 8px; }
    .stTabs [data-baseweb="tab"] { color: white !important; }
    .stTabs [aria-selected="true"] { background-color: #E4000F !important; }
    .stButton > button { background-color: #F8B800 !important; border: 3px solid #000 !important; font-weight: 800 !important; box-shadow: 3px 3px 0px #8C5200; }
</style>""", unsafe_allow_html=True)

# --- 2. ฟังก์ชันช่วยประมวลผล ---
def is_inside(x, y, poly):
    n, inside = len(poly), False
    if n == 0: return False
    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y) and y <= max(p1y, p2y) and x <= max(p1x, p2x):
            if p1y != p2y: xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
            if p1x == p2x or x <= xinters: inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def is_convex(points):
    def cp(o, a, b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    points = list(points); n = len(points)
    res = [cp(points[i], points[(i+1)%n], points[(i+2)%n]) for i in range(n)]
    return all(x > 0 for x in res) or all(x < 0 for x in res)

# --- 3. DIALOGS ---
@st.dialog("🚩 สร้างด่านใหม่")
def create_zone_dialog(points, w, h):
    st.markdown("### 🍄 สร้างโซนใหม่")
    dept = st.selectbox("เลือกแผนก", ["WH", "SH", "TP", "LM", "BD", "EOE", "ENG", "PC", "➕ อื่นๆ..."])
    custom_dept = st.text_input("ระบุแผนกใหม่") if dept == "➕ อื่นๆ..." else ""
    with st.form("new_zone_form"):
        z = st.text_input("ชื่อด่าน (Eng)")
        staff = st.text_input("ผู้รับผิดชอบ")
        if st.form_submit_button("🔨 สร้างด่าน"):
            final_dept = custom_dept if dept == "➕ อื่นๆ..." else dept
            p_pct = [{"x": f"{(p[0]/w)*100}%", "y": f"{(p[1]/h)*100}%"} for p in points]
            supabase.table("cleaning_plans").insert({"zone_name": z, "dept": final_dept, "responsible_staff": staff, "coords": {"points": p_pct}, "tools": [], "activities": []}).execute()
            st.session_state.points = []; st.session_state.success_msg = "🏰 สร้างสำเร็จ!"; st.rerun()

@st.dialog("⭐️ LEVEL SETTINGS", width="large")
def edit_mission_dialog(item_id):
    # โหลดข้อมูลเข้า Temp ครั้งแรก
    if f"temp_init_{item_id}" not in st.session_state:
        res = supabase.table("cleaning_plans").select("*").eq("id", item_id).execute()
        if res.data:
            item = res.data[0]
            st.session_state[f"temp_acts_{item_id}"] = item.get('activities', [])
            st.session_state[f"temp_tools_{item_id}"] = item.get('tools', [])
            st.session_state[f"temp_name_{item_id}"] = item['zone_name']
            st.session_state[f"temp_staff_{item_id}"] = item.get('responsible_staff', '')
            st.session_state[f"temp_init_{item_id}"] = True

    t1, t2, t3, t4 = st.tabs(["📊 ข้อมูลหลัก", "🧹 กิจกรรม", "🎒 อุปกรณ์", "🧨 ลบด่าน"])
    
    with t1:
        st.session_state[f"temp_name_{item_id}"] = st.text_input("ชื่อด่าน", value=st.session_state[f"temp_name_{item_id}"])
        st.session_state[f"temp_staff_{item_id}"] = st.text_input("ฮีโร่", value=st.session_state[f"temp_staff_{item_id}"])

    with t2:
        st.markdown("### 🧹 ภารกิจ (เพิ่มได้เรื่อยๆ)")
        a_sel = st.selectbox("กิจกรรม", ["➕ พิมพ์เอง..."] + PRESET_ACTIVITIES, key=f"asel_{item_id}")
        a_cust = st.text_input("ระบุกิจกรรม", key=f"acust_{item_id}")
        c1, c2 = st.columns(2); n_p = c1.number_input("คน", 1, 50, 1, key=f"np_{item_id}"); n_h = c2.number_input("ชม.", 1, 50, 1, key=f"nh_{item_id}")
        
        # แก้ปัญหา Popup ปิด: ใช้ on_click เพื่อรันเฉพาะกิจ
        def add_act():
            name = a_cust if a_sel == "➕ พิมพ์เอง..." else a_sel
            if name: st.session_state[f"temp_acts_{item_id}"].append({"name": name, "people": n_p, "hours": n_h})
        
        st.button("➕ เพิ่มลงตะกร้า", use_container_width=True, on_click=add_act)

        for i, a in enumerate(st.session_state[f"temp_acts_{item_id}"]):
            cols = st.columns([3, 1, 1, 0.5])
            cols[0].write(f"🔹 {a['name']}"); cols[1].write(f"👥{a['people']}"); cols[2].write(f"⏱️{a['hours']}")
            if cols[3].button("🗑️", key=f"da_{item_id}_{i}"):
                st.session_state[f"temp_acts_{item_id}"].pop(i); st.rerun()

    with t3:
        st.markdown("### 🎒 อุปกรณ์")
        t_sel = st.selectbox("ไอเทม", MASTER_TOOLS + ["➕ พิมพ์เอง..."], key=f"tsel_{item_id}")
        t_qty = st.number_input("จำนวน", 1, 100, 1, key=f"tq_{item_id}")
        
        def add_tool():
            st.session_state[f"temp_tools_{item_id}"].append({"item": t_sel, "amount": t_qty})
        
        st.button("➕ เพิ่มเข้าเป้", use_container_width=True, on_click=add_tool)
        
        for i, t in enumerate(st.session_state[f"temp_tools_{item_id}"]):
            cols = st.columns([4, 1, 0.5])
            cols[0].write(f"📦 {t['item']}"); cols[1].write(f"x{t['amount']}")
            if cols[2].button("🗑️", key=f"dt_{item_id}_{i}"):
                st.session_state[f"temp_tools_{item_id}"].pop(i); st.rerun()

    st.divider()
    if st.button("💾 บันทึกทุกอย่างลงฐานข้อมูล", type="primary", use_container_width=True):
        supabase.table("cleaning_plans").update({"zone_name": st.session_state[f"temp_name_{item_id}"], "responsible_staff": st.session_state[f"temp_staff_{item_id}"], "activities": st.session_state[f"temp_acts_{item_id}"], "tools": st.session_state[f"temp_tools_{item_id}"]}).eq("id", item_id).execute()
        for k in [f"temp_init_{item_id}", f"temp_acts_{item_id}", f"temp_tools_{item_id}", f"temp_name_{item_id}", f"temp_staff_{item_id}"]:
            if k in st.session_state: del st.session_state[k]
        st.session_state.success_msg = "✅ บันทึกสำเร็จ!"; st.rerun()

    with t4:
        if st.button("🧨 ยืนยันลบด่าน", use_container_width=True):
            supabase.table("cleaning_plans").delete().eq("id", item_id).execute()
            st.session_state.success_msg = "🧨 ลบแล้ว"; st.rerun()

# --- 4. MAIN LAYOUT ---
st.markdown("<h1>SUPER 5S WORLD</h1>", unsafe_allow_html=True)
tab_map, tab_score = st.tabs(["🎮 แผนที่ตะลุยด่าน", "🏆 ตารางคะแนนและสรุปผล"])

with tab_map:
    all_plans = supabase.table("cleaning_plans").select("*").order("created_at", desc=True).execute().data
    col_info, col_display = st.columns([1.5, 5])
    
    with col_info:
        zoom_scale = st.slider("Zoom (%)", 50, 250, 100, step=10, key="zoom_slider")
        zoom_factor = zoom_scale / 100
        if st.button("🔄 ล้างจุดวาด", use_container_width=True):
            st.session_state.points = []; st.rerun()
        if os.path.exists("mario.png"): st.image("mario.png")

    with col_display:
        try:
            img = Image.open("map.png")
            orig_w, orig_h = img.size
            draw = ImageDraw.Draw(img)
            for p in all_plans:
                c = p.get('coords', {}).get('points', [])
                if c:
                    poly = [(float(pt['x'].replace('%',''))*orig_w/100, float(pt['y'].replace('%',''))*orig_h/100) for pt in c]
                    draw.polygon(poly, outline="#E4000F", width=10)
                    draw.text((poly[0][0], poly[0][1] - 35), f" {p['zone_name']}", fill="#F8B800", font_size=28, stroke_width=3, stroke_fill="black")
            
            if "points" not in st.session_state: st.session_state.points = []
            for p in st.session_state.points:
                draw.ellipse((p[0]-15, p[1]-15, p[0]+15, p[1]+15), fill="#F8B800", outline="white")
            
            raw_click = streamlit_image_coordinates(img, key=f"m_map_{zoom_scale}", width=int(orig_w * zoom_factor))
            
            if raw_click:
                cx, cy = raw_click["x"] / zoom_factor, raw_click["y"] / zoom_factor
                if st.session_state.get("last_c") != (cx, cy):
                    st.session_state.last_c = (cx, cy)
                    target = None
                    for p in all_plans:
                        c = p.get('coords', {}).get('points', [])
                        if c:
                            poly = [(float(pt['x'].replace('%',''))*orig_w/100, float(pt['y'].replace('%',''))*orig_h/100) for pt in c]
                            if is_inside(cx, cy, poly): target = p; break
                    
                    if target:
                        edit_mission_dialog(target['id'])
                    else:
                        st.session_state.points.append((cx, cy))
                        if len(st.session_state.points) == 4:
                            if is_convex(st.session_state.points):
                                create_zone_dialog(st.session_state.points, orig_w, orig_h)
                            else:
                                st.toast("⚠️ เส้นตัดกัน!")
                                st.session_state.points = []
                                st.rerun()
                        else:
                            st.rerun()
        except Exception as e: st.error(f"Error: {e}")

with tab_score:
    if all_plans:
        df_data = []
        for p in all_plans:
            t_str = ", ".join([f"{x['item']}(x{x['amount']})" for x in p.get('tools', [])])
            a_str = ", ".join([x['name'] for x in p.get('activities', [])])
            df_data.append({"ด่าน": p['zone_name'], "ฮีโร่": p.get('responsible_staff'), "อุปกรณ์": t_str, "กิจกรรม": a_str})
        st.dataframe(pd.DataFrame(df_data), use_container_width=True)