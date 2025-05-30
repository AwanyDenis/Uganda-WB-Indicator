## # QN: How do the different indicator metric evolve over time and how do they compare to each other?
# print((UG_data_subset.columns))

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
UG_data = pd.read_csv("https://github.com/AwanyDenis/Uganda-WB-Indicator/main/data/API_UGA_DS2_en_csv_v2_93736.csv", skiprows=3)


# UG_data.columns
UG_data_subset = UG_data.drop(['Country Name','Country Code','Unnamed: 69'], axis=1)
year_cols = UG_data_subset.columns[2:]

UG_data_long = UG_data_subset.melt(id_vars=['Indicator Name','Indicator Code'],
    value_vars=year_cols, var_name='Year', value_name='Percentage')

UG_data_long = UG_data_long.rename(columns={'Indicator Name': 'IndicatorName', 'Indicator Code': 'IndicatorCode'})

UG_data_long['Year'] = UG_data_long['Year'].astype(int)


# Add a sidebar

with st.sidebar:
    st.title('🏂 UGANDA World Bank Indicator Dashboard')
    
    year_list = list(UG_data_long.Year.unique())[::-1]
    
    selected_year = st.selectbox('Select a year', year_list, index=len(year_list)-1)
    df_selected_year = UG_data_long[UG_data_long.Year == selected_year]
    df_selected_year_sorted = df_selected_year.sort_values(by="Percentage", ascending=False)

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

# (2) # Donut chart: Next, we’re going to create a donut chart for the IndicatorName migration in percentage.
def calculate_yearly_difference(input_df, input_year):
    selected_year_data = input_df[input_df['Year'] == input_year].reset_index()
    previous_year_data = input_df[input_df['Year'] == input_year - 1].reset_index()
    selected_year_data['yearly_difference'] = selected_year_data.Percentage.sub(previous_year_data.Percentage, fill_value=0)
    return pd.concat([selected_year_data.IndicatorName, selected_year_data.IndicatorCode, selected_year_data.Percentage, selected_year_data.yearly_difference], axis=1).sort_values(by="yearly_difference", ascending=False)

# The donut chart is then created from the aforementioned percentage value for IndicatorName migration.
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
    if num > 1000000:
        if not num % 1000000:
            return f'{num // 1000000} M'
        return f'{round(num / 1000000, 1)} M'
    return f'{num // 1000} K'



# App layout
# Finally, it’s time to put everything together in the app.
# Define the layout
# Begin by creating 3 columns:

col = st.columns((1.5, 4.5, 2), gap='medium')

# Particularly, the input argument (1.5, 4.5, 2) indicated that the second column has a width of about three times that of the first column and 
# that the third column has a width about twice less than that of the second column.

# Column 1
# The Gain/Loss section is shown where metrics card are displaying IndicatorName with the highest inbound and outbound migration for the selected year (specified via the 
# Select a year drop-down widget created via st.selectbox). The IndicatorName migration section shows a donut chart where the percentage of IndicatorName with annual 
# inbound or outbound migration > 50,000 are displayed.
with col[0]:
    st.markdown('#### Gains/Losses')

    df_percentage_difference_sorted = calculate_yearly_difference(UG_data_long, selected_year)

    if selected_year > 1960:
        first_inddicator_name = df_percentage_difference_sorted.IndicatorName.iloc[0]
        first_indicator_percentage = format_number(df_percentage_difference_sorted.Percentage.iloc[0])
        first_indicator_delta = format_number(df_percentage_difference_sorted.Percentage_difference.iloc[0])
    else:
        first_inddicator_name = '-'
        first_indicator_percentage = '-'
        first_indicator_delta = ''
    st.metric(label=first_inddicator_name, value=first_indicator_percentage, delta=first_indicator_delta)

    if selected_year > 1960:
        last_indicator_name = df_percentage_difference_sorted.IndicatorName.iloc[-1]
        last_indicator_percentage = format_number(df_percentage_difference_sorted.Percentage.iloc[-1])   
        last_indicator_delta = format_number(df_percentage_difference_sorted.Percentage_difference.iloc[-1])   
    else:
        last_indicator_name = '-'
        last_indicator_percentage = '-'
        last_indicator_delta = ''
    st.metric(label=last_indicator_name, value=last_indicator_percentage, delta=last_indicator_delta)

    
    st.markdown('#### Changes in Indicators')

    if selected_year > 1960:
        # Filter IndicatorName with indicator difference > 50000
        # df_greater_50000 = df_percentage_difference_sorted[df_percentage_difference_sorted.Percentage_difference_absolute > 50000]
        df_greater_50000 = df_percentage_difference_sorted[df_percentage_difference_sorted.Percentage_difference > 50000]
        df_less_50000 = df_percentage_difference_sorted[df_percentage_difference_sorted.Percentage_difference < -50000]
        
        # % of IndicatorName with indicator difference > 50000
        indicator_changes_greater = round((len(df_greater_50000)/df_percentage_difference_sorted.IndicatorName.nunique())*100)
        indicator_changes_less = round((len(df_less_50000)/df_percentage_difference_sorted.IndicatorName.nunique())*100)
        donut_chart_greater = make_donut(indicator_changes_greater, 'Inbound Change', 'green')
        donut_chart_less = make_donut(indicator_changes_less, 'Outbound Change', 'red')
    else:
        indicator_changes_greater = 0
        indicator_changes_less = 0
        donut_chart_greater = make_donut(indicator_changes_greater, 'Inbound Change', 'green')
        donut_chart_less = make_donut(indicator_changes_less, 'Outbound Change', 'red')

    migrations_col = st.columns((0.2, 1, 0.2))
    with migrations_col[1]:
        st.write('Inbound')
        st.altair_chart(donut_chart_greater)
        st.write('Outbound')
        st.altair_chart(donut_chart_less)


# Column 3
# Finally, the third column shows the top indicators via a dataframe whereby the percentages are shown as a colored progress bar via the column_config parameter of st.dataframe.
# An About section is displayed via the st.expander() container to provide information on the data source and definitions for terminologies used in the dashboard.

with col[2]:
    st.markdown('#### Top Indicators')

    st.dataframe(df_selected_year_sorted,
                 column_order=("IndicatorName", "Percentage"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "IndicatorName": st.column_config.TextColumn(
                        "Indicator",
                    ),
                    "Percentage": st.column_config.ProgressColumn(
                        "Percentage",
                        format="%f",
                        min_value=0,
                        max_value=max(df_selected_year_sorted.Percentage),
                     )}
                 )
    
    with st.expander('About', expanded=True):
        st.write('''
            - Data: [UGA World Bank Indicator](<https://github.com/AwanyDenis/Uganda-WB-Indicator/main/data/API_UGA_DS2_en_csv_v2_93736.csv>).
            - :orange[**Gains/Losses**]: Indicators with high inbound/ outbound changes for selected year
            - :orange[**Indicator Changes**]: percentage of indicators with annual inbound/ outbound changes > 50,000
            ''')





