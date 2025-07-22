"""
Comprehensive Streamlit dashboard for the OCR Receipt Processor.
Includes all features from the original dashboard with enhanced functionality.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

# Configure page
st.set_page_config(
    page_title="OCR Receipt Processor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API base URL
API_BASE_URL = "https://receipt-processor-884o.onrender.com"

def main():
    st.title("📄 OCR Receipt Processor Dashboard")
    st.markdown("Upload receipts and bills to extract structured data using real OCR technology")
    
    # Sidebar
    st.sidebar.header("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Upload Receipts", "View Receipts", "Advanced Search", "Advanced Sorting", "Advanced Analytics", "Analytics & Insights", "Export Data"]
    )
    
    if page == "Upload Receipts":
        upload_page()
    elif page == "View Receipts":
        view_receipts_page()
    elif page == "Advanced Search":
        advanced_search_page()
    elif page == "Advanced Sorting":
        advanced_sorting_page()
    elif page == "Advanced Analytics":
        advanced_analytics_page()
    elif page == "Analytics & Insights":
        analytics_page()
    elif page == "Export Data":
        export_page()

def upload_page():
    st.header("📤 Upload Receipts & Bills")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a receipt or bill file",
        type=['jpg', 'jpeg', 'png', 'pdf', 'txt', 'csv'],
        help="Supported formats: Images (JPG, PNG), PDFs, and text files"
    )
    
    if uploaded_file is not None:
        # Display file info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", uploaded_file.name)
        with col2:
            st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")
        with col3:
            st.metric("File Type", uploaded_file.type or "Unknown")
        
        # Upload button
        if st.button("🚀 Process Receipt", type="primary"):
            with st.spinner("Processing receipt with OCR..."):
                try:
                    # Upload file to API
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(f"{API_BASE_URL}/upload", files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Receipt processed successfully!")
                        
                        # Display extracted data
                        display_extracted_data(result["extracted_data"])
                        
                    else:
                        st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
                        
                except Exception as e:
                    st.error(f"❌ Error uploading file: {str(e)}")

def display_extracted_data(receipt_data):
    st.subheader("📋 Extracted Data")
    
    # Create columns for layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Vendor", receipt_data["vendor"])
        st.metric("Amount", f"${receipt_data['amount']:.2f}")
        st.metric("Category", receipt_data["category"])
        
    with col2:
        st.metric("Date", receipt_data["transaction_date"])
        st.metric("Confidence Score", f"{receipt_data['confidence_score']:.1%}")
        st.metric("Items Found", len(receipt_data["items"]))
    
    # Display extracted text
    with st.expander("🔍 Raw Extracted Text"):
        st.text_area("OCR Extracted Text", receipt_data["extracted_text"], height=200)
    
    # Display items if any
    if receipt_data["items"]:
        st.subheader("🛒 Extracted Items")
        items_df = pd.DataFrame(receipt_data["items"])
        st.dataframe(items_df, use_container_width=True)

def view_receipts_page():
    st.header("📋 View All Receipts")
    
    try:
        response = requests.get(f"{API_BASE_URL}/receipts")
        if response.status_code == 200:
            receipts = response.json()
            
            if not receipts:
                st.info("No receipts uploaded yet. Upload some receipts to see them here!")
                return
            
            # Convert to DataFrame
            df = pd.DataFrame(receipts).astype({
                'vendor': str,
                'transaction_date': str,
                'amount': float,
                'category': str,
                'confidence_score': float,
                'file_name': str,
                'items': object,
                'upload_timestamp': str
            })
            
            # Display summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Receipts", len(receipts))
            with col2:
                total_amount = sum(r["amount"] for r in receipts)
                st.metric("Total Spend", f"${total_amount:.2f}")
            with col3:
                avg_confidence = sum(r["confidence_score"] for r in receipts) / len(receipts)
                st.metric("Avg Confidence", f"{avg_confidence:.1%}")
            with col4:
                unique_vendors = len(set(r["vendor"] for r in receipts))
                st.metric("Unique Vendors", unique_vendors)
            
            # Filter options
            st.subheader("🔍 Filters")
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                categories = ["All"] + list(df["category"].unique())
                selected_category = st.selectbox("Category", categories)
            with col2:
                vendors = ["All"] + list(df["vendor"].unique())
                selected_vendor = st.selectbox("Vendor", vendors)
            with col3:
                min_confidence = st.slider("Min Confidence", 0.0, 1.0, 0.0, 0.1)
            with col4:
                vendor_like = st.text_input("Vendor contains", "")
            with col5:
                category_like = st.text_input("Category contains", "")

            # Apply filters
            filtered_df = df.copy()
            if selected_category != "All":
                filtered_df = filtered_df[filtered_df["category"] == selected_category]
            if selected_vendor != "All":
                filtered_df = filtered_df[filtered_df["vendor"] == selected_vendor]
            filtered_df = filtered_df[filtered_df["confidence_score"] >= min_confidence]
            if vendor_like:
                filtered_df = filtered_df[pd.Series(filtered_df["vendor"]).astype(str).str.contains(vendor_like, case=False, na=False)]
            if category_like:
                filtered_df = filtered_df[pd.Series(filtered_df["category"]).astype(str).str.contains(category_like, case=False, na=False)]
            filtered_df = pd.DataFrame(filtered_df).reset_index(drop=True)

            # Display filtered data
            st.subheader("📊 Receipt Details")
            st.dataframe(
                filtered_df[["vendor", "transaction_date", "amount", "category", "confidence_score", "file_name"]],
                use_container_width=True
            )

            # Detailed view with edit option
            if st.checkbox("Show detailed receipt information"):
                for idx, receipt in filtered_df.iterrows():
                    with st.expander(f"{receipt['vendor']} - ${receipt['amount']:.2f} ({receipt['transaction_date']})"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Vendor:** {receipt['vendor']}")
                            st.write(f"**Date:** {receipt['transaction_date']}")
                            st.write(f"**Amount:** ${receipt['amount']:.2f}")
                            st.write(f"**Category:** {receipt['category']}")
                        with col2:
                            st.write(f"**Confidence:** {receipt['confidence_score']:.1%}")
                            st.write(f"**File:** {receipt['file_name']}")
                            st.write(f"**Items:** {len(receipt['items'])}")
                        
                        # Edit functionality
                        try:
                            receipt_id_int = int(receipt['id'])
                        except (ValueError, TypeError):
                            st.warning("This receipt cannot be edited (invalid ID). Please upload a new receipt.")
                            continue
                        
                        # Edit form
                        with st.form(f"edit_form_{receipt['id']}"):
                            new_vendor = st.text_input("Vendor", value=receipt["vendor"], key=f"vendor_{receipt['id']}")
                            new_date = st.text_input("Date", value=receipt["transaction_date"], key=f"date_{receipt['id']}")
                            new_amount = st.number_input("Amount", value=float(receipt["amount"]), key=f"amount_{receipt['id']}")
                            new_category = st.text_input("Category", value=receipt["category"], key=f"category_{receipt['id']}")
                            new_items = st.text_area("Items (JSON)", value=str(receipt["items"]), key=f"items_{receipt['id']}")
                            submitted = st.form_submit_button("Save Changes")
                            if submitted:
                                patch_url = f"{API_BASE_URL}/receipts/{receipt_id_int}"
                                patch_data = {
                                    "vendor": new_vendor,
                                    "transaction_date": new_date,
                                    "amount": new_amount,
                                    "category": new_category,
                                    "items": new_items
                                }
                                response = requests.patch(patch_url, json=patch_data)
                                if response.status_code == 200:
                                    st.success("Receipt updated successfully!")
                                else:
                                    st.error(f"Failed to update: {response.text}")
        else:
            st.error("Failed to load receipts")
    except Exception as e:
        st.error(f"Error loading receipts: {str(e)}")

def advanced_search_page():
    st.header("🔍 Advanced Search")
    st.markdown("Use advanced search algorithms to find receipts")
    
    # Get algorithm info
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/algorithms")
        if response.status_code == 200:
            algo_info = response.json()
            search_algorithms = algo_info.get("search_algorithms", {})
        else:
            search_algorithms = {}
    except:
        search_algorithms = {}
    
    # Search form
    with st.form("advanced_search_form"):
        st.subheader("Search Parameters")
        
        col1, col2 = st.columns(2)
        with col1:
            query = st.text_input("Search Query", placeholder="Enter search term...")
            algorithm = st.selectbox(
                "Search Algorithm",
                options=list(search_algorithms.keys()) if search_algorithms else ["linear", "binary", "hash", "fuzzy", "range", "pattern"],
                format_func=lambda x: f"{x} - {search_algorithms.get(x, '')}" if search_algorithms else x
            )
            field = st.selectbox(
                "Search Field",
                options=["vendor", "transaction_date", "amount", "category", "confidence_score"]
            )
        
        with col2:
            threshold = st.slider("Fuzzy Search Threshold", 0.0, 1.0, 0.7, 0.1)
            min_value = st.text_input("Min Value (for range search)", placeholder="e.g., 10.0 or 01/01/2024")
            max_value = st.text_input("Max Value (for range search)", placeholder="e.g., 100.0 or 12/31/2024")
            pattern = st.text_input("Regex Pattern (for pattern search)", placeholder="e.g., ^[A-Z].*")
        
        submitted = st.form_submit_button("🔍 Search", type="primary")
        
        if submitted and query:
            perform_search(query, field, algorithm, threshold, min_value, max_value, pattern)

def perform_search(query, field, algorithm, threshold, min_value, max_value, pattern):
    try:
        # Prepare search request
        search_data = {
            "query": query,
            "algorithm": algorithm,
            "field": field,
            "threshold": threshold if algorithm == "fuzzy" else None,
            "min_value": min_value if algorithm == "range" and min_value else None,
            "max_value": max_value if algorithm == "range" and max_value else None,
            "pattern": pattern if algorithm == "pattern" and pattern else None
        }
        
        # Remove None values
        search_data = {k: v for k, v in search_data.items() if v is not None}
        
        response = requests.post(f"{API_BASE_URL}/search", json=search_data)
        
        if response.status_code == 200:
            result = response.json()
            
            st.success(f"✅ Found {result['total_count']} results using {result['algorithm_used']} algorithm")
            st.metric("Execution Time", f"{result['execution_time_ms']:.2f} ms")
            
            if result['results']:
                # Display results
                st.subheader("📊 Search Results")
                results_df = pd.DataFrame(result['results'])
                st.dataframe(
                    results_df[["vendor", "transaction_date", "amount", "category", "confidence_score"]],
                    use_container_width=True
                )
                
                # Show query info
                with st.expander("🔍 Query Information"):
                    st.json(result['query_info'])
            else:
                st.info("No results found")
                
        else:
            st.error(f"❌ Search failed: {response.text}")
            
    except Exception as e:
        st.error(f"❌ Error performing search: {str(e)}")

def advanced_sorting_page():
    st.header("📊 Advanced Sorting")
    st.markdown("Sort receipts using different algorithms")
    
    # Get algorithm info
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/algorithms")
        if response.status_code == 200:
            algo_info = response.json()
            sort_algorithms = algo_info.get("sort_algorithms", {})
        else:
            sort_algorithms = {}
    except:
        sort_algorithms = {}
    
    # Sorting form
    with st.form("advanced_sorting_form"):
        st.subheader("Sort Parameters")
        
        col1, col2 = st.columns(2)
        with col1:
            field = st.selectbox(
                "Sort Field",
                options=["vendor", "transaction_date", "amount", "category", "confidence_score"]
            )
            order = st.selectbox("Sort Order", options=["asc", "desc"])
        
        with col2:
            algorithm = st.selectbox(
                "Sort Algorithm",
                options=list(sort_algorithms.keys()) if sort_algorithms else ["quicksort", "mergesort", "timsort", "heapsort"],
                format_func=lambda x: f"{x} - {sort_algorithms.get(x, '')}" if sort_algorithms else x
            )
        
        submitted = st.form_submit_button("📊 Sort", type="primary")
        
        if submitted:
            perform_sort(field, order, algorithm)

def perform_sort(field, order, algorithm):
    try:
        # Prepare sort request
        sort_data = {
            "field": field,
            "order": order,
            "algorithm": algorithm
        }
        
        response = requests.post(f"{API_BASE_URL}/analytics/sort", json=sort_data)
        
        if response.status_code == 200:
            result = response.json()
            
            st.success(f"✅ Sorted {len(result['results'])} receipts using {result['algorithm_used']} algorithm")
            st.metric("Execution Time", f"{result['execution_time_ms']:.2f} ms")
            
            # Display sorted results
            st.subheader("📊 Sorted Results")
            results_df = pd.DataFrame(result['results'])
            st.dataframe(
                results_df[["vendor", "transaction_date", "amount", "category", "confidence_score"]],
                use_container_width=True
            )
            
            # Show sort info
            with st.expander("📊 Sort Information"):
                st.json(result['sort_info'])
                
        else:
            st.error(f"❌ Sorting failed: {response.text}")
            
    except Exception as e:
        st.error(f"❌ Error performing sort: {str(e)}")

def advanced_analytics_page():
    st.header("📈 Advanced Analytics")
    st.markdown("Perform advanced statistical aggregations")
    
    # Get algorithm info
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/algorithms")
        if response.status_code == 200:
            algo_info = response.json()
            agg_functions = algo_info.get("aggregation_functions", {})
        else:
            agg_functions = {}
    except:
        agg_functions = {}
    
    # Analytics form
    with st.form("analytics_form"):
        st.subheader("Aggregation Parameters")
        
        col1, col2 = st.columns(2)
        with col1:
            function = st.selectbox(
                "Aggregation Function",
                options=list(agg_functions.keys()) if agg_functions else ["sum", "mean", "median", "mode", "variance", "std_dev", "histogram", "time_series"],
                format_func=lambda x: f"{x} - {agg_functions.get(x, '')}" if agg_functions else x
            )
            field = st.selectbox(
                "Aggregation Field",
                options=["vendor", "transaction_date", "amount", "category", "confidence_score"]
            )
        
        with col2:
            time_field = st.selectbox(
                "Time Field (for time series)",
                options=["transaction_date", "upload_timestamp"],
                disabled=function != "time_series"
            )
            window = st.selectbox(
                "Time Window (for time series)",
                options=["daily", "weekly", "monthly"],
                disabled=function != "time_series"
            )
            bins = st.number_input(
                "Number of Bins (for histogram)",
                min_value=1,
                max_value=100,
                value=10,
                disabled=function != "histogram"
            )
        
        if st.form_submit_button("📈 Analyze", type="primary"):
            perform_aggregation(function, field, bins, time_field, window)

def perform_aggregation(function, field, bins, time_field, window):
    try:
        # Prepare aggregation request
        agg_data = {
            "function": function,
            "field": field,
            "time_field": time_field if function == "time_series" else None,
            "window": window if function == "time_series" else None,
            "bins": bins if function == "histogram" else None
        }
        
        # Remove None values
        agg_data = {k: v for k, v in agg_data.items() if v is not None}
        
        response = requests.post(f"{API_BASE_URL}/analytics/aggregate", json=agg_data)
        
        if response.status_code == 200:
            result = response.json()
            
            st.success(f"✅ Analysis completed using {result['function_used']} function")
            st.metric("Execution Time", f"{result['execution_time_ms']:.2f} ms")
            
            # Display results based on function type
            st.subheader("📊 Analysis Results")
            
            if function == "histogram":
                if isinstance(result['result'], dict):
                    # Create histogram chart
                    hist_data = result['result']
                    if hist_data.get('bins') and hist_data.get('counts'):
                        # Create histogram using bins and counts
                        fig = px.bar(
                            x=hist_data['bins'],
                            y=hist_data['counts'],
                            title=f"Histogram of {field}",
                            labels={'x': field, 'y': 'Frequency'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    elif hist_data.get('frequency_distribution'):
                        # Alternative format with frequency distribution
                        freq_data = hist_data['frequency_distribution']
                        fig = px.bar(
                            x=list(freq_data.keys()),
                            y=list(freq_data.values()),
                            title=f"Histogram of {field}",
                            labels={'x': field, 'y': 'Frequency'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    st.json(result['result'])
            
            elif function == "time_series":
                if isinstance(result['result'], list):
                    # Create time series chart
                    df = pd.DataFrame(result['result'])
                    if not df.empty:
                        # Use 'sum' field for time series data
                        y_field = 'sum' if 'sum' in df.columns else 'total_amount'
                        fig = px.line(
                            df,
                            x='time_period',
                            y=y_field,
                            title=f"Time Series Analysis of {field}",
                            labels={'time_period': 'Time Period', y_field: 'Count' if field == 'transaction_date' else 'Total Amount'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    st.json(result['result'])
            
            else:
                # Display simple result
                if function:
                    function_title = function.replace('_', ' ').title()
                    st.metric(f"{function_title} of {field}", result['result'])
                else:
                    st.metric(f"Result of {field}", result['result'])
                st.json(result['result'])
            
            # Show aggregation info
            with st.expander("📊 Aggregation Information"):
                st.json(result['aggregation_info'])
                
        else:
            st.error(f"❌ Analysis failed: {response.text}")
            
    except Exception as e:
        st.error(f"❌ Error performing analysis: {str(e)}")

def display_histogram(hist_data):
    if hist_data and 'bins' in hist_data and 'counts' in hist_data:
        fig = go.Figure(data=[
            go.Bar(x=hist_data['bins'][:-1], y=hist_data['counts'])
        ])
        fig.update_layout(title="Histogram", xaxis_title="Value", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)

def display_time_series(time_data):
    if time_data:
        df = pd.DataFrame(time_data)
        fig = px.line(df, x='time_period', y='sum', title="Time Series Analysis")
        st.plotly_chart(fig, use_container_width=True)

def analytics_page():
    st.header("📈 Analytics & Insights")
    
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/statistics")
        if response.status_code == 200:
            stats = response.json()
            
            if stats["total_receipts"] == 0:
                st.info("No receipts uploaded yet. Upload some receipts to see analytics!")
                return
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Receipts", stats["total_receipts"])
            with col2:
                st.metric("Total Spend", f"${stats['total_spend']:.2f}")
            with col3:
                avg_spend = stats["total_spend"] / stats["total_receipts"]
                st.metric("Average Receipt", f"${avg_spend:.2f}")
            with col4:
                unique_vendors = len(stats["top_vendors"])
                st.metric("Unique Vendors", unique_vendors)
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("💰 Category Breakdown")
                if stats["category_breakdown"]:
                    category_df = pd.DataFrame(stats["category_breakdown"])
                    fig = px.pie(
                        category_df, 
                        values="total_amount", 
                        names="category",
                        title="Spending by Category"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No category data available")
            
            with col2:
                st.subheader("🏪 Top Vendors")
                if stats["top_vendors"]:
                    vendor_df = pd.DataFrame(stats["top_vendors"])
                    fig = px.bar(
                        vendor_df,
                        x="vendor",
                        y="total_amount",
                        title="Top Vendors by Spend",
                        labels={"total_amount": "Total Spend ($)", "vendor": "Vendor"}
                    )
                    fig.update_xaxes(tickangle=45)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No vendor data available")
            
            # Advanced statistics
            if stats.get("advanced_stats"):
                st.subheader("📊 Advanced Statistics")
                advanced_stats = stats["advanced_stats"]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Average Amount", f"${advanced_stats.get('avg_receipt_amount', 0):.2f}")
                with col2:
                    st.metric("Most Expensive Receipt", f"${advanced_stats.get('most_expensive_receipt', 0):.2f}")
                with col3:
                    st.metric("Confidence Average", f"{advanced_stats.get('confidence_avg', 0):.1%}")
            
            # Detailed breakdowns
            st.subheader("📊 Detailed Analytics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if stats["top_vendors"]:
                    st.write("**Top Vendors by Receipt Count:**")
                    vendor_count_df = pd.DataFrame(stats["top_vendors"])
                    vendor_count_df = vendor_count_df.sort_values("count", ascending=False)
                    st.dataframe(vendor_count_df[["vendor", "count", "total_amount"]], use_container_width=True)
            
            with col2:
                if stats["category_breakdown"]:
                    st.write("**Category Breakdown:**")
                    category_df = pd.DataFrame(stats["category_breakdown"])
                    st.dataframe(category_df, use_container_width=True)
            
            # Monthly trends (if available)
            if stats["monthly_trends"]:
                st.subheader("📅 Monthly Trends")
                trends_df = pd.DataFrame(stats["monthly_trends"])
                fig = px.line(
                    trends_df,
                    x="month",
                    y="total_amount",
                    title="Monthly Spending Trends",
                    labels={"total_amount": "Total Spend ($)", "month": "Month"}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.error("Failed to fetch statistics")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")

def export_page():
    st.header("📤 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Export as CSV")
        if st.button("📊 Download CSV"):
            try:
                response = requests.get(f"{API_BASE_URL}/export/csv")
                if response.status_code == 200:
                    st.download_button(
                        label="📥 Download CSV File",
                        data=response.content,
                        file_name="receipts.csv",
                        mime="text/csv"
                    )
                else:
                    st.error("Failed to generate CSV")
            except Exception as e:
                st.error(f"Error exporting CSV: {str(e)}")
    
    with col2:
        st.subheader("Export as JSON")
        if st.button("📄 Download JSON"):
            try:
                response = requests.get(f"{API_BASE_URL}/export/json")
                if response.status_code == 200:
                    st.download_button(
                        label="📥 Download JSON File",
                        data=response.content,
                        file_name="receipts.json",
                        mime="application/json"
                    )
                else:
                    st.error("Failed to generate JSON")
            except Exception as e:
                st.error(f"Error exporting JSON: {str(e)}")

if __name__ == "__main__":
    main() 
