# Add to app/dashboard.py
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time


class RealTimeDashboard:
    def __init__(self):
        self.refresh_interval = 30  # seconds

    def render_dashboard(self, df: pd.DataFrame):
        """Render real-time dashboard"""
        st.title("📊 Real-Time Invoice Analytics Dashboard")

        # Auto-refresh mechanism
        if st.checkbox("Auto-refresh (30s)", value=False):
            time.sleep(self.refresh_interval)
            st.experimental_rerun()

        # Key metrics row
        self._render_kpi_cards(df)

        # Charts row
        col1, col2 = st.columns(2)

        with col1:
            self._render_spending_trend(df)
            self._render_vendor_pie_chart(df)

        with col2:
            self._render_category_analysis(df)
            self._render_anomaly_alerts(df)

        # Bottom section
        self._render_recent_activity(df)

    def _render_kpi_cards(self, df: pd.DataFrame):
        """Render KPI cards"""
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            total_amount = df['total_price'].sum()
            st.metric(
                "Total Spending",
                f"${total_amount:,.2f}",
                delta=f"{(total_amount * 0.1):,.2f}"  # Mock delta
            )

        with col2:
            st.metric(
                "Active Vendors",
                df['vendor_name'].nunique(),
                delta=2
            )

        with col3:
            avg_invoice = df.groupby('invoice_id')['total_price'].sum().mean() if 'invoice_id' in df.columns else df[
                'total_price'].mean()
            st.metric(
                "Avg Invoice Value",
                f"${avg_invoice:.2f}",
                delta=f"{(avg_invoice * 0.05):.2f}"
            )

        with col4:
            processing_accuracy = 95.5  # Mock metric
            st.metric(
                "Processing Accuracy",
                f"{processing_accuracy}%",
                delta="2.1%"
            )

        with col5:
            cost_savings = 15000  # Mock metric
            st.metric(
                "Monthly Savings",
                f"${cost_savings:,}",
                delta="$2,500"
            )

    def _render_spending_trend(self, df: pd.DataFrame):
        """Render spending trend chart"""
        st.subheader("📈 Spending Trend")

        if 'invoice_date' in df.columns:
            daily_spending = df.groupby(df['invoice_date'].dt.date)['total_price'].sum()

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily_spending.index,
                y=daily_spending.values,
                mode='lines+markers',
                name='Daily Spending',
                line=dict(color='#1f77b4', width=3)
            ))

            fig.update_layout(
                title="Daily Spending Trend",
                xaxis_title="Date",
                yaxis_title="Amount ($)",
                hovermode='x unified'
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Date information not available for trend analysis")

    def _render_vendor_pie_chart(self, df: pd.DataFrame):
        """Render vendor distribution pie chart"""
        st.subheader("🏢 Vendor Distribution")

        vendor_spending = df.groupby('vendor_name')['total_price'].sum().head(8)

        fig = go.Figure(data=[go.Pie(
            labels=vendor_spending.index,
            values=vendor_spending.values,
            hole=0.4
        )])

        fig.update_traces(
            textposition='inside',
            textinfo='percent+label'
        )

        fig.update_layout(
            title="Spending by Vendor",
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_anomaly_alerts(self, df: pd.DataFrame):
        """Render anomaly alerts"""
        st.subheader("⚠️ Anomaly Alerts")

        if 'is_anomaly' in df.columns:
            anomalies = df[df['is_anomaly'] == True]

            if not anomalies.empty:
                st.warning(f"Found {len(anomalies)} anomalous transactions")

                for idx, row in anomalies.head(5).iterrows():
                    with st.expander(f"Anomaly: {row['description'][:50]}..."):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Amount:** ${row['total_price']:.2f}")
                            st.write(f"**Vendor:** {row['vendor_name']}")
                        with col2:
                            st.write(f"**Anomaly Score:** {row.get('anomaly_score', 'N/A'):.2f}")
                            st.write(f"**Date:** {row.get('invoice_date', 'N/A')}")
            else:
                st.success("No anomalies detected")
        else:
            st.info("Run anomaly detection to see alerts")