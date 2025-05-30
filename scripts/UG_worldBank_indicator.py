# UG_worldBank_indicator.py
# ---------------------------------------------
# Uganda World Bank Indicator Analysis (Streamlit App)
# Author: Denis Awany
# ---------------------------------------------


# Import libraries
# -------
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px


# Page configuration
# ------
st.set_page_config(
    page_title="UGANDA World Bank Indicator Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

# Import the data
UG_data = pd.read_csv("https://raw.githubusercontent.com/AwanyDenis/Uganda-WB-Indicator/main/data/API_UGA_DS2_en_csv_v2_93736.csv", skiprows=3)


# UG_data.columns
UG_data_subset = UG_data.drop(['Country Name','Country Code','1960','Unnamed: 69'], axis=1)
year_cols = UG_data_subset.columns[2:]

UG_data_long = UG_data_subset.melt(id_vars=['Indicator Name','Indicator Code'],
    value_vars=year_cols, var_name='Year', value_name='Amount')

UG_data_long = UG_data_long.rename(columns={'Indicator Name': 'IndicatorName', 'Indicator Code': 'IndicatorCode'})

UG_data_long['Year'] = UG_data_long['Year'].astype(int)
UG_data_long['Amount'] = UG_data_long['Amount'].astype(float)
UG_data_long = UG_data_long.dropna(subset=['Amount'])


# Add a sidebar
with st.sidebar:
    st.title('🏂 UGANDA World Bank Indicator Dashboard')
    
    year_list = list(UG_data_long.Year.unique())[::-1]
    indicator_list = list(UG_data_long.IndicatorName.unique())[::-1]
    
    selected_year = st.selectbox('Select a year', year_list, index=len(year_list)-1)
    df_selected_year = UG_data_long[UG_data_long.Year == selected_year]
    df_selected_year_sorted = df_selected_year.sort_values(by="Amount", ascending=False)

    selected_indicator = st.selectbox('Select an indicator', indicator_list, index=len(indicator_list)-1)
    df_selected_indicator = UG_data_long[UG_data_long.Year == selected_indicator]
    df_selected_indicator_sorted = df_selected_indicator.sort_values(by="Amount", ascending=False)

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)



# Plot and chart types
# Next, we’re going to define custom functions to create the various plots displayed in the dashboard.

# (1) Heatmap: A heatmap will allow us to see the indicator growth over the years
def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
            color=alt.Color(f'max({input_color}):Q',
                             legend=None,
                             scale=alt.Scale(scheme=input_color_theme)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=900
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        ) 
    # height=300
    return heatmap

# (2) Donut chart: Next, we’re going to create a donut chart for the IndicatorName performance metric in Amount.
def calculate_yearly_difference(input_df, input_year):
    selected_year_data = input_df[input_df['Year'] == input_year].reset_index()
    previous_year_data = input_df[input_df['Year'] == input_year - 1].reset_index()
    selected_year_data['yearly_difference'] = selected_year_data.Amount.sub(previous_year_data.Amount, fill_value=0)
    return pd.concat([selected_year_data.IndicatorName, selected_year_data.IndicatorCode, selected_year_data.Amount, selected_year_data.yearly_difference], axis=1).sort_values(by="yearly_difference", ascending=False)

# The donut chart is then created from the aforementioned Amount value for IndicatorName performance metric.
def make_donut(input_response, input_text, input_color):
    if input_color == 'blue':
        chart_color = ['#29b5e8', '#155F7A']
    if input_color == 'green':
        chart_color = ['#27AE60', '#12783D']
    if input_color == 'orange':
        chart_color = ['#F39C12', '#875A12']
    if input_color == 'red':
        chart_color = ['#E74C3C', '#781F16']

    source = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100-input_response, input_response]
    })
    source_bg = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100, 0]
    })
        
    
    plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
        theta="% value",
        color= alt.Color("Topic:N",
                        scale=alt.Scale(
                            #domain=['A', 'B'],
                            domain=[input_text, ''],
                            # range=['#29b5e8', '#155F7A']),  # 31333F
                            range=chart_color),
                        legend=None),
    ).properties(width=130, height=130)
        
    text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
    plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
        theta="% value",
        color= alt.Color("Topic:N",
                        scale=alt.Scale(
                            # domain=['A', 'B'],
                            domain=[input_text, ''],
                            range=chart_color),  # 31333F
                        legend=None),
    ).properties(width=130, height=130)
    return plot_bg + plot + text


# Convert indicator to text
# Next, we’ll going to create a custom function for making indicator values more concise as well as improving the aesthetics. 
# Particularly, instead of being displayed as numerical values of 28,995,881 in the metrics card to a more concised form as 29.0 M. 
# This was also applied to numerical values in the thousand range.
def format_number(num):
    if num >= 1_000_000_000_000:
        return f'{num / 1_000_000_000_000:.1f} T' if num % 1_000_000_000_000 else f'{num // 1_000_000_000_000} T'
    elif num >= 1_000_000_000:
        return f'{num / 1_000_000_000:.1f} B' if num % 1_000_000_000 else f'{num // 1_000_000_000} B'
    elif num >= 1_000_000:
        return f'{num / 1_000_000:.1f} M' if num % 1_000_000 else f'{num // 1_000_000} M'
    elif num >= 1_000:
        return f'{num / 1_000:.0f} K'
    else:
        return f'{num:,}'



# App layout
# Finally, it’s time to put everything together in the app.
# Define the layout
# Begin by creating 3 columns:

col = st.columns((1.5, 4.5, 2), gap='medium')

# Particularly, the input argument (1.5, 4.5, 2) indicated that the second column has a width of about three times that of the first column and 
# that the third column has a width about twice less than that of the second column.

# Column 1
# --------------------
# The Gain/Loss section is shown where metrics card are displaying IndicatorName with the highest Growth and Decline performance metric for the selected year (specified via the 
# Select a year drop-down widget created via st.selectbox). The IndicatorName performance metric section shows a donut chart where the Amount of IndicatorName with annual 
# Growth or Decline performance metric > 50,000 are displayed.
with col[0]:
    st.markdown('#### Growth/Decline')

    df_yearly_difference_sorted = calculate_yearly_difference(UG_data_long, selected_year)

    if selected_year > 1960:
        first_inddicator_name = df_yearly_difference_sorted.IndicatorName.iloc[0]
        first_indicator_Amount = format_number(df_yearly_difference_sorted.Amount.iloc[0])
        first_indicator_delta = format_number(df_yearly_difference_sorted.yearly_difference.iloc[0])
    else:
        first_inddicator_name = '-'
        first_indicator_Amount = '-'
        first_indicator_delta = ''
    st.metric(label=first_inddicator_name, value=first_indicator_Amount, delta=first_indicator_delta)

    if selected_year > 1960:
        last_indicator_name = df_yearly_difference_sorted.IndicatorName.iloc[-1]
        last_indicator_Amount = format_number(df_yearly_difference_sorted.Amount.iloc[-1])   
        last_indicator_delta = format_number(df_yearly_difference_sorted.yearly_difference.iloc[-1])   
    else:
        last_indicator_name = '-'
        last_indicator_Amount = '-'
        last_indicator_delta = ''
    st.metric(label=last_indicator_name, value=last_indicator_Amount, delta=last_indicator_delta)

    
    st.markdown('#### Changes in Indicators')

    if selected_year > 1960:
        # Filter IndicatorName with indicator difference > 50000
        # df_greater_50000 = df_yearly_difference_sorted[df_yearly_difference_sorted.yearly_difference_absolute > 50000]
        df_greater_50000 = df_yearly_difference_sorted[df_yearly_difference_sorted.yearly_difference > 50000]
        df_less_50000 = df_yearly_difference_sorted[df_yearly_difference_sorted.yearly_difference < -50000]
        
        # % of IndicatorName with indicator difference > 50000
        indicator_changes_greater = round((len(df_greater_50000)/df_yearly_difference_sorted.IndicatorName.nunique())*100)
        indicator_changes_less = round((len(df_less_50000)/df_yearly_difference_sorted.IndicatorName.nunique())*100)
        donut_chart_greater = make_donut(indicator_changes_greater, 'Growth', 'green')
        donut_chart_less = make_donut(indicator_changes_less, 'Decline', 'red')
    else:
        indicator_changes_greater = 0
        indicator_changes_less = 0
        donut_chart_greater = make_donut(indicator_changes_greater, 'Growth', 'green')
        donut_chart_less = make_donut(indicator_changes_less, 'Decline', 'red')

    variables_col = st.columns((0.2, 1, 0.2))
    with variables_col[1]:
        st.write('Growth')
        st.altair_chart(donut_chart_greater)
        st.write('Decline')
        st.altair_chart(donut_chart_less)



# Column 2
# ---------------------
def make_choropleth(input_df, input_id, input_column, input_color_theme):
    choropleth = px.choropleth(
        input_df,
        locations=input_id,  # should contain country names like "Uganda"
        locationmode='country names',
        color=input_column,
        color_continuous_scale=input_color_theme,
        scope="africa",  # focuses on Africa
        labels={'Amount': 'Amount'}
    )
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth


df_selected_year = pd.DataFrame({
    "Country": ["Uganda"],
    "Amount": [73.2]
})


with col[1]:
    st.markdown('#### ') # st.markdown('#### Total Amount')
    
    # choropleth = make_choropleth(df_selected_year, 'states_code', 'population', selected_color_theme)
    # st.plotly_chart(choropleth, use_container_width=True)
    
    heatmap = make_heatmap(UG_data_long, 'Year','Amount', selected_color_theme)
    st.altair_chart(heatmap, use_container_width=True)

    choropleth = make_choropleth(df_selected_year, 'Country', 'Amount', 'Viridis')
    st.plotly_chart(choropleth, use_container_width=True)



# Column 3
# -----------------
# Finally, the third column shows the top metrics via a dataframe whereby the Amounts are shown as a colored progress bar via the column_config parameter of st.dataframe.
# An About section is displayed via the st.expander() container to provide information on the data source and definitions for terminologies used in the dashboard.

with col[2]:
    st.markdown('#### Top metrics')

    st.dataframe(df_selected_year_sorted,
                 column_order=("Year","IndicatorName", "Amount"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "IndicatorName": st.column_config.TextColumn(
                        "Indicator",
                    ),
                    "Amount": st.column_config.ProgressColumn(
                        "Amount",
                        format="%f",
                        min_value=0,
                        max_value=max(df_selected_year_sorted.Amount),
                     )}
                 )
    
    with st.expander('About', expanded=True):
        st.write('''
            - Data: [UGA World Bank Indicator](<https://raw.githubusercontent.com/AwanyDenis/Uganda-WB-Indicator/main/data/API_UGA_DS2_en_csv_v2_93736.csv>).
            - :orange[**Growth/Decline**]: Metrics with high Growth/ Declines for selected year
            ''')





