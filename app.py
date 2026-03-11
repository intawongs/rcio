import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image, ImageDraw
import pandas as pd
from supabase import create_client, Client
import os

# --- 1. CONFIG & MARIO THEME ---
st.set_page_config(layout="wide", page_title="โลก 5ส ของมาริโอ้", page_icon="🍄")

try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except:
    st.error("❌ เชื่อมต่อฐานข้อมูลไม่ได้!"); st.stop()

MASTER_TOOLS = ["ไม้กวาด", "น้ำยา", "ผ้าคลุมกันฝุ่น", "ถุงขยะ", "ถังน้ำ", "แปรงขัดพื้น", "เครื่องดูดฝุ่น", "ไม้ถูพื้น", "ถุงมือ", "หน้ากากกันฝุ่น"]

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Kanit:wght@400;700;800&display=swap');
    
    .stApp { background-color: #5C94FC; font-family: 'Kanit', sans-serif; }
    
    h1 { 
        font-family: 'Press Start 2P', cursive; 
        color: #FFFFFF !important; 
        text-shadow: 4px 4px 0px #E4000F; 
        text-align: center; 
        font-size: 38px !important;
        margin-bottom: 5px !important;
    }

    .stTabs [data-baseweb="tab-list"] { 
        background-color: #008800; 
        border: 4px solid #000; 
        padding: 8px;
    }
    .stTabs [data-baseweb="tab"] { 
        color: white !important; 
        font-size: 24px !important; 
        font-weight: 800 !important;
        padding: 10px 20px !important;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #E4000F !important; 
    }

    .how-to-play {
        background-color: #F8B800;
        border: 3px solid #000;
        padding: 15px;
        border-radius: 10px;
        margin-top: 10px;
        font-size: 16px;
        color: #000;
        line-height: 1.6;
        box-shadow: 4px 4px 0px #000;
    }

    .stButton > button { 
        background-color: #F8B800 !important; 
        border: 3px solid #000 !important; 
        font-weight: 800 !important; 
        font-size: 20px !important;
        box-shadow: 3px 3px 0px #8C5200;
        margin-bottom: 10px;
    }
            
    @media (max-width: 991px) {
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- 2. ฟังก์ชันหลัก ---
def get_all_plans():
    res = supabase.table("cleaning_plans").select("*").order("created_at", desc=True).execute()
    return res.data

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
    # ฟังก์ชันเช็คว่ารูป 4 จุดนี้ "กางออก" เป็นสี่เหลี่ยม ไม่ใช่รูปนาฬิกาทราย
    def cross_product(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    
    cp = []
    n = len(points)
    for i in range(n):
        cp.append(cross_product(points[i], points[(i+1)%n], points[(i+2)%n]))
    
    # ถ้าค่า Cross Product มีเครื่องหมายเดียวกันหมด (+ หรือ - ทั้งหมด) แสดงว่าเป็นสี่เหลี่ยมที่นูนสวย
    return all(x > 0 for x in cp) or all(x < 0 for x in cp)

# --- 3. DIALOGS ---
#@st.dialog("🚩 สร้างด่านใหม่")
# def create_zone_dialog(points, w, h):
#     st.markdown("### 🍄 สร้างโซนใหม่")
#     with st.form("nz"):
#         z = st.text_input("ชื่อด่าน")
#         d = st.selectbox("แผนก", ["WH", "SH", "TP", "LM", "BD", "EOE", "ENG", "PC"])
#         staff = st.text_input("ผู้รับผิดชอบ")
#         if st.form_submit_button("🔨 เริ่มสร้างด่าน"):
#             p_pct = [{"x": f"{(p[0]/w)*100}%", "y": f"{(p[1]/h)*100}%"} for p in points]
#             supabase.table("cleaning_plans").insert({
#                 "zone_name": z, "dept": d, "responsible_staff": staff,
#                 "coords": {"points": p_pct}, "tools": []
#             }).execute()
#             st.session_state.points = []
#             st.rerun()
@st.dialog("🚩 สร้างด่านใหม่")
def create_zone_dialog(points, w, h):
    st.markdown("### 🍄 สร้างโซนใหม่")
    
    # --- ส่วนเลือกแผนก (อยู่นอก Form เพื่อให้เลือกแล้วช่องพิมพ์โผล่ทันที) ---
    dept_options = ["WH", "SH", "TP", "LM", "BD", "EOE", "ENG", "PC", "➕ อื่นๆ (ระบุเอง)..."]
    d_select = st.selectbox("เลือกแผนก", dept_options)
    
    custom_dept = ""
    if d_select == "➕ อื่นๆ (ระบุเอง)...":
        custom_dept = st.text_input("📝 ระบุชื่อแผนกใหม่")
    
    # --- ส่วนที่เหลือใช้ Form ตามปกติ ---
    with st.form("nz"):
        z = st.text_input("ชื่อด่าน (Zone Name)")
        staff = st.text_input("ฮีโร่ผู้รับผิดชอบ (Owner)")
        
        if st.form_submit_button("🔨 เริ่มสร้างด่าน (START)"):
            # เลือกใช้ชื่อแผนกจากช่องที่พิมพ์ หรือจาก Selectbox
            final_dept = custom_dept if d_select == "➕ อื่นๆ (ระบุเอง)..." else d_select
            
            if not z or not final_dept:
                st.error("⚠️ โปรดระบุชื่อด่านและแผนกให้ครบถ้วน!")
            else:
                p_pct = [{"x": f"{(p[0]/w)*100}%", "y": f"{(p[1]/h)*100}%"} for p in points]
                supabase.table("cleaning_plans").insert({
                    "zone_name": z, 
                    "dept": final_dept, 
                    "responsible_staff": staff,
                    "coords": {"points": p_pct}, 
                    "tools": []
                }).execute()
                
                st.session_state.points = []
                st.rerun()

@st.dialog("⭐️ LEVEL SETTINGS")
def edit_mission_dialog(item_id):
    res = supabase.table("cleaning_plans").select("*").eq("id", item_id).execute()
    if not res.data: return
    item = res.data[0]
    t1, t2, t3 = st.tabs(["📊 ข้อมูล", "🎒 อุปกรณ์", "🧨 ลบ"])
    with t1:
        with st.form("f1"):
            u_name = st.text_input("ชื่อด่าน", value=item['zone_name'])
            u_staff = st.text_input("ฮีโร่", value=item.get('responsible_staff', ''))
            if st.form_submit_button("อัปเดต"):
                supabase.table("cleaning_plans").update({"zone_name": u_name, "responsible_staff": u_staff}).eq("id", item_id).execute()
                st.rerun()
    with t2:
        st.write("### 🎒 จัดการไอเทม")
        c1, c2, c3 = st.columns([2, 1, 1])
        sel = c1.selectbox("เลือก", MASTER_TOOLS + ["➕ พิมพ์เอง..."], key=f"s_{item_id}")
        final_tool = sel
        if sel == "➕ พิมพ์เอง...":
            final_tool = st.text_input("ชื่ออุปกรณ์", key=f"c_{item_id}")
        qty = c2.number_input("จำนวน", min_value=1, value=1, key=f"q_{item_id}")
        if c3.button("➕ เก็บ", key=f"a_{item_id}"):
            current = item.get('tools', [])
            current.append({"item": final_tool, "amount": int(qty)})
            supabase.table("cleaning_plans").update({"tools": current}).eq("id", item_id).execute()
            st.rerun()
        st.divider()
        for i, t in enumerate(item.get('tools', [])):
            col_t, col_b = st.columns([4, 1])
            col_t.markdown(f"💰 **{t['item']}** x{t['amount']}")
            if col_b.button("🗑️", key=f"d_{item_id}_{i}"):
                item['tools'].pop(i)
                supabase.table("cleaning_plans").update({"tools": item['tools']}).eq("id", item_id).execute()
                st.rerun()
    with t3:
        if st.button("🧨 ยืนยันทำลายด่าน"):
            supabase.table("cleaning_plans").delete().eq("id", item_id).execute()
            st.rerun()

# --- 4. MAIN LAYOUT ---
st.markdown("<h1>SUPER 5S WORLD</h1>", unsafe_allow_html=True)
tab_map, tab_score = st.tabs(["🎮 แผนที่ตะลุยด่าน", "🏆 ตารางคะแนนและสรุปผล"])

all_plans = get_all_plans()

with tab_map:
    # สลับเอา col_info ขึ้นก่อนในโค้ด (เพื่อให้ Mobile เห็นก่อน)
    # แต่บน Desktop มันจะอยู่ซ้าย-ขวา ตามสัดส่วน [1.5, 5]
    col_info, col_display = st.columns([1.5, 5])
    
    with col_info:
        # --- 1. ปุ่มและรูปมาริโอ้ (จะอยู่ด้านบนในมือถือ) ---
        st.button("🔄 ล้างจุดวาด", on_click=lambda: st.session_state.update({"points": []}), use_container_width=True)
        
        if os.path.exists("mario.png"):
            st.image("mario.png", use_container_width=True)
            
        st.markdown("""
        <div class="how-to-play">
            <b>🎮 วิธีเล่น (How to Play)</b><br>
            1. <b>สร้างด่าน:</b> คลิกบนแผนที่ <b>4 จุด</b> เพื่อวาดพื้นที่<br>
            2. <b>จัดการด่าน:</b> คลิกที่ <b>ในกรอบสีแดง</b> เพื่อเพิ่มอุปกรณ์<br>
            3. <b>รีเซ็ต:</b> กด <b>'ล้างจุดวาด'</b> หากต้องการเริ่มใหม่
        </div>
        """, unsafe_allow_html=True)

    with col_display:
        # --- 2. แผนที่ (จะอยู่ถัดลงมาในมือถือ) ---
        try:
            img = Image.open("map.png")
            w, h = img.size
            draw = ImageDraw.Draw(img)
            
            # วาดเส้นและชื่อด่าน (ใช้แบบตัดขอบดำตามที่แก้ไปก่อนหน้า)
            for p in all_plans:
                c = p.get('coords', {}).get('points', [])
                if c:
                    poly = [(float(pt['x'].replace('%',''))*w/100, float(pt['y'].replace('%',''))*h/100) for pt in c]
                    draw.polygon(poly, outline="#E4000F", width=10)
                    draw.text(
                        (poly[0][0], poly[0][1] - 35), 
                        f" {p['zone_name']}", 
                        fill="#F8B800", 
                        font_size=28, 
                        stroke_width=3, 
                        stroke_fill="black"
                    )
            
            # วาดจุดเหลืองที่กำลังเลือก
            if "points" not in st.session_state: st.session_state.points = []
            for p in st.session_state.points:
                draw.ellipse((p[0]-15, p[1]-15, p[0]+15, p[1]+15), fill="#F8B800", outline="white")
            
            # แสดงแผนที่
            click = streamlit_image_coordinates(img, key="m_map", width=None)
        except:
            st.error("ไม่พบไฟล์ map.png")

# with tab_map:
#     col_left, col_right = st.columns([5, 1.5])
    
#     with col_right:
#         # ปุ่มล้างจุด
#         st.button("🔄 ล้างจุดวาด", on_click=lambda: st.session_state.update({"points": []}), use_container_width=True)
        
#         # --- แสดงรูปจากไฟล์ mario.PNG ---
#         if os.path.exists("mario.png"):
#             st.image("mario.png", use_container_width=True)
#         else:
#             st.warning("⚠️ ไม่พบไฟล์ mario.PNG ในโฟลเดอร์")
        
#         # --- คู่มือการเล่น ---
#         st.markdown("""
#         <div class="how-to-play">
#             <b>🎮 วิธีเล่น (How to Play)</b><br>
#             1. <b>สร้างด่าน:</b> คลิกบนแผนที่ว่างๆ <b>4 จุด</b> เพื่อวาดพื้นที่ใหม่<br>
#             2. <b>จัดการด่าน:</b> คลิกที่ <b> ชื่อด่าน</b> เพื่อเพิ่มอุปกรณ์หรือแก้ไขข้อมูล<br>
#             3. <b>เก็บไอเทม:</b> ไปที่เมนู <b>'🎒 อุปกรณ์'</b> เพื่อเลือกของใส่กระเป๋า<br>
#             4. <b>รีเซ็ต:</b> กดปุ่ม <b>'ล้างจุดวาด'</b> หากต้องการยกเลิกจุดที่กำลังวาด
#         </div>
#         """, unsafe_allow_html=True)

#     with col_left:
#         try:
#             img = Image.open("map.png")
#             w, h = img.size
#             draw = ImageDraw.Draw(img)
#             # for p in all_plans:
#             #     c = p.get('coords', {}).get('points', [])
#             #     if c:
#             #         poly = [(float(pt['x'].replace('%',''))*w/100, float(pt['y'].replace('%',''))*h/100) for pt in c]
#             #         draw.polygon(poly, outline="#E4000F", width=10)
#             #         draw.text(poly[0], f" 🍄{p['zone_name']}", fill="white", font_size=40)
#             # --- ค้นหาบรรทัดนี้ในโค้ดเดิมของคุณ ---
#             for p in all_plans:
#                 c = p.get('coords', {}).get('points', [])
#                 if c:
#                     poly = [(float(pt['x'].replace('%',''))*w/100, float(pt['y'].replace('%',''))*h/100) for pt in c]
                    
#                     # 1. วาดเส้นขอบโซน (สีแดง)
#                     draw.polygon(poly, outline="#E4000F", width=10)
                    
#                     # 2. แก้ไขบรรทัด draw.text ตรงนี้ครับ! (ก๊อปปี้ไปวางทับได้เลย)
#                     draw.text(
#                         (poly[0][0], poly[0][1] - 30), # ขยับขึ้นบนนิดหน่อยไม่ให้ทับเส้น
#                         f" {p['zone_name']}", 
#                         fill="#F8B800",       # เปลี่ยนเป็นสีเหลืองมาริโอ้
#                         font_size=28,         # ปรับขนาดให้ใหญ่ขึ้น
#                         stroke_width=3,      # เพิ่มขอบสีดำ
#                         stroke_fill="black"  # ตัดขอบดำให้อ่านง่าย
#                     )
            
#             if "points" not in st.session_state: st.session_state.points = []
#             for p in st.session_state.points:
#                 draw.ellipse((p[0]-15, p[1]-15, p[0]+15, p[1]+15), fill="#F8B800", outline="white")
            
#             click = streamlit_image_coordinates(img, key="m_map", width=None)
#         except: st.error("ไม่พบไฟล์ map.png"); st.stop()

# --- 5. LOGIC ---
# --- 5. LOGIC (จุดที่ต้องแก้) ---
if click:
    cx, cy = click["x"], click["y"]
    if "last_c" not in st.session_state or st.session_state.last_c != (cx, cy):
        st.session_state.last_c = (cx, cy)
        
        # เช็คว่าคลิกโดนด่านที่มีอยู่แล้วหรือไม่
        target = None
        for p in all_plans:
            c = p.get('coords', {}).get('points', [])
            if c:
                poly = [(float(pt['x'].replace('%',''))*w/100, float(pt['y'].replace('%',''))*h/100) for pt in c]
                if is_inside(cx, cy, poly): target = p; break
        
        if target: 
            edit_mission_dialog(target['id'])
        else:
            # เพิ่มจุดใหม่เข้าไปในลิสต์
            st.session_state.points.append((cx, cy))
            
            # เมื่อครบ 4 จุด ให้ตรวจสอบเบื้องต้น
            if len(st.session_state.points) == 4:
                # 1. เช็คความนูนของรูปทรง (ห้ามเส้นตัดกัน)
                if not is_convex(st.session_state.points):
                    # ใช้ toast เพื่อให้เด้งเตือนทันทีแม้จะ rerun
                    st.toast("⚠️ เส้นห้ามตัดกัน! วาดใหม่นะมาริโอ้", icon="🧨")
                    # หน่วงเวลาเล็กน้อย หรือใช้ st.error โดยไม่มี rerun เพื่อให้คนเห็นข้อความ
                    st.error("⚠️ รูปทรงไม่ถูกต้อง: โปรดวาดเรียงลำดับจุด (เช่น วนตามเข็มนาฬิกา)")
                    st.session_state.points = [] 
                    # ไม่ต้องใส่ st.rerun() ตรงนี้ เพื่อให้ Error Message ค้างให้คนอ่าน
                else:
                    # 2. [เพิ่มใหม่] เช็คว่ามีจุดใดจุดหนึ่งไปอยู่ในโซนอื่นที่มีอยู่แล้วไหม
                    is_overlapping = False
                    for p_existing in all_plans:
                        c = p_existing.get('coords', {}).get('points', [])
                        if c:
                            # สร้างพื้นที่ของด่านที่มีอยู่แล้ว
                            poly_existing = [(float(pt['x'].replace('%',''))*w/100, float(pt['y'].replace('%',''))*h/100) for pt in c]
                            
                            # เช็คจุดใหม่ทั้ง 4 จุด ว่ามีจุดไหนหลุดเข้าไปในด่านเก่าไหม
                            for new_pt in st.session_state.points:
                                if is_inside(new_pt[0], new_pt[1], poly_existing):
                                    is_overlapping = True
                                    break
                    
                    if is_overlapping:
                        st.error("⚠️ พื้นที่นี้มีเจ้าของแล้ว! ห้ามวาดทับซ้อนกัน")
                        st.session_state.points = []
                    else:
                        # ถ้าผ่านทุกด่าน... สร้างด่านได้!
                        create_zone_dialog(st.session_state.points, w, h)
            else: 
                st.rerun()



                
# if click:
#     cx, cy = click["x"], click["y"]
#     if "last_c" not in st.session_state or st.session_state.last_c != (cx, cy):
#         st.session_state.last_c = (cx, cy)
#         target = None
#         for p in all_plans:
#             c = p.get('coords', {}).get('points', [])
#             if c:
#                 poly = [(float(pt['x'].replace('%',''))*w/100, float(pt['y'].replace('%',''))*h/100) for pt in c]
#                 if is_inside(cx, cy, poly): target = p; break
#         if target: edit_mission_dialog(target['id'])
#         else:
#             st.session_state.points.append((cx, cy))
#             if len(st.session_state.points) == 4:
#                 create_zone_dialog(st.session_state.points, w, h)
#             else: st.rerun()

with tab_score:
    if all_plans:
        df = pd.DataFrame([{"ด่าน": p['zone_name'], "ฮีโร่": p.get('responsible_staff'), "อุปกรณ์": ", ".join([f"{x['item']}(x{x['amount']})" for x in p.get('tools', [])])} for p in all_plans])
        st.dataframe(df, use_container_width=True)