import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="Property Preservation Rate Lookup", page_icon="📋", layout="wide")

# Custom CSS
st.markdown("""
<style>
   /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #e5e7eb;
        margin-bottom: 15px;
        width: fit-content; /* <--- This forces the white box to end exactly after the 3rd tab */
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        border-radius: 4px;
        margin-right: 5px;
        padding-left: 15px;
        padding-right: 15px;
        color: #4b5563 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #f0fdf4 !important;
        border-bottom: 3px solid #059669 !important;
        color: #065f46 !important;
        font-weight: bold;
    }

    /* Core UI Elements */
    .tier-1 { background-color: #d1fae5; color: #065f46; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 0.85em; }
    .tier-2 { background-color: #fef08a; color: #854d0e; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 0.85em; }
    .disclaimer { font-size: 0.9em; color: #6b7280; font-style: italic; margin-top: 20px; border-top: 1px solid #e5e7eb; padding-top: 10px; }
    .card { border: 1px solid #e5e7eb; border-radius: 8px; padding: 15px; margin-bottom: 15px; background-color: #f9fafb; box-shadow: 0 1px 2px rgba(0,0,0,0.05); color: #1f2937; }
    .waterfall-row { display: flex; align-items: center; margin-bottom: 8px; color: inherit; }    .waterfall-bar { height: 32px; border-radius: 4px; display: flex; align-items: center; padding: 0 10px; color: white; font-weight: bold; font-size: 0.9em; }
    .waterfall-label { width: 160px; font-size: 0.9em; color: inherit; font-weight: 500; }
    .waterfall-amount { width: 120px; text-align: right; font-weight: bold; font-size: 0.95em; margin-left: 10px; color: #9ca3af; }
    .waterfall-note { font-size: 0.85em; color: #64748b; font-style: italic; margin-top: 15px; line-height: 1.4; border-top: 1px dashed #e5e7eb; padding-top: 10px; }
    .gap-alert { background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 12px 16px; margin-top: 10px; color: #1f2937; }
    .gap-good { background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 12px 16px; margin-top: 10px; color: #1f2937; }
</style>
""", unsafe_allow_html=True)

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("Property_Pricing_Master.csv")
    
    # Rename HUD to HUD / FHA for clarity
    df['national'] = df['national'].replace({'HUD': 'HUD / FHA'})
    
    # Consolidation mapping for Grass Cuts
    def categorize_lot(size_str):
        if pd.isna(size_str) or str(size_str).strip() == "": return ""
        s = str(size_str).lower().replace('sf', '').strip()
        
        if any(x in s for x in ['1-10000', '1-5000', '5001-10000', '1-1000', '1001-5000', '5001-8000', '8001-10000', '1-10890', '10891-12000']):
            return "Standard Lot (<10,000 sf)"
        elif any(x in s for x in ['10001-20000', '10001-15000', '15001-20000', '12001-15000', '15001-18000', '18001-20000', '10001-10890']):
            return "Medium Lot (10k-20k sf)"
        elif any(x in s for x in ['20001', '30001', '15001-25000', '25001', '35001', '40001', '10001+', '1-15000']):
            return "Oversized Lot (20k+ sf)"
        return "Standard Lot (<10,000 sf)" # Catch-all
        
    df['lot_size'] = df['lot_size'].apply(categorize_lot)
    
    # Group by the clean parameters and take the max price to deduplicate rows
    df.fillna("N/A_TEMP", inplace=True)
    group_cols = [c for c in df.columns if c != 'price']
    df = df.groupby(group_cols, as_index=False)['price'].max()
    df.replace("N/A_TEMP", "", inplace=True)
    
    # Merge the "Phantom Variable" (Lot Size) directly into the Work Type
    df['display_work'] = df.apply(
        lambda x: f"{x['work_type']} ({x['lot_size']})" if str(x['lot_size']).strip() != "" else x['work_type'],
        axis=1
    )
    
    # Build work type categories for the category filter
    def categorize(wt):
        wt_lower = str(wt).lower()
        if 'grass' in wt_lower or 'lawn' in wt_lower or 'recut' in wt_lower or 'landscape' in wt_lower or 'shrub' in wt_lower or 'tree trim' in wt_lower:
            return "🌿 Grass & Lawn"
        elif 'winteriz' in wt_lower or 'dewint' in wt_lower or 'thaw' in wt_lower or 're-wint' in wt_lower or 'pressure test' in wt_lower:
            return "❄️ Winterization"
        elif 'lock' in wt_lower or 'padlock' in wt_lower or 'board' in wt_lower or 'secur' in wt_lower or 'slider' in wt_lower or 'slide bolt' in wt_lower or 'window lock' in wt_lower or 're-key' in wt_lower or 'rekey' in wt_lower or 'glaz' in wt_lower:
            return "🔒 Securing & Boarding"
        elif 'debris' in wt_lower or 'trash' in wt_lower or 'carpet' in wt_lower or 'removal' in wt_lower or 'vehicle' in wt_lower or 'tire' in wt_lower or 'appliance' in wt_lower or 'refriger' in wt_lower or 'hazard' in wt_lower or 'personal property' in wt_lower:
            return "🗑️ Debris & Removal"
        elif 'roof' in wt_lower or 'gutter' in wt_lower or 'chimney' in wt_lower or 'tarp' in wt_lower:
            return "🏠 Roof & Gutters"
        elif 'inspect' in wt_lower or 'occupancy' in wt_lower or 'verification' in wt_lower or 'photo' in wt_lower:
            return "🔍 Inspections"
        elif 'snow' in wt_lower:
            return "🌨️ Snow Removal"
        elif 'clean' in wt_lower or 'broom' in wt_lower or 'maid' in wt_lower or 'janitorial' in wt_lower or 'sales clean' in wt_lower:
            return "🧹 Cleaning"
        elif 'sump' in wt_lower or 'dehumid' in wt_lower or 'basement' in wt_lower or 'mold' in wt_lower or 'cap' in wt_lower or 'wire' in wt_lower or 'outlet' in wt_lower or 'electric' in wt_lower or 'well' in wt_lower or 'septic' in wt_lower:
            return "🔧 Utilities & Mechanicals"
        elif 'pool' in wt_lower or 'spa' in wt_lower or 'hot tub' in wt_lower:
            return "🏊 Pools & Spas"
        elif 'smoke' in wt_lower or 'co2' in wt_lower or 'co detector' in wt_lower or 'handrail' in wt_lower or 'step' in wt_lower or 'guard' in wt_lower or 'extermin' in wt_lower or 'pest' in wt_lower:
            return "⚠️ Health & Safety"
        elif 'door' in wt_lower or 'garage' in wt_lower or 'fence' in wt_lower or 'graffiti' in wt_lower or 'overhead' in wt_lower or 'pressure wash' in wt_lower or 'address' in wt_lower:
            return "🔨 Repairs & Maintenance"
        elif 'trip' in wt_lower or 'access' in wt_lower or 'eviction' in wt_lower or 'emergency' in wt_lower or 'allowance' in wt_lower or 'initial service' in wt_lower:
            return "🚗 Service Calls & Admin"
        else:
            return "📦 Other Services"

    df['category'] = df['display_work'].apply(categorize)
    return df

df = load_data()

# Custom Sorting for Investors (Feds first, then alphabetical)
def sort_investors(investors_list):
    top_tier = ["HUD / FHA", "Fannie Mae", "Freddie Mac", "VA"]
    found_top = [i for i in top_tier if i in investors_list]
    others = sorted([i for i in investors_list if i not in top_tier])
    return found_top + others

# Main Header
st.title("📋 Property Preservation Rate Lookup")
st.caption("Bidding & Allowable Calculator for Property Preservation Contractors")
st.markdown("")

# Tabs
tab1, tab2, tab3 = st.tabs(["🔎 Rate Lookup", "📊 National Comparison", "💰 Pricing Waterfall"])

# ========================
# TAB 1: RATE LOOKUP
# ========================
with tab1:
    
    # Row 1: Category + Investor
    col_cat, col_inv = st.columns(2)
    
    all_inv = df['national'].unique()
    all_categories = sorted(df['category'].unique())
    
    with col_cat:
        selected_categories = st.multiselect("Service Category", all_categories, placeholder="All categories")
    
    with col_inv:
        selected_investors = st.multiselect("Investor / National", sort_investors(all_inv), default=["HUD / FHA"])
    
    # Apply category filter first to narrow work types
    cat_filtered = df.copy()
    if selected_categories:
        cat_filtered = cat_filtered[cat_filtered['category'].isin(selected_categories)]
    if selected_investors:
        cat_filtered = cat_filtered[cat_filtered['national'].isin(selected_investors)]
    
    # Row 2: Work Type + State
    col_work, col_state = st.columns(2)
    
    valid_works = sorted(cat_filtered['display_work'].unique())
    
    with col_work:
        selected_works = st.multiselect("Work Type", valid_works, placeholder="Start typing to search...")
    
    # Narrow states based on all selections so far
    state_filtered = cat_filtered
    if selected_works:
        state_filtered = state_filtered[state_filtered['display_work'].isin(selected_works)]
    valid_states = sorted(state_filtered['state'].unique())
    
    with col_state:
        selected_states = st.multiselect("State", valid_states, placeholder="All States included by default")

    # Final filter
    result = df.copy()
    if selected_categories: result = result[result['category'].isin(selected_categories)]
    if selected_investors: result = result[result['national'].isin(selected_investors)]
    if selected_works: result = result[result['display_work'].isin(selected_works)]
    if selected_states: result = result[result['state'].isin(selected_states)]

    st.markdown("---")
    
    has_selection = selected_investors or selected_works or selected_states or selected_categories
    
    if not result.empty and has_selection:
        
        # Result count + controls row
        res_col1, res_col2, res_col3 = st.columns([2, 1, 1])
        with res_col1:
            st.markdown(f"**{len(result):,} results** matching your filters")
        with res_col2:
            mobile_view = st.toggle("📱 Mobile View", key="t1")
        with res_col3:
            # CSV download
            csv_export = result[['national', 'display_work', 'state', 'price', 'unit', 'tier', 'last_updated', 'notes', 'region_override']].copy()
            csv_export.rename(columns={'national':'Company','display_work':'Work Type','state':'State','price':'Rate','unit':'Unit','tier':'Tier','last_updated':'Date','notes':'Notes','region_override':'Zone'}, inplace=True)
            st.download_button("⬇️ Export CSV", csv_export.to_csv(index=False), "property_research_results.csv", "text/csv", use_container_width=True)
        
        if mobile_view:
            # Paginated card view for performance
            PAGE_SIZE = 25
            total_pages = max(1, (len(result) + PAGE_SIZE - 1) // PAGE_SIZE)
            
            if total_pages > 1:
                page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, key="t1_page")
            else:
                page = 1
            
            start_idx = (page - 1) * PAGE_SIZE
            end_idx = start_idx + PAGE_SIZE
            page_result = result.iloc[start_idx:end_idx]
            
            if total_pages > 1:
                st.caption(f"Showing {start_idx+1}-{min(end_idx, len(result))} of {len(result)}")
            
            for _, row in page_result.iterrows():
                status_icon = "✅ Active & Verified" if row['tier'] == 1 else "⚠️ Community Data"
                zone_tag = f" · 📍 {row['region_override']}" if str(row.get('region_override', '')).strip() else ""
                st.markdown(f"""
                <div class='card'>
                    <div style='color: #4b5563; font-size: 0.85em; text-transform: uppercase; font-weight: bold;'>{row['national']}{zone_tag}</div>
                    <div style='font-size: 1.1em; font-weight: bold; margin-bottom: 5px;'>{row['display_work']} — {row['state']}</div>
                    <div style='font-size: 1.4em; color: #059669; font-weight: bold; margin-bottom: 8px;'>${row['price']:,.2f} <span style='font-size: 0.7em; color: #6b7280;'>{row['unit']}</span></div>
                    <div style='font-size: 0.85em; margin-bottom: 10px; color: #4b5563;'><i>{status_icon} · {row['last_updated']}</i></div>
                    {"<div style='font-size: 0.9em; border-top: 1px solid #e5e7eb; padding-top: 8px;'>" + str(row['notes']) + "</div>" if str(row['notes']).strip() else ""}
                </div>
                """, unsafe_allow_html=True)
        else:
            # Dataframe UI for desktop
            display_res = result[['national', 'display_work', 'state', 'price', 'unit', 'tier', 'last_updated', 'notes', 'region_override']].copy()
            display_res['price'] = display_res['price'].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) and x != "" else "N/A")
            display_res['Status'] = display_res.apply(
                lambda r: f"✅ Verified ({r['last_updated']})" if r['tier'] == 1 else f"⚠️ Legacy ({r['last_updated']})", axis=1
            )
            # Add zone info for NRES etc
            display_res['Zone'] = display_res['region_override'].apply(lambda x: str(x) if str(x).strip() else "—")
            
            display_res = display_res[['national', 'display_work', 'state', 'Zone', 'price', 'unit', 'Status', 'notes']]
            display_res.rename(columns={
                'national': 'Company', 
                'display_work': 'Work Type', 
                'state': 'State', 
                'price': 'Rate', 
                'unit': 'Unit', 
                'notes': 'Notes'
            }, inplace=True)
            
            st.dataframe(
                display_res, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Notes": st.column_config.TextColumn(width="large")
                }
            )
    else:
        st.info("Select a category, company, work type, or state above to view rates.")

# ========================
# TAB 2: NATIONAL COMPARISON
# ========================
with tab2:
    st.markdown("### Side-by-Side Rate Comparison")
    st.caption("Compare what different companies pay for the same work in the same state.")
    
    comp_col1, comp_col2 = st.columns(2)
    
    with comp_col1:
        comp_cat = st.selectbox("Filter by Category", ["All"] + sorted(df['category'].unique()), key="comp_cat")
    
    comp_df_base = df if comp_cat == "All" else df[df['category'] == comp_cat]
    
    with comp_col2:
        comp_work = st.selectbox("Select Work Type", [""] + sorted(comp_df_base['display_work'].unique()), key="comp_work")
    
    if comp_work:
        work_df = comp_df_base[comp_df_base['display_work'] == comp_work]
        
        # State picker — only show states with 2+ nationals for meaningful comparison
        state_nat_counts = work_df.groupby('state')['national'].nunique()
        multi_states = state_nat_counts[state_nat_counts >= 2].index.tolist()
        
        comp_state = st.selectbox(
            "Select State", 
            sorted(multi_states) if multi_states else sorted(work_df['state'].unique()),
            key="comp_state"
        )
        
        if comp_state:
            comp_result = work_df[(work_df['state'] == comp_state) | (work_df['state'] == 'All States')]
            
            # Sort: Tier 1 first, then by price descending (highest payer on top)
            comp_result = comp_result.copy()
            comp_result['sort_key'] = comp_result['tier'].apply(lambda t: 0 if t == 1 else 1)
            comp_result = comp_result.sort_values(['sort_key', 'price'], ascending=[True, False])
            
            if not comp_result.empty:
                st.markdown(f"**{comp_work}** in **{comp_state}** — {len(comp_result)} companies reporting")
                
                # Visual bar comparison
                max_price = comp_result['price'].max()
                
                for _, row in comp_result.iterrows():
                    bar_pct = (row['price'] / max_price * 100) if max_price > 0 else 0
                    bar_color = "#059669" if row['tier'] == 1 else "#d97706"
                    tier_tag = "✅" if row['tier'] == 1 else "⚠️"
                    zone_note = f" ({row['region_override']})" if str(row.get('region_override', '')).strip() else ""
                    date_note = str(row['last_updated'])
                    
                    st.markdown(f"""
                    <div class='waterfall-row'>
                        <div class='waterfall-label'>{tier_tag} {row['national']}{zone_note}</div>
                        <div style='flex: 1;'>
                            <div class='waterfall-bar' style='width: {max(bar_pct, 8)}%; background-color: {bar_color};'>${row['price']:,.2f}</div>
                        </div>
                        <div class='waterfall-amount'>{date_note}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Gap analysis
                if len(comp_result) >= 2:
                    highest = comp_result.iloc[0]
                    lowest = comp_result.iloc[-1]
                    gap = highest['price'] - lowest['price']
                    gap_pct = (gap / highest['price'] * 100) if highest['price'] > 0 else 0
                    
                    if gap_pct > 30:
                        st.markdown(f"""
                        <div class='gap-alert'>
                            💡 <b>Spread: ${gap:,.2f} ({gap_pct:.0f}%)</b> between {highest['national']} (${highest['price']:,.2f}) and {lowest['national']} (${lowest['price']:,.2f}). 
                            If you're getting the low end, you may be multiple layers from the investor.
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class='gap-good'>
                            📊 <b>Spread: ${gap:,.2f} ({gap_pct:.0f}%)</b> — relatively tight range across reporting companies.
                        </div>
                        """, unsafe_allow_html=True)
                
                # Table below the bars
                with st.expander("View full data table"):
                    tbl = comp_result[['national', 'state', 'price', 'unit', 'tier', 'last_updated', 'notes', 'region_override']].copy()
                    tbl['price'] = tbl['price'].apply(lambda x: f"${x:,.2f}")
                    tbl.rename(columns={'national':'Company','state':'State','price':'Rate','unit':'Unit','tier':'Tier','last_updated':'Date','notes':'Notes','region_override':'Zone'}, inplace=True)
                    st.dataframe(tbl, use_container_width=True, hide_index=True)
            else:
                st.info("No data for this combination.")
    else:
        st.info("Select a work type above to see how different companies compare.")

# ========================
# TAB 3: PRICING WATERFALL
# ========================
with tab3:
    st.markdown("### Where Does the Money Go?")
    st.caption("See how investor allowables get split before reaching you. Based on industry-standard fee structures shared by veteran contractors.")
    
    st.markdown("""
    The investor (HUD / FHA, Fannie, Freddie, VA) sets the **allowable rate** for every service. 
    That money then flows through **layers** before it reaches the boots-on-the-ground contractor. 
    Each layer takes a cut. Use this calculator to see where you sit.
    """)
    
    st.markdown("---")
    
    wf_col1, wf_col2 = st.columns(2)
    
    with wf_col1:
        st.markdown("**Option A: Pick from our database**")
        
        wf_cat = st.selectbox("Category", [""] + sorted(df[df['tier'] == 1]['category'].unique()), key="wf_cat")
        
        if wf_cat:
            wf_works = sorted(df[(df['tier'] == 1) & (df['category'] == wf_cat)]['display_work'].unique())
            wf_work = st.selectbox("Work Type", wf_works, key="wf_work")
            
            wf_states = sorted(df[(df['tier'] == 1) & (df['display_work'] == wf_work)]['state'].unique())
            wf_state = st.selectbox("State", wf_states, key="wf_state")
            
            if wf_work and wf_state:
                match = df[(df['tier'] == 1) & (df['display_work'] == wf_work) & (df['state'] == wf_state)]
                if not match.empty:
                    investor_rate = match.iloc[0]['price']
                    investor_name = match.iloc[0]['national']
                    st.success(f"**{investor_name} allowable: ${investor_rate:,.2f}** ({wf_work} in {wf_state})")
                else:
                    investor_rate = 0
                    investor_name = ""
            else:
                investor_rate = 0
                investor_name = ""
        else:
            investor_rate = 0
            investor_name = ""
    
    with wf_col2:
        st.markdown("**Option B: Enter manually**")
        manual_rate = st.number_input("Investor allowable rate ($)", min_value=0.0, value=0.0, step=5.0, key="wf_manual")
        your_rate = st.number_input("What YOU are being paid ($)", min_value=0.0, value=0.0, step=5.0, key="wf_yours")
    
    # Use whichever rate is set
    base_rate = manual_rate if manual_rate > 0 else investor_rate
    
    if base_rate > 0:
        st.markdown("---")
        st.markdown("#### The Money Waterfall")
        
        # Standard industry splits
        national_cut_pct = 0.25
        regional_cut_pct = 0.40  # of remainder
        
        national_takes = base_rate * national_cut_pct
        after_national = base_rate - national_takes
        regional_takes = after_national * regional_cut_pct
        botg_gets = after_national - regional_takes
        
        # The waterfall visualization
        layers = [
            ("Investor Allowable", base_rate, "#1e40af", "What the investor allows for this service"),
            ("After National (~25%)", after_national, "#059669", f"National keeps ${national_takes:,.2f}"),
            ("After Regional (~40%)", botg_gets, "#d97706", f"Regional keeps ${regional_takes:,.2f}"),
        ]
        
        for label, amount, color, note in layers:
            bar_pct = (amount / base_rate * 100) if base_rate > 0 else 0
            st.markdown(f"""
            <div class='waterfall-row'>
                <div class='waterfall-label'>{label}</div>
                <div style='flex: 1;'>
                    <div class='waterfall-bar' style='width: {max(bar_pct, 8)}%; background-color: {color};'>${amount:,.2f}</div>
                </div>
                <div class='waterfall-amount' style='font-size: 0.75em;'>{note}</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<div class='waterfall-note'>*Percentage deductions are based on historical industry estimates and community-reported averages. Actual margins vary by national and contract.</div>", unsafe_allow_html=True)
        
        # Summary stats
        st.markdown("")
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.metric("Investor Allows", f"${base_rate:,.2f}")
        with sc2:
            st.metric("BOTG Contractor Gets", f"${botg_gets:,.2f}", f"{botg_gets/base_rate*100:.0f}% of allowable")
        with sc3:
            lost = base_rate - botg_gets
            st.metric("Lost to Middlemen", f"${lost:,.2f}", f"-{lost/base_rate*100:.0f}%", delta_color="inverse")
        
        # If they entered their actual pay
        if your_rate > 0:
            st.markdown("---")
            st.markdown("#### Your Position in the Chain")
            
            your_pct = (your_rate / base_rate * 100) if base_rate > 0 else 0
            
            if your_rate >= botg_gets * 0.95:
                st.markdown(f"""
                <div class='gap-good'>
                    ✅ <b>You're getting ${your_rate:,.2f} ({your_pct:.0f}% of allowable)</b> — This is consistent with working directly 
                    for a national or as a first-tier subcontractor.
                </div>
                """, unsafe_allow_html=True)
            elif your_rate >= botg_gets * 0.60:
                layers_deep = "2-3 layers"
                st.markdown(f"""
                <div class='gap-alert'>
                    ⚠️ <b>You're getting ${your_rate:,.2f} ({your_pct:.0f}% of allowable)</b> — This suggests you're roughly {layers_deep} 
                    from the investor. There's ${base_rate - your_rate:,.2f} being taken before it reaches you.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='gap-alert'>
                    🚩 <b>You're getting ${your_rate:,.2f} ({your_pct:.0f}% of allowable)</b> — You're likely a sub-of-a-sub-of-a-sub. 
                    The investor allows ${base_rate:,.2f} and you're seeing ${your_rate:,.2f}. That's ${base_rate - your_rate:,.2f} disappearing 
                    into the food chain. Consider moving up the chain or going direct.
                </div>
                """, unsafe_allow_html=True)

# ========================
# GLOBAL DISCLAIMER
# ========================
st.markdown("")
st.markdown("""
<div class="disclaimer">
⚠️ <b>Disclaimer:</b> Investor allowables (HUD, VA, Fannie Mae, Freddie Mac) are current as of February 2026. 
National servicer rates are historical community data (2014–2021) included for comparison purposes. 
Always confirm current rates directly with your national or investor before submitting a bid. 
This data is provided for reference only.
</div>
""", unsafe_allow_html=True)