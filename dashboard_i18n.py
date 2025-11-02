"""
This is a backup/reference file showing the complete localized dashboard implementation.
Use this as a reference for updating dashboard.py systematically.
"""

# Key patterns for localization:
# 1. All hardcoded strings should use t('key')
# 2. Strings with variables use t('key', var=value)
# 3. Tab labels: st.tabs([t('tab1'), t('tab2'), ...])
# 4. Headers: st.header(t('header_key'))
# 5. Buttons: st.button(t('button_key'))
# 6. Selectbox: st.selectbox(t('label_key'), options)
# 7. Metrics: st.metric(t('metric_key'), value, help=t('help_key'))

# Example translations for each page:
SALES_ANALYSIS_TRANSLATIONS = """
st.header(f"📊 {t('sales_analysis')}")
st.subheader(t('overall_performance'))
tab1, tab2, tab3, tab4 = st.tabs([
    f"📈 {t('trends')}", 
    f"🏆 {t('top_products')}", 
    f"⏰ {t('time_patterns')}", 
    f"🚨 {t('anomalies')}"
])
period = st.selectbox(t('select_period'), [t('daily'), t('weekly'), t('monthly')])
st.subheader(t('revenue_trends'))
fig.update_layout(title=t('daily_revenue_trend'), xaxis_title=t('date'), yaxis_title=t('revenue'))
"""

CUSTOMER_ANALYSIS_TRANSLATIONS = """
st.header(f"👥 {t('customer_insights')}")
st.subheader(t('customer_metrics'))
st.metric(t('total_customers'), f"{metrics:,}")
st.metric(t('repeat_customers'), f"{metrics:,}")
st.metric(t('repeat_rate'), f"{metrics:.1f}%")
st.metric(t('avg_customer_ltv'), f"${metrics:,.2f}")
tab1, tab2, tab3, tab4 = st.tabs([
    f"🌟 {t('valuable_customers')}", 
    f"⚠️ {t('churn_risk')}", 
    f"📊 {t('segments')}", 
    f"🆕 {t('new_customers')}"
])
"""

PRODUCT_ANALYSIS_TRANSLATIONS = """
st.header(f"📦 {t('product_performance')}")
tab1, tab2, tab3, tab4 = st.tabs([
    f"🏃 {t('fast_slow_movers')}", 
    f"📊 {t('abc_analysis')}", 
    f"🔄 {t('lifecycle')}", 
    f"📈 {t('inventory_signals')}"
])
st.subheader(t('fast_moving_products'))
st.subheader(t('slow_moving_products'))
"""

RFM_ANALYSIS_TRANSLATIONS = """
st.header(f"🎯 {t('rfm_title')}")
st.markdown(t('rfm_description'))
st.subheader(t('segment_overview'))
st.subheader(t('segment_details'))
selected_segment = st.selectbox(t('select_segment'), segments)
st.write(t('recommended_actions'))
"""

REFILL_PREDICTION_TRANSLATIONS = """
st.header(f"💊 {t('refill_title')}")
st.markdown(t('refill_description'))
st.subheader(t('refill_dashboard'))
st.metric(t('tracked_pairs'), f"{count:,}")
st.metric(t('avg_interval'), f"{days:.1f} {t('days')}")
st.metric(t('overdue'), f"{count:,}")
tab1, tab2, tab3, tab4 = st.tabs([
    f"⚠️ {t('overdue_refills')}", 
    f"📅 {t('upcoming_refills')}", 
    f"👤 {t('customer_schedule')}", 
    f"💰 {t('price_predictions')}"
])
"""

CROSS_SELL_TRANSLATIONS = """
st.header(f"🔗 {t('cross_sell_title')}")
st.markdown(t('market_basket_description'))
st.markdown(t('market_basket_helps'))
tab1, tab2, tab3, tab4 = st.tabs([
    f"🎁 {t('product_bundles')}", 
    f"🔄 {t('product_associations')}", 
    f"📊 {t('market_basket')}", 
    f"💡 {t('recommendations')}"
])
"""

AI_QUERY_TRANSLATIONS = """
st.header(f"🤖 {t('ai_query_title')}")
st.markdown(t('ai_query_description'))
st.subheader(t('ask_your_question'))
user_query = st.text_input(t('your_question'), placeholder="e.g., What are the top 5 products?")
if st.button(t('ask'), type="primary"):
    with st.spinner(t('analyzing')):
        # Process query
"""

EXPORT_TRANSLATIONS = """
st.header(f("📥 {t('export_title')}")
st.subheader(t('generate_reports'))
report_type = st.selectbox(t('select_report_type'), [
    t('sales_summary'),
    t('customer_analysis'),
    t('product_performance_report'),
    t('rfm_segmentation_report'),
    t('refill_predictions_report'),
    t('cross_sell_opportunities')
])
if st.button(t('generate_report')):
    with st.spinner(t('generating_report')):
        # Generate report
    st.success(t('report_generated'))
"""

# Notes for implementation:
# 1. Use global t() function defined at module level
# 2. Rerun app when language changes: st.rerun()
# 3. Format strings: t('key', n=value, days=value, product=name)
# 4. Charts need text updated: fig.update_layout(title=t('chart_title'))
# 5. Plotly charts text direction handled by CSS
# 6. Keep emojis in menu items - they work in both directions

