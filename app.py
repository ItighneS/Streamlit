import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import plotly.express as px
import seaborn as sns

#DATA PREPARATION
trade=pd.read_csv(r"C:\Users\itigh\Streamlit\Imports_Exports_Dataset.csv")
samtrade = trade.sample(n=3001, random_state=55015)
samtrade.head()
samtrade.info()
st.title('Import Export Database Dashboard')


##############################################
#1
total_import_value = samtrade[samtrade['Import_Export'] == 'Import']['Value'].sum()
total_export_value = samtrade[samtrade['Import_Export'] == 'Export']['Value'].sum()
absolute_difference = abs(total_import_value - total_export_value)
data = {
    'Type': ['Import', 'Export'],
    'Value': [total_import_value, total_export_value]
}
difference_data = pd.DataFrame(data)
plt.figure(figsize=(10, 6))
bars = plt.barh(difference_data['Type'], difference_data['Value'], color=['orange', 'blue'])
plt.title('Total Import and Export Values', fontsize=14)
plt.xlabel('Value ($)', fontsize=14)
plt.ylabel('Type', fontsize=12)
plt.xticks(rotation=45)
max_value = max(difference_data['Value'])
plt.xlim(5000000, max_value * 1.1)  # 10% more than max value for better spacing
plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
plt.annotate(f'Net Loss in trade: ${absolute_difference:,.2f}', 
             xy=(max_value * .985, 1),  # Position it slightly offset to the right
             xytext=(10, 0),
             textcoords='offset points', 
             fontsize=8, 
             color='red', 
             ha='left')
st.pyplot(plt.gcf())
plt.close()

#######################################

#2
samtrade['Date'] = pd.to_datetime(samtrade['Date'], dayfirst=True, errors='coerce')
samtrade.set_index('Date', inplace=True, drop=False)
monthly_data = samtrade.groupby([pd.Grouper(freq='ME'), 'Import_Export'])['Value'].sum().unstack()
monthly_data.reset_index(inplace=True)
monthly_data['Year'] = pd.to_datetime(monthly_data['Date']).dt.year
export_data_yearly = monthly_data.groupby('Year')['Export'].sum().reset_index()
import_data_yearly = monthly_data.groupby('Year')['Import'].sum().reset_index()

def currency_format(x, pos):
    return '${:,.0f}'.format(x)

max_export_year = export_data_yearly['Export'].idxmax()
max_import_year = import_data_yearly['Import'].idxmax()
plt.figure(figsize=(10, 6))
bars_export = plt.bar(export_data_yearly['Year'], export_data_yearly['Export'], color='blue')
bars_export[max_export_year].set_color('red')
plt.title('Total Cumulative Export Value by Year', fontsize=16)
plt.xlabel('Year', fontsize=14)
plt.ylabel('Total Export Value', fontsize=14)
plt.xticks(rotation=45)
plt.gca().yaxis.set_major_formatter(FuncFormatter(currency_format))
plt.grid(False)
plt.tight_layout()
st.pyplot(plt.gcf()) 
plt.figure(figsize=(10, 6))
bars_import = plt.bar(import_data_yearly['Year'], import_data_yearly['Import'], color='orange')
bars_import[max_import_year].set_color('red')
plt.title('Total Cumulative Import Value by Year', fontsize=16)
plt.xlabel('Year', fontsize=14)
plt.ylabel('Total Import Value', fontsize=14)
plt.xticks(rotation=45)
plt.gca().yaxis.set_major_formatter(FuncFormatter(currency_format))
plt.grid(False)
plt.tight_layout()
st.pyplot(plt.gcf())

################################


#3 Trade by category
def currency_format(x, pos):
    return '${:,.0f}'.format(x)
trade_type = st.selectbox("Select Trade Type", options=["Import", "Export"])
filtered_data = samtrade[samtrade['Import_Export'] == trade_type]
category_counts = filtered_data.groupby('Category')['Value'].sum()
colors = plt.cm.viridis(np.linspace(0, 1, len(category_counts)))
fig, ax = plt.subplots()
ax.bar(category_counts.index, category_counts.values, color=colors)
ax.set_xlabel('Category')  
ax.set_ylabel('Transactions')
ax.yaxis.set_major_formatter(FuncFormatter(currency_format))
st.title("Category-wise Trade")
st.pyplot(fig)

########################################################################


#4
category_counts = samtrade.groupby('Category')['Value'].sum()
fig3, ax4 = plt.subplots()
ax4.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%', startangle=90)
ax4.axis('equal')
st.title(f"{trade_type} Category-wise Trade Distribution")
st.pyplot(fig3)

########################################################################

#5
country_agg = samtrade.groupby('Country').agg({
    'Quantity': 'count',
    'Value': 'sum'
}).reset_index()
top_countries = country_agg.nlargest(10, 'Value')

fig_map = px.choropleth(
    top_countries,
    locations='Country',
    locationmode='country names',
    color='Value',
    hover_name='Country',
    title='Top 10 Countries by Overall Trade Value',
    color_continuous_scale='Viridis',
    labels={'Value': 'Total Trade Value'},
)
st.title("Top 10 Countries in Terms of Overall Trade Value")
st.plotly_chart(fig_map)
top_countries = country_agg.nlargest(10, 'Value')
import_data = samtrade[samtrade['Import_Export'] == 'Import'].groupby('Country')['Value'].sum()
export_data = samtrade[samtrade['Import_Export'] == 'Export'].groupby('Country')['Value'].sum()
top_import_export = pd.DataFrame({
    'Import': import_data,
    'Export': export_data
}).reindex(top_countries['Country']) 
fig, ax = plt.subplots(figsize=(12, 6))
bar_width = 0.35
r1 = np.arange(len(top_import_export))
r2 = r1 + bar_width 
bars1 = ax.bar(r1, top_import_export['Import'], color='blue', width=bar_width, edgecolor='grey', label='Import')
bars2 = ax.bar(r2, top_import_export['Export'], color='orange', width=bar_width, edgecolor='grey', label='Export')
ax.set_xlabel('Countries', fontsize=14)
ax.set_ylabel('Total Value', fontsize=14)
ax.set_title('Import and Export Values for Top 10 Countries', fontsize=16)
ax.set_xticks(r1 + bar_width / 2) 
ax.set_xticklabels(top_import_export.index, rotation=45)
ax.legend()
from matplotlib.ticker import FuncFormatter
def currency_formatter(x, _):
    if x >= 1_000_000:
        return f'${x/1_000_000:.1f}M'  # Millions
    elif x >= 1_000:
        return f'${x/1_000:.1f}K'  # Thousands
    else:
        return f'${int(x)}'  # Actual number
ax.yaxis.set_major_formatter(FuncFormatter(currency_formatter))
st.title("Import and Export Values for Top 10 Countries")
st.pyplot(fig)


#########################################################################

#6
samtrade['Value'] = pd.to_numeric(samtrade['Value'], errors='coerce')
top_exports = samtrade[samtrade['Import_Export'] == 'Export'] \
                .groupby('Country')['Value'].sum().sort_values(ascending=False).head(3).index.tolist()

top_imports = samtrade[samtrade['Import_Export'] == 'Import'] \
                .groupby('Country')['Value'].sum().sort_values(ascending=False).head(3).index.tolist()
export_categories = samtrade[(samtrade['Country'].isin(top_exports)) & (samtrade['Import_Export'] == 'Export')]
if not export_categories.empty:
    export_category_counts = export_categories.groupby(['Country', 'Category'])['Value'].sum().unstack().fillna(0)
else:
    export_category_counts = pd.DataFrame()
import_categories = samtrade[(samtrade['Country'].isin(top_imports)) & (samtrade['Import_Export'] == 'Import')]
if not import_categories.empty:
    import_category_counts = import_categories.groupby(['Country', 'Category'])['Value'].sum().unstack().fillna(0)
else:
    import_category_counts = pd.DataFrame()
st.title('Product Categories Traded by Top Exporting and Importing Countries')
st.subheader('Export Categories by Top Exporting Countries')
if not export_category_counts.empty:
    export_chart = px.bar(export_category_counts.reset_index(),
                           x='Country',
                           y=export_category_counts.columns,
                           title='Export Categories by Country',
                           labels={'value': 'Value', 'Category': 'Category'},
                           hover_data={'Country': True})  # Show country in hover
    st.plotly_chart(export_chart)
else:
    st.write("No data available for exporting countries.")
st.subheader('Import Categories by Top Importing Countries')
if not import_category_counts.empty:
    import_chart = px.bar(import_category_counts.reset_index(),
                           x='Country',
                           y=import_category_counts.columns,
                           title='Import Categories by Country',
                           labels={'value': 'Value', 'Category': 'Category'},
                           hover_data={'Country': True})  # Show country in hover
    st.plotly_chart(import_chart)
else:
    st.write("No data available for importing countries.")

################################################################
#7

shipping_data = samtrade.groupby('Shipping_Method')['Value'].sum()
colors = ['#FFB3BA', '#FFDFBA', '#FFFFBA']  
plt.figure(figsize=(8, 8)) 
plt.pie(
    shipping_data,
    labels=[f'{method} ({value:,.2f})' for method, value in zip(shipping_data.index, shipping_data)],
    colors=colors,
    startangle=90,
    autopct='%1.1f%%',
    pctdistance=0.85,
)
plt.axis('equal')
plt.title('Trade value by Shipping Method', fontsize=16)
st.pyplot(plt.gcf())

###############################################################

#8
payment_terms = ['All'] + list(samtrade['Payment_Terms'].unique())
selected_payment_term = st.selectbox("Select Payment Terms:", payment_terms)
if selected_payment_term == 'All':
    filtered_data = samtrade  
else:
    filtered_data = samtrade[samtrade['Payment_Terms'] == selected_payment_term]
transaction_counts = filtered_data.groupby(['Shipping_Method', 'Payment_Terms']).size().reset_index(name='Count')
fig = px.bar(
    transaction_counts,
    x='Shipping_Method',  
    y='Count',
    color='Payment_Terms',
    title=f'Usage of Shipping Methods for Payment Terms: {selected_payment_term}',
    labels={'Count': 'Number of Transactions'},
)
fig.update_layout(barmode='stack', xaxis_title='Shipping Method', yaxis_title='Number of Transactions')

st.plotly_chart(fig)

#######################################################################

#9
correlation_matrix = samtrade[['Value', 'Weight']].corr()
plt.figure(figsize=(6, 4))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', square=True, cbar_kws={"shrink": .8})
plt.title('Correlation Matrix between Transaction Value and Weight', fontsize=16)
st.pyplot(plt.gcf())

############################################

#10
value_summary = samtrade.groupby('Payment_Terms')['Value'].mean().reset_index()
plt.figure(figsize=(14, 6))
plt.plot(value_summary['Payment_Terms'], value_summary['Value'], marker='o', color='b', linestyle='-', linewidth=2, markersize=8)
plt.scatter(value_summary['Payment_Terms'], value_summary['Value'], color='red', s=100, edgecolor='black')
plt.title('Average Transaction Value by Payment Terms', fontsize=16)
plt.xlabel('Payment Terms', fontsize=14)
plt.ylabel('Average Value', fontsize=14)
plt.xticks(rotation=45)  # Rotate x labels for better readability
plt.grid(True)
st.pyplot(plt.gcf())


############################################

samtrade['Date'] = pd.to_datetime(samtrade['Date'], errors='coerce')

monthly_dataset = samtrade.copy()  # Create a copy of the original dataset
monthly_dataset['Value'].fillna(0, inplace=True)  # Replace NaN in Value with 0 for calculations

# Create new columns for Year and Month in the monthly dataset
monthly_dataset['Year'] = monthly_dataset['Date'].dt.year
monthly_dataset['Month'] = monthly_dataset['Date'].dt.month

# Group by Month and calculate average trade value across all years
monthly_avg = monthly_dataset.groupby('Month')['Value'].mean().reset_index()

# Create a new column to format month names
monthly_avg['Month_Name'] = monthly_avg['Month'].apply(lambda x: pd.to_datetime(f'2023-{int(x)}-01').strftime('%B'))

# Sort by Month number for correct ordering
monthly_avg.sort_values(by='Month', inplace=True)

# Plot the line chart
plt.figure(figsize=(10, 6))
plt.plot(monthly_avg['Month_Name'], monthly_avg['Value'], marker='o', color='blue')

plt.title('Average Trade Values per Month (2019-2024)', fontsize=16)
plt.xlabel('Month', fontsize=14)
plt.ylabel('Average Trade Value ($)', fontsize=14)
plt.xticks(rotation=45)
plt.grid()
plt.tight_layout()

# Display the chart in Streamlit
st.pyplot(plt.gcf())



