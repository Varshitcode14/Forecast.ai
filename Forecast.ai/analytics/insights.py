import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import plotly.graph_objects as go
import json
import os

class DataAnalyzer:
    def __init__(self, df):
        self.df = df
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.prepare_data()

    def prepare_data(self):
        # Add month and year columns
        self.df['Month'] = self.df['Date'].dt.month
        self.df['Year'] = self.df['Date'].dt.year
        
        # Calculate additional metrics
        self.df['Month_Year'] = self.df['Date'].dt.strftime('%Y-%m')

    def get_basic_stats(self):
        return {
            'total_sales': float(self.df['Total Amount'].sum()),
            'avg_order_value': float(self.df['Total Amount'].mean()),
            'total_orders': len(self.df),
            'unique_customers': self.df['Customer ID'].nunique(),
            'avg_age': float(self.df['Age'].mean())
        }

    def generate_gender_distribution(self):
        gender_dist = self.df['Gender'].value_counts()
        fig = px.pie(
            values=gender_dist.values,
            names=gender_dist.index,
            title='Customer Gender Distribution'
        )
        return json.loads(fig.to_json())

    def generate_age_distribution(self):
        fig = px.histogram(
            self.df,
            x='Age',
            nbins=20,
            title='Customer Age Distribution'
        )
        return json.loads(fig.to_json())

    def generate_sales_by_category(self):
        category_sales = self.df.groupby('Product Category')['Total Amount'].sum().reset_index()
        fig = px.bar(
            category_sales,
            x='Product Category',
            y='Total Amount',
            title='Sales by Product Category'
        )
        return json.loads(fig.to_json())

    def generate_monthly_trend(self):
        monthly_sales = self.df.groupby('Month_Year')['Total Amount'].sum().reset_index()
        fig = px.line(
            monthly_sales,
            x='Month_Year',
            y='Total Amount',
            title='Monthly Sales Trend'
        )
        return json.loads(fig.to_json())

    def generate_quantity_distribution(self):
        fig = px.box(
            self.df,
            x='Product Category',
            y='Quantity',
            title='Quantity Distribution by Product Category'
        )
        return json.loads(fig.to_json())

    def generate_age_category_correlation(self):
        avg_age_category = self.df.groupby('Product Category')['Age'].mean().reset_index()
        fig = px.bar(
            avg_age_category,
            x='Product Category',
            y='Age',
            title='Average Customer Age by Product Category'
        )
        return json.loads(fig.to_json())

    def get_customer_segments(self):
        # Simple RFM segmentation
        today = self.df['Date'].max()
        
        rfm = self.df.groupby('Customer ID').agg({
            'Date': lambda x: (today - x.max()).days,  # Recency
            'Transaction ID': 'count',  # Frequency
            'Total Amount': 'sum'  # Monetary
        }).reset_index()
        
        rfm.columns = ['Customer ID', 'Recency', 'Frequency', 'Monetary']
        
        # Scale the RFM values
        scaler = StandardScaler()
        rfm_scaled = scaler.fit_transform(rfm[['Recency', 'Frequency', 'Monetary']])
        
        # Simple segmentation based on average values
        rfm['Segment'] = 'Regular'
        rfm.loc[rfm['Monetary'] > rfm['Monetary'].mean(), 'Segment'] = 'High Value'
        rfm.loc[rfm['Frequency'] > rfm['Frequency'].mean(), 'Segment'] = 'Loyal'
        rfm.loc[(rfm['Monetary'] > rfm['Monetary'].mean()) & 
                (rfm['Frequency'] > rfm['Frequency'].mean()), 'Segment'] = 'VIP'
        
        segment_counts = rfm['Segment'].value_counts()
        fig = px.pie(
            values=segment_counts.values,
            names=segment_counts.index,
            title='Customer Segments Distribution'
        )
        return json.loads(fig.to_json())

    def get_all_insights(self):
        return {
            'basic_stats': self.get_basic_stats(),
            'gender_distribution': self.generate_gender_distribution(),
            'age_distribution': self.generate_age_distribution(),
            'sales_by_category': self.generate_sales_by_category(),
            'monthly_trend': self.generate_monthly_trend(),
            'quantity_distribution': self.generate_quantity_distribution(),
            'age_category_correlation': self.generate_age_category_correlation(),
            'customer_segments': self.get_customer_segments()
        }