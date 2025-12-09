import streamlit as st
import pandas as pd
import pyodbc
from datetime import date

# ========================= PAGE CONFIG =========================
st.set_page_config(page_title="Quotation Generator", layout="wide")

# ========================= CUSTOM CSS =========================
st.markdown("""
<style>
    .top-header {
        background: linear-gradient(90deg, #1976d2, #0d47a1);
        color: white; padding: 22px; border-radius: 14px; text-align: center;
        font-size: 38px; font-weight: bold; margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
    }
    .section-title {
        color: #1565c0; font-size: 24px; font-weight: bold;
        margin: 25px 0 15px; padding-bottom: 10px;
        border-bottom: 5px solid #42a5f5;
    }
    .price-box {
        background: #fff8e1; padding: 20px; border-radius: 12px;
        text-align: center; font-size: 30px; font-weight: bold;
        color: #e65100; border: 4px solid #ffb300;
        box-shadow: 0 4px 15px rgba(255,179,0,0.2);
    }
    .stButton > button {
        height: 58px !important; font-weight: bold; border-radius: 12px; font-size: 17px;
    }
    .total-box {
        background: #28a745; color: white; padding: 18px; border-radius: 12px;
        text-align: center; font-size: 28px; font-weight: bold;
    }
    .big-font {font-size: 32px; font-weight: bold; text-align: center; color: #003366;}
    .header-blue {font-weight: bold; color: #1565c0; text-align: center;}
    .calc-cell {background: #e6f7ff; padding: 8px; border-radius: 6px; text-align: center;}
    .row-even {background: #f8f9fa;}
    .row-odd {background: #ffffff;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="top-header">QUOTATION GENERATOR</div>', unsafe_allow_html=True)

# ========================= DATABASE =========================
@st.cache_resource(show_spinner=False)
def get_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=PRATIKSHARAUT\\SQLEXPRESS;"
        "DATABASE=version1;"
        "Trusted_Connection=yes;"
    )

@st.cache_data(ttl=300)
def load_customers():
    try:
        with get_connection() as con:
            return pd.read_sql("SELECT name, phone, address FROM customers ORDER BY name", con)
    except:
        return pd.DataFrame(columns=["name", "phone", "address"])

@st.cache_data(ttl=300)
def load_categories():
    try:
        with get_connection() as con:
            df = pd.read_sql("SELECT CategoryName FROM Categories ORDER BY CategoryName", con)
            return ["General"] + df["CategoryName"].dropna().tolist()
    except:
        return ["General"]

@st.cache_data(ttl=300)
def load_inventory():
    try:
        with get_connection() as con:
            cursor = con.cursor()
            cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'inventory'")
            cols = [row[0] for row in cursor.fetchall()]
            select_cols = "Description, Ratings, Make, MaterialName, TotalQuantity, Discount, ListPrice"
            if "CategoryName" in cols:
                select_cols = "CategoryName, " + select_cols
            query = f"SELECT {select_cols} FROM inventory ORDER BY Description"
            return pd.read_sql(query, con)
    except Exception as e:
        st.error(f"Inventory Error: {e}")
        return pd.DataFrame()

# Load data
customers_df = load_customers()
category_list = load_categories()
inventory_df = load_inventory()
has_category = "CategoryName" in inventory_df.columns

# ========================= SESSION STATE =========================
COLUMNS = ["section", "description", "ratings", "make", "material", "quantity", "net_qty",
           "list_price", "discount", "disc_unit_price", "disc_gross_price", "lp_gross_price"]

if "items_df" not in st.session_state:
    st.session_state.items_df = pd.DataFrame(columns=COLUMNS)
if "show_add_category" not in st.session_state:
    st.session_state.show_add_category = False

# ====================== DIALOGS (UNCHANGED) ======================
# [All your dialogs: Enclosure, Wiring, Busbar — fully preserved below]
@st.dialog("Enclosure Fabrication", width="large")
def show_enclosure_fabrication():
    st.markdown("<h1 class='big-font'>Enclosure Fabrication Details</h1>", unsafe_allow_html=True)

    if "enc_rows" not in st.session_state:
        st.session_state.enc_rows = [
            {"spec": "18 SWG", "mm": 1.20, "L": 2500.0, "W": 1250.0, "kg": 30.0, "include": False},
            {"spec": "16 SWG", "mm": 1.50, "L": 2500.0, "W": 1250.0, "kg": 40.0, "include": False},
            {"spec": "14 SWG", "mm": 2.00, "L": 2500.0, "W": 1250.0, "kg": 50.0, "include": False},
            {"spec": "13 SWG", "mm": 2.30, "L": 2500.0, "W": 1250.0, "kg": 60.0, "include": False},
            {"spec": "12 SWG", "mm": 2.64, "L": 2500.0, "W": 1250.0, "kg": 70.0, "include": False},
            {"spec": "11 SWG", "mm": 3.00, "L": 2500.0, "W": 1250.0, "kg": 80.0, "include": False},
            {"spec": "10 SWG", "mm": 3.25, "L": 2500.0, "W": 1250.0, "kg": 90.0, "include": False},
        ]
    if "enc_dim" not in st.session_state:
        st.session_state.enc_dim = [
            ["28+1+1", 2400.0, 300.0, 1600.0, 0.0],
            ["1", 0.0, 0.0, 0.0, 0.0],
            ["2", 0.0, 0.0, 0.0, 0.0],
            ["3", 0.0, 0.0, 0.0, 0.0],
            ["4", 0.0, 0.0, 0.0, 0.0],
            ["5", 0.0, 0.0, 0.0, 0.0],
        ]
    if "enc_percent" not in st.session_state:
        st.session_state.enc_percent = {"applied": False, "base": 0, "delta": 0, "final": 0, "text": ""}

    # Sheet Metal Table
    st.markdown("<div class='section-title'>Sheet Metal Specifications</div>", unsafe_allow_html=True)
    hcols = st.columns([0.7, 2.4, 1.1, 1.4, 1.4, 1.3, 1.6, 2.0])
    headers = ["", "Specification", "MM", "Length", "Width", "Kg", "Calculated Total", "Kg per Sqmm"]
    for c, h in zip(hcols, headers):
        if h: c.markdown(f"<div class='header-blue'>{h}</div>", unsafe_allow_html=True)

    total_weight = 0.0
    for i, row in enumerate(st.session_state.enc_rows):
        cols = st.columns([0.7, 2.4, 1.1, 1.4, 1.4, 1.3, 1.6, 2.0])
        bg = "#f8f9fa" if i % 2 == 0 else "#ffffff"
        inc = cols[0].checkbox("", value=row["include"], key=f"enc_inc_{i}")
        st.session_state.enc_rows[i]["include"] = inc

        # SPECIFICATION COLUMN TEXT NOW IN BOLD RED - HIGHLY VISIBLE
        cols[1].markdown(
            f"<div class='spec-cell' style='background:{bg}; "
            f"color: red; font-weight: bold; font-size: 1.1em; padding: 8px;'>"
            f"{row['spec']}</div>", 
            unsafe_allow_html=True
        )

        mm = cols[2].number_input("", value=row["mm"], step=0.01, format="%.3f", key=f"enc_mm_{i}", label_visibility="collapsed")
        L = cols[3].number_input("", value=row["L"], step=1.0, key=f"enc_L_{i}", label_visibility="collapsed")
        W = cols[4].number_input("", value=row["W"], step=1.0, key=f"enc_W_{i}", label_visibility="collapsed")
        kg = cols[5].number_input("", value=row["kg"], step=0.1, format="%.2f", key=f"enc_kg_{i}", label_visibility="collapsed")

        st.session_state.enc_rows[i].update({"mm": mm, "L": L, "W": W, "kg": kg})
        area = L * W
        calc = round(mm * area * 0.00000785, 2)
        kg_per = kg / area if area > 0 else 0.0
        if inc: total_weight += calc

        cols[6].markdown(f"<div class='calc-cell' style='color: red; font-weight: bold;'>{calc:.2f}</div>", unsafe_allow_html=True)
        cols[7].markdown(f"<div class='calc-cell' style='color: red; font-weight: bold;'>{kg_per:.10f}</div>", unsafe_allow_html=True)

    st.markdown("---")
    t1, t2 = st.columns([6, 4])
    t1.markdown("**Enclosure Total:**")
    t2.markdown(f"<div class='total-box' style='color: red; font-size: 1.4em; font-weight: bold;'>₹ {total_weight:,.2f}</div>", unsafe_allow_html=True)

    # Dimensions Table
    st.markdown("<div class='section-title'>Additional Enclosure Details</div>", unsafe_allow_html=True)
    dcols = st.columns([1.6, 1.9, 1.9, 1.9, 2.8])
    for c, h in zip(dcols, ["", "L", "W", "H", "Volume"]):
        c.markdown(f"<div class='header-blue'>{h}</div>", unsafe_allow_html=True)

    def enc_autofill(col_idx, val):
        if col_idx not in (1, 2): return
        fill = {1: [1, 3], 2: [3]}
        for r in fill.get(col_idx, []):
            if r < len(st.session_state.enc_dim):
                st.session_state.enc_dim[r][col_idx] = float(val)

    total_vol = 0
    for r in range(6):
        row = st.session_state.enc_dim[r]
        dc = st.columns([1.6, 1.9, 1.9, 1.9, 2.8])
        if r == 0:
            dc[0].text_input("", "28+1+1", disabled=True, key=f"enc_lab_fixed_{r}")
        else:
            dc[0].text_input("", value=row[0] if row[0] else str(r), key=f"enc_lab_{r}")

        L = dc[1].number_input("", value=float(row[1]), step=1.0, key=f"enc_dL_{r}", label_visibility="collapsed")
        W = dc[2].number_input("", value=float(row[2]), step=1.0, key=f"enc_dW_{r}", label_visibility="collapsed")
        H = dc[3].number_input("", value=float(row[3]), step=1.0, key=f"enc_dH_{r}", label_visibility="collapsed")

        if L != row[1]: enc_autofill(1, L)
        if W != row[2]: enc_autofill(2, W)

        st.session_state.enc_dim[r][1:4] = [L, W, H]
        vol = L * W * H
        st.session_state.enc_dim[r][4] = vol
        if r > 0: total_vol += vol
        dc[4].markdown(f"<div class='calc-cell' style='color: red; font-weight: bold;'>{int(vol):,}</div>", unsafe_allow_html=True)

    # Percent Adjustment
    st.markdown("---")
    pc1, pc2, pc3, pc4 = st.columns([2, 2, 2, 2])
    pc1.markdown("**Percent:**")
    pct_in = pc2.text_input("", placeholder="e.g. 10%, -5", key="enc_pct_input", label_visibility="collapsed")
    kc1, kc2, kc3, kc4 = st.columns([2, 2, 2, 2])
    kc1.markdown("**Total Kg:**")

    if st.button("Apply Percent", type="primary", key="enc_apply_pct"):
        try:
            txt = pct_in.strip()
            val = txt.rstrip("%")
            pct = float(val) / 100
            base = sum(r["kg"] for r in st.session_state.enc_rows if r["include"])
            delta = base * pct
            final = base + delta
            st.session_state.enc_percent = {
                "applied": True, "base": base, "delta": delta, "final": final,
                "text": txt + "%" if not txt.endswith("%") else txt
            }
            st.success(f"Applied {st.session_state.enc_percent['text']}!")
        except:
            st.error("Invalid input")

    res = st.session_state.enc_percent
    if res["applied"]:
        pc3.metric("Delta", f"{res['delta']:+.4f}")
        pc4.metric("Final", f"{res['final']:.4f}")
        kc2.metric("Base", f"{res['base']:.4f}")
        kc3.metric("Delta", f"{res['delta']:+.4f}")
        kc4.metric("Final", f"{res['final']:.4f}")

        st.markdown(f"""
        <div style='background-color:#ffebee; padding:15px; border-radius:10px; border-left:6px solid red;'>
            <h4 style='color:red; margin:0;'>Percent Adjustment: <strong>{res['text']}</strong></h4>
            <p style='color:red; margin:5px 0;'><strong>Base:</strong> {res['base']:.4f} kg &nbsp; | &nbsp; 
               <strong>Delta:</strong> {res['delta']:+.4f} kg &nbsp; | &nbsp; 
               <strong>Final Total:</strong> {res['final']:.4f} kg</p>
        </div>
        """, unsafe_allow_html=True)

    b1, b2 = st.columns(2)
    if b1.button("Total Volume", key="enc_total_vol"):
        st.success(f"Total Volume: <span style='color:red; font-size:1.2em; font-weight:bold;'>{int(total_vol):,}</span> mm³", unsafe_allow_html=True)
    if b2.button("Close", key="enc_close"):
        st.rerun()

@st.dialog("Wiring + Accessories", width="large")
def show_wiring_accessories():
    st.markdown("<div class='big-font'>Wiring + Accessories</div>", unsafe_allow_html=True)

    # Predefined items
    PREDEFINED_ITEMS = [
        (35, 350), (25, 250), (16, 170), (10, 110),
        (6, 60),   (4, 40),   (2.5, 30), (1, 15)
    ]

    # Initialize session state
    if "wiring_rows" not in st.session_state:
        st.session_state.wiring_rows = [
            {"size": str(size), "rate": str(rate), "qty": "", "total": 0.0}
            for size, rate in PREDEFINED_ITEMS
        ]
        st.session_state.wiring_rows.append({"size": "", "rate": "", "qty": "", "total": 0.0})

    def add_new_row():
        st.session_state.wiring_rows.append({"size": "", "rate": "", "qty": "", "total": 0.0})

    # Auto-add row when last qty is filled
    if st.session_state.wiring_rows and st.session_state.wiring_rows[-1]["qty"].strip():
        if len(st.session_state.wiring_rows) < len(PREDEFINED_ITEMS) + 10:
            add_new_row()

    # Header
    h1, h2, h3, h4 = st.columns([2, 2, 2, 2])
    for col, text in zip([h1, h2, h3, h4], ["SIZE (sq.mm)", "RATE (₹)", "QTY", "TOTAL (₹)"]):
        col.markdown(f"<div class='header-blue'>{text}</div>", unsafe_allow_html=True)

    total_grand = 0.0

    for idx, row in enumerate(st.session_state.wiring_rows):
        cols = st.columns([2, 2, 2, 2])
        with st.container():
            if idx % 2 == 0:
                st.markdown("<div class='row-even'>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='row-odd'>", unsafe_allow_html=True)

            with cols[0]:
                size = st.text_input("size", value=row["size"], key=f"w_size_{idx}", label_visibility="collapsed")
                st.session_state.wiring_rows[idx]["size"] = size

            with cols[1]:
                rate = st.text_input("rate", value=row["rate"], key=f"w_rate_{idx}", label_visibility="collapsed")
                st.session_state.wiring_rows[idx]["rate"] = rate

            with cols[2]:
                qty = st.text_input("qty", value=row["qty"], key=f"w_qty_{idx}", label_visibility="collapsed", placeholder="0")
                st.session_state.wiring_rows[idx]["qty"] = qty

            # Calculate row total
            try:
                q = float(qty or 0)
                r = float(rate or 0)
                row_total = q * r
                total_grand += row_total
            except:
                row_total = 0.0

            with cols[3]:
                st.markdown(f"""
                    <div style='background:#e6f7ff; padding:12px; border-radius:6px; text-align:right;
                                font-weight:bold; color:#0f4d7d; border:1px solid #0f4d7d; height:56px;
                                display:flex; align-items:center; justify-content:flex-end;'>
                        ₹ {row_total:,.2f}
                    </div>
                """, unsafe_allow_html=True)

            if idx % 2 == 0:
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown("</div>", unsafe_allow_html=True)

    # Grand Total
    st.markdown(f"<div class='total-box'>GRAND TOTAL: ₹ {total_grand:,.2f}</div>", unsafe_allow_html=True)

    # Buttons
    b1, b2, b3 = st.columns([2, 2, 6])
    with b1:
        if st.button("Recalculate", use_container_width=True):
            st.success("Recalculated!")
            st.rerun()
    with b2:
        if st.button("Add Row", use_container_width=True):
            add_new_row()
            st.rerun()

    # Save total to main session
    st.session_state.wiring_total = total_grand
@st.dialog("BUSBAR COSTING CALCULATOR", width="large")
def show_busbar_calculator():
    st.markdown("<h2 style='text-align:center;color:#003366;'>BUSBAR CALCULATOR</h2>", unsafe_allow_html=True)

    if 'busbar_options' not in st.session_state:
        st.session_state.busbar_options = [
            "VERTICAL-INCOMER FOR B/C", "VERTICAL-O/G FOR Ph1", "VERTICAL-O/G FOR Ph2",
            "VERTICAL-APFC O/G", "VERTICAL-INCOMER", "VERTICAL-OUTGOING",
            "CONTROL BUS", "EARTH"
        ]
    if 'busbar_sections' not in st.session_state:
        st.session_state.busbar_sections = []
    if 'busbar_density' not in st.session_state:
        st.session_state.busbar_density = 0.0
    if 'busbar_grand_total' not in st.session_state:
        st.session_state.busbar_grand_total = 0.0

    busbar_data = {
        "VERTICAL-INCOMER FOR B/C": [["25","10","1","","3","","1600","1","","","400",""]],
        "VERTICAL-O/G FOR Ph1": [["30","5","2","","1","1","1800","2","","","500",""]],
        "VERTICAL-O/G FOR Ph2": [["40","5","2","","2","1","1500","1","","","520",""]],
        "VERTICAL-APFC O/G": [["50","10","2","","1","1","1800","1","","","600",""]],
        "VERTICAL-INCOMER": [["20","10","1","","1","0","1600","1","","","450",""]],
        "VERTICAL-OUTGOING": [["20","10","1","","0","1","1600","1","","","450",""]],
        "CONTROL BUS": [["10","5","1","","1","1","1600","2","","","300",""]],
        "EARTH": [["16","5","1","","0","1","1600","1","","","200",""]]
    }

    headers = ["L","W","RUN","WEIGHT (KG/M)","PHASE","NEUTRAL",
               "PANEL LENGTH","NO. OF HORI","TOTAL LENGTH (Mts)",
               "WEIGHT OF THE BUS BAR","BUS BAR PRICE","GRAND PRICE"]

    def add_section(title, data):
        if any(s['title'] == title for s in st.session_state.busbar_sections):
            st.toast("Already added!", icon="Warning")
            return
        df = pd.DataFrame(data, columns=headers)
        st.session_state.busbar_sections.append({'title': title, 'df': df})

    def calculate_all():
        density = st.session_state.busbar_density
        if density == 0:
            st.error("Select material!")
            return
        for sec in st.session_state.busbar_sections:
            df = sec['df']
            for i in df.index:
                try:
                    L = float(df.at[i,'L'] or 0)
                    W = float(df.at[i,'W'] or 0)
                    run = float(df.at[i,'RUN'] or 0)
                    wt_per_m = L * W * run * density
                    df.at[i,'WEIGHT (KG/M)'] = f"{wt_per_m:.4f}"

                    phase = int(df.at[i,'PHASE'] or 0)
                    neutral = int(df.at[i,'NEUTRAL'] or 0)
                    plen = float(df.at[i,'PANEL LENGTH'] or 0)
                    hori = float(df.at[i,'NO. OF HORI'] or 0)
                    total_len = (plen / 1000) * hori * (phase + neutral)
                    df.at[i,'TOTAL LENGTH (Mts)'] = f"{total_len:.2f}"

                    total_wt = total_len * wt_per_m
                    df.at[i,'WEIGHT OF THE BUS BAR'] = f"{total_wt:.2f}"

                    price = float(df.at[i,'BUS BAR PRICE'] or 0)
                    grand = total_wt * price
                    df.at[i,'GRAND PRICE'] = f"{grand:,.2f}"
                except:
                    df.at[i,'GRAND PRICE'] = "Error"
        update_grand_total()

    def update_grand_total():
        total = 0.0
        for sec in st.session_state.busbar_sections:
            for val in sec['df']['GRAND PRICE']:
                try:
                    total += float(str(val).replace(",",""))
                except: pass
        st.session_state.busbar_grand_total = total

    c1,c2,c3,c4,c5 = st.columns([3,1.2,2.5,1.2,2])
    with c1:
        sel = st.selectbox("Select Type", ["Select"] + st.session_state.busbar_options)
    with c2:
        if st.button("Add Selected", use_container_width=True):
            if sel != "Select":
                add_section(sel, busbar_data.get(sel, [["" for _ in headers]]))
                st.rerun()
    with c3:
        name = st.text_input("Custom Name")
    with c4:
        if st.button("Add Custom", use_container_width=True):
            if name.strip():
                n = name.strip().upper()
                if n not in st.session_state.busbar_options:
                    st.session_state.busbar_options.append(n)
                add_section(n, [["" for _ in headers]])
                st.rerun()
    with c5:
        mat = st.selectbox("Material", ["Aluminum = 0.0027", "Copper = 0.0089"])
        st.session_state.busbar_density = 0.0027 if "Aluminum" in mat else 0.0089

    st.markdown("---")

    if st.session_state.busbar_sections:
        for i, sec in enumerate(st.session_state.busbar_sections):
            with st.expander(f"**{sec['title']}**", expanded=True):
                if st.button("Delete", key=f"delb_{i}"):
                    del st.session_state.busbar_sections[i]
                    st.rerun()
                edited = st.data_editor(sec['df'], num_rows="dynamic", use_container_width=True,
                    column_config={
                        "L": st.column_config.NumberColumn("L(mm)"),
                        "W": st.column_config.NumberColumn("W(mm)"),
                        "RUN": st.column_config.NumberColumn("RUN"),
                        "PHASE": st.column_config.NumberColumn("Phase"),
                        "NEUTRAL": st.column_config.NumberColumn("Neutral"),
                        "PANEL LENGTH": st.column_config.NumberColumn("Panel Len(mm)"),
                        "NO. OF HORI": st.column_config.NumberColumn("Hori"),
                        "BUS BAR PRICE": st.column_config.NumberColumn("Price/kg"),
                        "WEIGHT (KG/M)": st.column_config.TextColumn(disabled=True),
                        "TOTAL LENGTH (Mts)": st.column_config.TextColumn(disabled=True),
                        "WEIGHT OF THE BUS BAR": st.column_config.TextColumn(disabled=True),
                        "GRAND PRICE": st.column_config.TextColumn(disabled=True),
                    },
                    hide_index=False, key=f"bus_{i}")
                sec['df'] = edited
    else:
        st.info("Add busbar sections above")

    b1,b2,b3 = st.columns([2,2,3])
    with b1:
        if st.button("CALCULATE ALL", type="primary", use_container_width=True):
            calculate_all()
            st.rerun()
    with b2:
        if st.button("REFRESH TOTAL", use_container_width=True):
            update_grand_total()
            st.rerun()
    with b3:
        st.markdown(f"<div style='background:#28a745;color:white;padding:20px;border-radius:12px;text-align:center;font-size:28px;font-weight:bold;'>BUSBAR TOTAL: ₹ {st.session_state.busbar_grand_total:,.2f}</div>", unsafe_allow_html=True)

# Helper: Add Section Header
def add_section(name):
    name = name.upper()
    if name not in [s.upper() for s in st.session_state.items_df["section"].dropna().astype(str)]:
        header = pd.DataFrame([dict.fromkeys(COLUMNS, None)])
        header["section"] = name
        header["disc_gross_price"] = 0
        header["lp_gross_price"] = 0
        st.session_state.items_df = pd.concat([st.session_state.items_df, header], ignore_index=True)
        st.rerun()
    else:
        st.toast(f"Section '{name}' already exists!")

# ========================= LAYOUT =========================
left_col, right_col = st.columns([1.8, 2.2])

with left_col:
    # Customer Details
    with st.container(border=True):
        st.markdown("<div class='section-title'>Customer Details</div>", unsafe_allow_html=True)
        def update_customer():
            name = st.session_state.cust_name
            if name and not customers_df.empty:
                row = customers_df[customers_df['name'] == name]
                if not row.empty:
                    st.session_state.phone = row.iloc[0]['phone']
                    st.session_state.shipping = row.iloc[0]['address']
        st.selectbox("Customer Name", [""] + sorted(customers_df["name"].dropna().unique().tolist()),
                     key="cust_name", on_change=update_customer)
        st.text_input("Phone", key="phone", placeholder="Auto-filled or enter manually")
        st.text_area("Shipping Address", key="shipping", height=100)
        st.date_input("Quotation Date", value=date.today(), key="quotation_date")
        st.date_input("Delivery Date", value=date.today(), key="delivery_date")

    # Quick Add Sections
    st.markdown("<div class='section-title'>Quick Add Sections</div>", unsafe_allow_html=True)
    with st.container(border=True):
        qcol1, qcol2 = st.columns(2)
        with qcol1:
            if st.button("Enclosure Fabrication", use_container_width=True, type="secondary"):
                show_enclosure_fabrication()
            if st.button("Wiring + Accessories", use_container_width=True, type="secondary"):
                show_wiring_accessories()
        with qcol2:
            if st.button("Transport/Labour", use_container_width=True, type="secondary"):
                add_section("TRANSPORT/LABOUR")
            if st.button("Busbar Calculator", use_container_width=True, type="primary"):
                show_busbar_calculator()

    # COMBINED: Actions + Summary (Exactly like your screenshot)
    st.markdown("<div class='section-title'>Actions & Summary</div>", unsafe_allow_html=True)
    with st.container(border=True):
        # Calculate totals
        df = st.session_state.items_df
        lp_total = df["lp_gross_price"].sum() if not df.empty and "lp_gross_price" in df.columns else 0
        net_total = df["disc_gross_price"].sum() if not df.empty and "disc_gross_price" in df.columns else 0

        # Top row: Totals
        tcol1, tcol2 = st.columns(2)
        with tcol1:
            st.markdown("**List Price Total**")
            st.markdown(f"<div class='price-box'>₹ {lp_total:,.0f}</div>", unsafe_allow_html=True)
        with tcol2:
            st.markdown("**Net Amount (After Discount)**")
            st.markdown(f"<div class='price-box'>₹ {net_total:,.0f}</div>", unsafe_allow_html=True)

        # Bottom row: Action Buttons
        st.markdown("<br>", unsafe_allow_html=True)
        act1, act2, act3, act4 = st.columns(4)
        with act1:
            st.button("GENERATE PDF", type="primary", use_container_width=True)
        with act2:
            st.button("SAVE QUOTATION", use_container_width=True)
        with act3:
            if st.button("CLEAR ALL", use_container_width=True):
                st.session_state.items_df = pd.DataFrame(columns=COLUMNS)
                st.success("All items cleared!")
                st.rerun()
        with act4:
            st.button("EXIT", use_container_width=True)

# ========================= RIGHT COLUMN: ADD PRODUCTS (UNCHANGED) =========================
with right_col:
    with st.container(border=True):
        st.markdown("<div class='section-title'>Add Products</div>", unsafe_allow_html=True)
        # ... (your full product adding code - 100% unchanged)

        c1, c2 = st.columns([4, 1])
        with c1:
            selected_category = st.selectbox("Select Category", category_list, key="sel_category")
        with c2:
            if st.button("+ Add", use_container_width=True):
                st.session_state.show_add_category = True

        if st.session_state.show_add_category:
            with st.container(border=True):
                st.markdown("### Add New Category")
                with st.form("new_cat_form"):
                    new_name = st.text_input("Category Name").strip()
                    save_col, cancel_col = st.columns(2)
                    if save_col.form_submit_button("Save", type="primary"):
                        if new_name:
                            try:
                                with get_connection() as con:
                                    cur = con.cursor()
                                    cur.execute("INSERT INTO Categories (CategoryName) VALUES (?)", (new_name,))
                                    con.commit()
                                st.success(f"Added: {new_name}")
                                st.session_state.show_add_category = False
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                    if cancel_col.form_submit_button("Cancel"):
                        st.session_state.show_add_category = False
                        st.rerun()

        inv = inventory_df if not has_category or selected_category == "General" else \
              inventory_df[inventory_df["CategoryName"] == selected_category]

        desc_opts = [""] + sorted(inv["Description"].dropna().unique().tolist())
        sel_desc = st.selectbox("Description", desc_opts, key="desc")
        sel_make = sel_material = sel_price = ratings = discount = avail_qty = None

        if sel_desc:
            f1 = inv[inv["Description"] == sel_desc]
            make_opts = [""] + sorted(f1["Make"].dropna().unique().tolist())
            sel_make = st.selectbox("Make", make_opts, key="make")

        if sel_make:
            f2 = f1[f1["Make"] == sel_make]
            mat_opts = [""] + sorted(f2["MaterialName"].dropna().unique().tolist())
            sel_material = st.selectbox("Material", mat_opts, key="mat")

        if sel_material:
            f3 = f2[f2["MaterialName"] == sel_material]
            prices = sorted(f3["ListPrice"].dropna().unique())
            if len(prices) == 1:
                sel_price = prices[0]
                st.number_input("List Price", value=float(sel_price), disabled=True)
            else:
                sel_price = st.selectbox("List Price", [0] + prices, format_func=lambda x: f"₹{x:,.2f}" if x > 0 else "Select")

            if sel_price and sel_price > 0:
                item = f3[f3["ListPrice"] == sel_price].iloc[0]
                ratings = item.get("Ratings", "")
                avail_qty = item.get("TotalQuantity", 0)
                discount = item.get("Discount", 0) or 0
                st.info(f"Available: {avail_qty} | Rating: {ratings} | Discount: {discount}%")

        qty = st.number_input("Quantity", min_value=1, value=1, step=1)

        if st.button("ADD PRODUCT", type="primary", use_container_width=True):
            if not all([sel_desc, sel_make, sel_material, sel_price]):
                st.error("Please fill all fields!")
            else:
                disc_unit = sel_price * (1 - discount/100)
                section = selected_category.upper()
                dup_check = st.session_state.items_df[
                    (st.session_state.items_df["description"] == sel_desc) &
                    (st.session_state.items_df["make"] == sel_make) &
                    (st.session_state.items_df["material"] == sel_material) &
                    (st.session_state.items_df["list_price"] == sel_price)
                ]
                if not dup_check.empty:
                    st.warning("This item is already added!")
                else:
                    new_row = pd.DataFrame([{
                        "section": section,
                        "description": sel_desc,
                        "ratings": ratings,
                        "make": sel_make,
                        "material": sel_material,
                        "quantity": qty,
                        "net_qty": qty,
                        "list_price": sel_price,
                        "discount": discount,
                        "disc_unit_price": disc_unit,
                        "disc_gross_price": disc_unit * qty,
                        "lp_gross_price": sel_price * qty
                    }])
                    st.session_state.items_df = pd.concat([st.session_state.items_df, new_row], ignore_index=True)
                    st.success(f"Added: {qty} × {sel_desc}")
                    st.rerun()

        if st.button(f"Add Section → {selected_category.upper()}", type="secondary", use_container_width=True):
            add_section(selected_category.upper())

# ========================= FINAL QUOTATION TABLE (UNCHANGED) =========================
st.markdown("### Final Quotation Preview", unsafe_allow_html=True)

if not st.session_state.items_df.empty:
    df = st.session_state.items_df.copy()
    display_rows = []
    for section, group in df.groupby("section", sort=False):
        if pd.notna(section):
            header_row = {col: "" for col in df.columns}
            header_row["description"] = f"**{section}**"
            display_rows.append(header_row)
            for _, row in group.iterrows():
                if pd.notna(row["description"]) and not str(row["description"]).startswith("**"):
                    display_rows.append({
                        "description": row["description"],
                        "ratings": row["ratings"] or "",
                        "make": row["make"] or "",
                        "material": row["material"] or "",
                        "quantity": int(row["quantity"]) if pd.notna(row["quantity"]) else "",
                        "net_qty": int(row["net_qty"]) if pd.notna(row["net_qty"]) else "",
                        "list_price": f"₹{row['list_price']:,.2f}" if pd.notna(row['list_price']) else "",
                        "disc_unit_price": f"₹{row['disc_unit_price']:,.2f}" if pd.notna(row['disc_unit_price']) else "",
                        "disc_gross_price": f"₹{row['disc_gross_price']:,.2f}" if pd.notna(row['disc_gross_price']) else "",
                        "lp_gross_price": f"₹{row['lp_gross_price']:,.2f}" if pd.notna(row['lp_gross_price']) else ""
                    })
    disp_df = pd.DataFrame(display_rows)
    disp = disp_df[["description", "ratings", "make", "material", "quantity", "net_qty",
                    "list_price", "disc_unit_price", "disc_gross_price", "lp_gross_price"]].copy()

    def style_table(row):
        if str(row["description"]).startswith("**"):
            return ['background-color:#e3f2fd !important; font-weight:bold; font-size:20px; text-align:center; color:#1565c0; border-top:4px solid #42a5f5; height:50px'] * len(row)
        else:
            styles = ['text-align:right' if col in ["quantity","net_qty","list_price","disc_unit_price","disc_gross_price","lp_gross_price"] else 'text-align:left' for col in row.index]
            return styles

    st.dataframe(disp.style.apply(style_table, axis=1), use_container_width=True, hide_index=True)
else:
    st.info("No products added yet. Start by selecting a category and adding items.")

st.caption("Quotation Generator • Professional Layout • Ready for PDF")