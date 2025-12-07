# quotation_dashboard.py (100% FIXED - NO DUPLICATE ID ERRORS)
import streamlit as st
import pandas as pd
import pyodbc
from datetime import date

st.set_page_config(page_title="Quotation", layout="wide")

# Database connection
@st.cache_resource(show_spinner=False)
def get_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=PRATIKSHARAUT\\SQLEXPRESS;"
        "DATABASE=version1;"
        "Trusted_Connection=yes;"
    )

# Load data
@st.cache_data
def load_customers():
    try:
        with get_connection() as con:
            return pd.read_sql("SELECT name, phone, address FROM customers ORDER BY name", con)
    except:
        return pd.DataFrame(columns=["name", "phone", "address"])

@st.cache_data
def load_categories():
    try:
        with get_connection() as con:
            df = pd.read_sql("SELECT DISTINCT CategoryName FROM categories", con)
            return sorted(df['CategoryName'].dropna().unique())
    except:
        return []

@st.cache_data
def load_inventory():
    try:
        with get_connection() as con:
            return pd.read_sql("""
                SELECT Description, Ratings, Make, MaterialName,
                       TotalQuantity, Discount, ListPrice
                FROM inventory
                ORDER BY Description
            """, con)
    except:
        return pd.DataFrame(columns=["Description", "Ratings", "Make", "MaterialName",
                                     "TotalQuantity", "Discount", "ListPrice"])

def update_customer():
    selected = st.session_state.select_cust
    if selected:
        row = customers_df[customers_df['name'] == selected].iloc[0]
        st.session_state.cust_name = selected
        st.session_state.shipping = row['address']
        st.session_state.phone = row['phone']
        st.rerun()

# Load data
customers_df = load_customers()
categories = load_categories()
inventory_df = load_inventory()

# CSS
st.markdown("""
<style>
    :root{--bg-dark:#1f3b4a;--panel-blue:#2f5362;--accent:#69a4c1;--text-light:#ffffff;--table-header:#2b3f4a;}
    .top-bar{background:var(--bg-dark);color:var(--text-light);padding:10px 20px;border-radius:4px;margin-bottom:12px;text-align:center;}
    .top-bar h1{font-size:22px;margin:0;font-weight:700;}
    .cust-panel{background:linear-gradient(180deg,var(--panel-blue),#2a4f5d);padding:14px;border-radius:6px;color:var(--text-light);}
    .table-header{background:var(--table-header);color:white;padding:8px 12px;border-radius:4px;font-weight:600;margin-top:12px;}
    .footer-panel{background:var(--bg-dark);color:var(--text-light);padding:10px;border-radius:6px;}
    .big-font {font-size: 28px !important; font-weight: bold; color: #1e3d59;}
    .header-blue {background:#4a90e2 !important; color:white !important; padding:12px; border-radius:8px; text-align:center; font-weight:bold; font-size:16px;}
    .spec-cell {background:#e3f2fd; padding:14px; border-radius:6px; text-align:center; font-weight:bold; font-size:16px; color:#000000 !important; border-left: 4px solid #1976d2;}
    .calc-cell {background:#e8e8e8; padding:14px; border-radius:6px; text-align:right; font-weight:bold; font-size:16px; color:#d35400;}
    .total-box {background:#2c3e50; color:white; padding:18px; border-radius:12px; text-align:center; font-size:26px; font-weight:bold;}
    .section-title {font-size:24px; font-weight:bold; color:#1e3d59; margin-top:40px; margin-bottom:15px; padding-bottom:8px; border-bottom: 3px solid #4a90e2;}
    .stButton>button {background:#0f4d7d; color:white; font-weight:bold; padding:14px 32px; border-radius:10px; font-size:16px; border: none;}
    .stTextInput>div>div>input, .stNumberInput>div>div>input {font-size:16px !important; padding:12px !important; border-radius:8px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="top-bar"><h1>Quotation</h1></div>', unsafe_allow_html=True)

# Customer Section
with st.container():
    st.markdown('<div class="cust-panel">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2,1,1.2])
    with c1:
        st.text_input("Customer Name", value=st.session_state.get('cust_name',''), key="cust_name")
        if st.session_state.get('cust_name','') and len(st.session_state.cust_name) >= 1:
            opts = customers_df[customers_df["name"].str.lower().str.startswith(st.session_state.cust_name.lower())]["name"].tolist()
            if opts:
                st.selectbox("Select customer", opts, key="select_cust", on_change=update_customer)
        st.text_input("Shipping Address", value=st.session_state.get('shipping',''), key="shipping")
    with c2:
        st.text_input("Phone No.", value=st.session_state.get('phone',''), key="phone")
        st.date_input("Quotation Date", value=date.today(), key="quotation_date")
    with c3:
        st.text_input("Quotation No.", value="", key="quotation_no")
        st.date_input("Delivery Date", value=date.today(), key="delivery_date")
    st.markdown('</div>', unsafe_allow_html=True)
st.write("")

# Columns definition
COLUMNS = ["section","description","ratings","cat_no","make","quantity","net_qty",
           "list_price","discount","disc_unit_price","disc_gross_price","lp_gross_price"]

if "items_df" not in st.session_state:
    st.session_state.items_df = pd.DataFrame(columns=COLUMNS)

# Add Section Heading
st.subheader("Add Section Heading")
if categories:
    col1, col2 = st.columns([3,1])
    with col1:
        cat = st.selectbox("Category", categories, key="cat_sel")
    with col2:
        if st.button("Add Section Heading"):
            new_row = pd.DataFrame([{
                "section": "", "description": f"--- {cat.upper()} ---", "ratings": "", "cat_no": "", "make": "",
                "quantity": 0, "net_qty": 0, "list_price": 0.0, "discount": 0.0,
                "disc_unit_price": None, "disc_gross_price": None, "lp_gross_price": None
            }])
            st.session_state.items_df = pd.concat([st.session_state.items_df, new_row], ignore_index=True)
            st.rerun()

# Add Product
st.subheader("Add Product")
if not inventory_df.empty:
    col_desc, col_ratings = st.columns(2)
    with col_desc:
        desc_options = [""] + sorted(inventory_df["Description"].dropna().unique())
        selected_description = st.selectbox("Select Description", desc_options, index=0, key="sel_desc")

    if selected_description:
        filtered = inventory_df[inventory_df["Description"] == selected_description]
        with col_ratings:
            ratings_options = [""] + sorted(filtered["Ratings"].dropna().unique())
            selected_ratings = st.selectbox("Select Ratings", ratings_options, index=0, key="sel_rating")

        if selected_ratings:
            filtered = filtered[filtered["Ratings"] == selected_ratings]
            col_make, col_mat = st.columns(2)
            with col_make:
                make_options = [""] + sorted(filtered["Make"].dropna().unique())
                selected_make = st.selectbox("Select Make", make_options, index=0, key="sel_make")
            with col_mat:
                mat_options = [""] + sorted(filtered["MaterialName"].dropna().unique())
                selected_material = st.selectbox("Select MaterialName", mat_options, index=0, key="sel_mat")

            if selected_make and selected_material:
                filtered = filtered[(filtered["Make"] == selected_make) & (filtered["MaterialName"] == selected_material)]
                if not filtered.empty:
                    row = filtered.iloc[0]
                    st.info(f"Available Stock: {int(row['TotalQuantity'])}")

                    col_qty, col_disc = st.columns(2)
                    with col_qty:
                        qty = st.number_input("Quantity", min_value=1, value=1, step=1, key="add_qty")
                    with col_disc:
                        disc = st.number_input("Discount (%)", min_value=0.0, max_value=100.0, value=float(row["Discount"]), step=0.1, key="add_disc")

                    cash_discount = st.number_input("Cash Discount (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, key="cash_disc")

                    if st.button("Add Product"):
                        if qty > row["TotalQuantity"]:
                            st.error("Not enough stock!")
                        else:
                            lp_gross = float(row["ListPrice"]) * qty
                            net_after_cash_disc = lp_gross * (1 - cash_discount / 100)

                            new_row = pd.DataFrame([{
                                "section":"", "description":selected_description, "ratings":selected_ratings,
                                "cat_no":selected_material, "make":selected_make,
                                "quantity":qty, "net_qty":qty, "list_price":float(row["ListPrice"]),
                                "discount":disc,
                                "disc_unit_price":0.0,
                                "disc_gross_price":net_after_cash_disc,
                                "lp_gross_price":lp_gross
                            }])
                            st.session_state.items_df = pd.concat([st.session_state.items_df, new_row], ignore_index=True)
                            st.success("Product added!")
                            st.rerun()

# Calculation function
def apply_calculations(df):
    df = df.copy()
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = 0.0 if col in ["list_price","net_qty","quantity","discount","disc_unit_price","disc_gross_price","lp_gross_price"] else ""
    numeric_cols = ["list_price", "net_qty", "quantity", "discount", "disc_gross_price", "lp_gross_price"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    item_mask = ~df["description"].astype(str).str.startswith("---")
    df.loc[item_mask, "lp_gross_price"] = df["list_price"] * df["net_qty"]
    df["disc_gross_price"] = df["disc_gross_price"].round(2)
    df["lp_gross_price"] = df["lp_gross_price"].round(2)
    df.loc[~item_mask, ["disc_gross_price", "lp_gross_price"]] = None
    return df

display_df = apply_calculations(st.session_state.items_df)

# Column config
column_config = {
    "section": st.column_config.SelectboxColumn("Section", options=categories + [""], required=False),
    "quantity": st.column_config.NumberColumn("Qty", format="%.0f"),
    "net_qty": st.column_config.NumberColumn("Net Qty", format="%.0f"),
    "list_price": st.column_config.NumberColumn("List Price", format="₹ %.2f"),
    "discount": st.column_config.NumberColumn("Disc %", format="%.2f%%"),
    "disc_unit_price": st.column_config.NumberColumn("Unit After Disc", format="₹ %.2f", disabled=True),
    "disc_gross_price": st.column_config.NumberColumn("Gross After Disc", format="₹ %.2f", disabled=True),
    "lp_gross_price": st.column_config.NumberColumn("LP Gross", format="₹ %.2f", disabled=True),
}

st.markdown('<div class="table-header">DESCRIPTION & ITEMS</div>', unsafe_allow_html=True)

with st.expander("Open items table (click to expand)", expanded=True):
    edited = st.data_editor(
        display_df,
        num_rows="dynamic",
        column_config=column_config,
        use_container_width=True,
        hide_index=False,
        key="main_editor"
    )
    st.session_state.items_df = apply_calculations(edited)

# Final totals
df = st.session_state.items_df
item_rows = df[~df["description"].astype(str).str.startswith("---")] if not df.empty and "description" in df.columns else pd.DataFrame()
total_lp = float(item_rows["lp_gross_price"].sum() if not item_rows.empty else 0.0)
total_disc_gross = float(item_rows["disc_gross_price"].sum() if not item_rows.empty else 0.0)

# ====================== ENCLOSURE FABRICATION DIALOG (FIXED KEYS) ======================
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

        cols[1].markdown(f"<div class='spec-cell' style='background:{bg}'><strong>{row['spec']}</strong></div>", unsafe_allow_html=True)

        mm = cols[2].number_input("", value=row["mm"], step=0.01, format="%.3f", key=f"enc_mm_{i}", label_visibility="collapsed")
        L = cols[3].number_input("", value=row["L"], step=1.0, key=f"enc_L_{i}", label_visibility="collapsed")
        W = cols[4].number_input("", value=row["W"], step=1.0, key=f"enc_W_{i}", label_visibility="collapsed")
        kg = cols[5].number_input("", value=row["kg"], step=0.1, format="%.2f", key=f"enc_kg_{i}", label_visibility="collapsed")

        st.session_state.enc_rows[i].update({"mm": mm, "L": L, "W": W, "kg": kg})
        area = L * W
        calc = round(mm * area * 0.00000785, 2)
        kg_per = kg / area if area > 0 else 0.0
        if inc: total_weight += calc

        cols[6].markdown(f"<div class='calc-cell'>{calc:.2f}</div>", unsafe_allow_html=True)
        cols[7].markdown(f"<div class='calc-cell'>{kg_per:.10f}</div>", unsafe_allow_html=True)

    st.markdown("---")
    t1, t2 = st.columns([6, 4])
    t1.markdown("**Enclosure Total:**")
    t2.markdown(f"<div class='total-box'>₹ {total_weight:,.2f}</div>", unsafe_allow_html=True)

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
        dc[4].markdown(f"<div class='calc-cell'>{int(vol):,}</div>", unsafe_allow_html=True)

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
            st.session_state.enc_percent = {"applied": True, "base": base, "delta": delta, "final": final, "text": txt+"%" if not txt.endswith("%") else txt}
            st.success(f"Applied {st.session_state.enc_percent['text']}!")
        except:
            st.error("Invalid input")

    res = st.session_state.enc_percent
    if res["applied"]:
        pc3.metric("Δ", f"{res['delta']:+.4f}")
        pc4.metric("Final", f"{res['final']:.4f}")
        kc2.metric("Base", f"{res['base']:.4f}")
        kc3.metric("Δ", f"{res['delta']:+.4f}")
        kc4.metric("Final", f"{res['final']:.4f}")

    b1, b2 = st.columns(2)
    if b1.button("Total Volume", key="enc_total_vol"):
        st.success(f"Total Volume: {int(total_vol):,} mm³")
    if b2.button("Close", key="enc_close"):
        st.rerun()

# ====================== WIRING + ACCESSORIES DIALOG ======================
@st.dialog("Wiring + Accessories", width="medium")
def show_wiring_accessories():
    st.markdown("### Wiring + Accessories")
    wiring_data = {"SIZE": [15,25,35,50,70,95,120,150,185,240],
                   "RATE": [150.0,250.0,370.0,510.0,710.0,950.0,1250.0,1600.0,2000.0,2600.0],
                   "QTY": [0]*10, "TOTAL": [0.0]*10}
    df_w = pd.DataFrame(wiring_data)
    edited = st.data_editor(df_w, column_config={
        "SIZE": st.column_config.NumberColumn("Size", disabled=True),
        "RATE": st.column_config.NumberColumn("Rate (₹)", format="%.2f"),
        "QTY": st.column_config.NumberColumn("Qty", min_value=0, step=1, format="%d"),
        "TOTAL": st.column_config.NumberColumn("Total (₹)", format="%.2f", disabled=True),
    }, use_container_width=True, hide_index=True, num_rows="fixed", key="wiring_editor")
    edited["TOTAL"] = (edited["RATE"] * edited["QTY"]).round(2)
    st.dataframe(edited, use_container_width=True, hide_index=True)
    st.markdown(f"**Grand Total: ₹ {edited['TOTAL'].sum():,.2f}**")
    if st.button("Close", key="wiring_close"):
        st.rerun()

# Footer Buttons
colA, colB, colC, colD = st.columns([1.8,1,1,1.2])
with colA:
    st.markdown('<div class="footer-panel">', unsafe_allow_html=True)
    if st.button("ENCLOSURE FABRICATION"):
        show_enclosure_fabrication()
    if st.button("WIRING + ACCESSORIES"):
        show_wiring_accessories()
    for label in ["BUS BAR", "TRANSPORTATION", "LABOUR"]:
        st.button(label, key=f"btn_{label.lower().replace(' ', '_')}")
    st.markdown('</div>', unsafe_allow_html=True)

with colB:
    st.markdown("**LP GROSS TOTAL:**")
    st.text_input("", value=f"₹ {total_lp:,.2f}", disabled=True, key="final_lp_total", label_visibility="collapsed")
with colC:
    st.markdown("**NET AFTER DISCOUNT:**")
    st.text_input("", value=f"₹ {total_disc_gross:,.2f}", disabled=True, key="final_net_total", label_visibility="collapsed")
with colD:
    st.button("GENERATE BILL", type="primary", key="gen_bill")
    st.button("SAVE", key="save_quot")
    st.button("CONFIRM", key="confirm_quot")
    st.button("CANCEL", key="cancel_quot")

# Final Summary
st.write("---")
st.markdown("### Final Summary")
if not df.empty:
    def highlight(r):
        return ['background:#FFFFE0; font-weight:bold; text-align:center'] * len(r) if str(r.description or "").startswith('---') else ['']*len(r)
    st.dataframe(df.style.apply(highlight, axis=1).format({
        "list_price":"₹ {:.2f}", "disc_gross_price":"₹ {:.2f}", "lp_gross_price":"₹ {:.2f}"
    }), use_container_width=True, hide_index=False)
    st.download_button("Download CSV", df.to_csv(index=False).encode('utf-8'), "quotation.csv", "text/csv", key="download_csv")
else:
    st.info("No items yet. Add products or sections to begin.")