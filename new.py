import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages

# ================= Step 1: Teeno CSV files ko load kiya =================
# r lagaya hai taaki Windows path mein error na aaye
df1 = pd.read_csv(r"D:\Python Project\Indian Job Market Trends Analyzer\Cleaned_tech_layoffs.csv")
df2 = pd.read_csv(r"D:\Python Project\Indian Job Market Trends Analyzer\layoffs_location_with_coordinates.csv")
df3 = pd.read_csv(r"D:\Python Project\Indian Job Market Trends Analyzer\tech_layoffs_til_2025.csv")

# ================= Step 2: Merge se pehle Columns rename kiye =================
# Taaki Pandas ko pata chale ki 'usstate' aur 'USState' ek hi cheez hai
df1.rename(columns={'usstate': 'State', 'location_HQ': 'Location_HQ'}, inplace=True)
df2.rename(columns={'location_HQ': 'Location_HQ'}, inplace=True)
df3.rename(columns={'USState': 'State', 'location_HQ': 'Location_HQ'}, inplace=True)

# ================= Step 3: Saare data ko ek saath Joda (Merge) =================
df = pd.concat([df1, df2, df3], ignore_index=True)

# Agar extra USState column bacha ho toh use State mein merge karke uda diya
if 'USState' in df.columns:
    df['State'] = df['State'].fillna(df['USState'])
    df.drop(columns=['USState'], inplace=True)

# ================= Step 4: Data ki Safai (Cleaning) =================
# Jahan missing value hai wahan 0 ya 'Unknown' bhar diya
df['Laid_Off'] = df['Laid_Off'].fillna(0)
df['Percentage'] = df['Percentage'].fillna(0)
df['Industry'] = df['Industry'].fillna('Unknown')
df['Stage'] = df['Stage'].fillna('Unknown')
df['Company_Size_before_Layoffs'] = df['Company_Size_before_Layoffs'].fillna(0)
df['Company_Size_after_layoffs'] = df['Company_Size_after_layoffs'].fillna(0)
df['Money_Raised_in__mil'] = df['Money_Raised_in__mil'].fillna(0)
df['State'] = df['State'].fillna('Unknown')

# Jis row mein Company ka naam hi nahi hai, use delete kar diya
df.dropna(subset=['Company'], inplace=True)

# Faltu Serial Number (Nr) column ko hata diya
if 'Nr' in df.columns:
    df.drop(columns=['Nr'], inplace=True)

# Date ko sahi format mein badla aur Saal (Year) ka naya column banaya
df['Date_layoffs'] = pd.to_datetime(df['Date_layoffs'])
df['Year'] = df['Date_layoffs'].dt.year

# ================= Step 5: Analysis ke liye Numbers nikalna =================
# Top 10 Companies aur Industries ka total layoff calculate kiya
top_10_companies = df.groupby('Company')['Laid_Off'].sum().sort_values(ascending=False).head(10)
top_10_industries = df.groupby('Industry')['Laid_Off'].sum().sort_values(ascending=False).head(10)
yearly_layoffs = df.groupby('Year')['Laid_Off'].sum()

# ================= Step 6: Ek hi PDF mein saare Charts Save karna =================
# Ye path folder ka hai jahan PDF banegi
pdf_path = r"D:\Python Project\Indian Job Market Trends Analyzer\Layoffs_Report.pdf"

print("Bhai, PDF taiyaar ho rahi hai... Thoda sabar kar!")

with PdfPages(pdf_path) as pdf:

    # --- Chart 1: Top 10 Companies Bar Plot ---
    plt.figure(figsize=(12, 6))
    sns.barplot(x=top_10_companies.index, y=top_10_companies.values, palette='coolwarm')
    plt.title('Top 10 Companies by Total Layoffs', fontsize=15)
    plt.xticks(rotation=45)
    plt.tight_layout()
    pdf.savefig() # Page 1 Save
    plt.close()

    # --- Chart 2: Top 10 Industries Bar Plot ---
    plt.figure(figsize=(12, 6))
    sns.barplot(x=top_10_industries.index, y=top_10_industries.values, palette='viridis')
    plt.title('Top 10 Industries by Total Layoffs (2020-2025)', fontsize=15)
    plt.xticks(rotation=45)
    plt.tight_layout()
    pdf.savefig() # Page 2 Save
    plt.close()

    # --- Chart 3: Distribution Boxplot (Outliers dekhne ke liye) ---
    top_5_ind = df.groupby('Industry')['Laid_Off'].sum().sort_values(ascending=False).head(5).index
    df_top_5 = df[df['Industry'].isin(top_5_ind)]
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Industry', y='Laid_Off', data=df_top_5)
    plt.title('Layoffs Distribution (Top 5 Industries)', fontsize=15)
    plt.yscale('log') # Zyada gap hone ki wajah se log scale use kiya
    plt.tight_layout()
    pdf.savefig() # Page 3 Save
    plt.close()

    # --- Chart 4: Funding vs Layoffs (Scatter Plot) ---
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='Money_Raised_in__mil', y='Laid_Off', alpha=0.5, hue='Industry')
    plt.xscale('log')
    plt.yscale('log')
    plt.title('Relationship: Money Raised vs Employees Laid Off', fontsize=15)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
    plt.tight_layout()
    pdf.savefig() # Page 4 Save
    plt.close()

    # --- Chart 5: Global Hotspots (Map Jaisa View) ---
    plt.figure(figsize=(12, 8))
    plt.scatter(df['longitude'], df['latitude'], s=df['Laid_Off']/10, c=df['Money_Raised_in__mil'], alpha=0.5, cmap='Reds')
    plt.colorbar(label='Money Raised (in millions)')
    plt.title('Global Layoffs Hotspots (Size=Layoffs, Color=Funding)', fontsize=15)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    pdf.savefig() # Page 5 Save
    plt.close()

    # --- Chart 6: Year-wise Trend ---
    plt.figure(figsize=(10, 6))
    sns.barplot(x=yearly_layoffs.index, y=yearly_layoffs.values, palette='magma')
    plt.title('Year-wise Total Layoffs Trend', fontsize=15)
    plt.tight_layout()
    pdf.savefig() # Page 6 Save
    plt.close()

    # --- Chart 7: Top 10 Companies Heatmap (Saal-dar-Saal) ---
    top_10_list = top_10_companies.index.tolist()
    pivot_heat = df[df['Company'].isin(top_10_list)].pivot_table(
        values='Laid_Off', index='Company', columns='Year', aggfunc='sum', fill_value=0
    )
    
    if not pivot_heat.empty:
        plt.figure(figsize=(12, 6))
        sns.heatmap(pivot_heat, annot=True, fmt='.0f', cmap='YlOrRd')
        plt.title('Heatmap: Top 10 Companies Yearly Layoffs', fontsize=15)
        plt.tight_layout()
        pdf.savefig() # Page 7 Save
        plt.close()

# Block khatam hote hi PDF file "Save & Close" ho jayegi
print(f"Bhai, Saare charts ek hi PDF mein save ho gaye hain: {pdf_path}")