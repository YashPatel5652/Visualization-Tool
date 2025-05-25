import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from io import BytesIO
from fpdf import FPDF
import tempfile
import os
from PIL import Image

st.set_page_config(page_title="📊 Data Visualization Tool", layout="wide")
st.title("📊 Data Visualization Tool")

# Sidebar filters
st.sidebar.header("🔍 Filter Data")

uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type="csv")

# Initialize session state for plot type selection
if "plot_type" not in st.session_state:
    st.session_state.plot_type = None

# Filter options in the sidebar when file is uploaded
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.sidebar.subheader("🔢 Filter Data")
    filter_column = st.sidebar.selectbox("Select column to filter by", df.columns.tolist())
    filter_value = st.sidebar.text_input(f"Enter filter value for {filter_column}", "")
    
    # Apply filter if a filter value is provided
    if filter_value:
        df = df[df[filter_column].astype(str).str.contains(filter_value, case=False, na=False)]
        st.sidebar.write(f"Filtered dataset based on `{filter_column}` containing `{filter_value}`")
        
    st.subheader("📋 Dataset Preview")
    st.dataframe(df.head())

    # Plotting options in the sidebar
    all_columns = df.columns.tolist()
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

    st.sidebar.subheader("📈 Choose a Plot Type")
    plot_options = [
        "Scatter Plot", "Line Plot", "Histogram", "Box Plot", "Heatmap",
        "Area Plot", "Bar Plot", "Pie Chart", "Violin Plot",
        "Bubble Chart", "Treemap", "Sunburst Chart"
    ]
    st.session_state.plot_type = st.sidebar.selectbox("Select Plot Type", plot_options)
    plot_type = st.session_state.plot_type

    if plot_type:
        st.markdown(f"### 📍 Selected Plot: `{plot_type}`")
        lib_choice = st.sidebar.radio("Choose Visualization Library", ["Plotly (Interactive)", "Matplotlib/Seaborn"])

        # Additional column selections
        x_col = y_col = size_col = None

        if plot_type not in ["Heatmap", "Pairplot", "Pie Chart", "Treemap", "Sunburst Chart"]:
            x_col = st.sidebar.selectbox("X-Axis", all_columns)
            if plot_type != "Histogram":
                y_col = st.sidebar.selectbox("Y-Axis", numeric_columns)

        if plot_type == "Bubble Chart":
            size_col = st.sidebar.selectbox("Size by", numeric_columns)

        if plot_type in ["Pie Chart", "Treemap", "Sunburst Chart"]:
            cat_col = st.sidebar.selectbox("Category Column", all_columns)
            val_col = st.sidebar.selectbox("Value Column", numeric_columns)

        # Insights on sidebar or main area
        st.subheader("📌 Overview / Insight")
        if plot_type != "Heatmap" and y_col:
            st.markdown(f"- **Average `{y_col}`**: `{df[y_col].mean():.2f}`")
            st.markdown(f"- **Min `{y_col}`**: `{df[y_col].min():.2f}`")
            st.markdown(f"- **Max `{y_col}`**: `{df[y_col].max():.2f}`")
        elif plot_type == "Heatmap":
            st.markdown("🧊 **Heatmap Insight**: Stronger colors show higher correlation among numerical variables.")

        # Plot rendering (Plotly / Matplotlib)
        if lib_choice == "Plotly (Interactive)":
            if plot_type == "Scatter Plot":
                fig = px.scatter(df, x=x_col, y=y_col)
            elif plot_type == "Line Plot":
                fig = px.line(df, x=x_col, y=y_col)
            elif plot_type == "Histogram":
                fig = px.histogram(df, x=x_col)
            elif plot_type == "Box Plot":
                fig = px.box(df, x=x_col, y=y_col)
            elif plot_type == "Heatmap":
                fig = px.imshow(df[numeric_columns].corr(), text_auto=True)
            elif plot_type == "Area Plot":
                fig = px.area(df, x=x_col, y=y_col)
            elif plot_type == "Bar Plot":
                fig = px.bar(df, x=x_col, y=y_col)
            elif plot_type == "Pie Chart":
                fig = px.pie(df, names=cat_col, values=val_col)
            elif plot_type == "Bubble Chart":
                fig = px.scatter(df, x=x_col, y=y_col, size=size_col, color=x_col)
            elif plot_type == "Treemap":
                fig = px.treemap(df, path=[cat_col], values=val_col)
            elif plot_type == "Sunburst Chart":
                fig = px.sunburst(df, path=[cat_col], values=val_col)
            else:
                fig = px.scatter(df, x=x_col, y=y_col)
            st.plotly_chart(fig, use_container_width=True)

            # Download plot
            with BytesIO() as buf:
                fig.write_image(buf, format="png")
                st.download_button("📥 Download Plot (PNG)", buf.getvalue(), file_name="plot.png", mime="image/png")

        else:
            plt.figure(figsize=(10, 6))
            if plot_type == "Scatter Plot":
                sns.scatterplot(data=df, x=x_col, y=y_col)
            elif plot_type == "Line Plot":
                sns.lineplot(data=df, x=x_col, y=y_col)
            elif plot_type == "Histogram":
                sns.histplot(data=df, x=x_col, bins=30, kde=True)
            elif plot_type == "Box Plot":
                sns.boxplot(data=df, x=x_col, y=y_col)
            elif plot_type == "Heatmap":
                sns.heatmap(df[numeric_columns].corr(), annot=True, cmap="coolwarm")
            elif plot_type == "Area Plot":
                df.set_index(x_col)[y_col].plot.area()
            elif plot_type == "Bar Plot":
                sns.barplot(data=df, x=x_col, y=y_col)
            elif plot_type == "Violin Plot":
                sns.violinplot(data=df, x=x_col, y=y_col)
            else:
                sns.lineplot(data=df, x=x_col, y=y_col)

            st.pyplot(plt)

        if st.sidebar.button("📄 Export as PDF"):
            pdf = FPDF()
            pdf.add_page()

            # Title
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, txt="Data Visualization Report", ln=True, align="C")

            # Plot Title
            pdf.ln(10)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(200, 10, txt=f"Selected Plot: {plot_type}", ln=True)

            # Insights
            pdf.ln(10)
            pdf.set_font("Arial", size=12)
            if plot_type != "Heatmap" and y_col:
                avg = df[y_col].mean()
                min_val = df[y_col].min()
                max_val = df[y_col].max()
                pdf.multi_cell(0, 10, f"Avg {y_col}: {avg:.2f}\nMin {y_col}: {min_val:.2f}\nMax {y_col}: {max_val:.2f}")
            elif plot_type == "Heatmap":
                pdf.multi_cell(0, 10, "Heatmap Insight: Stronger colors show higher correlation among numerical variables.")

            # Save plot to image buffer
            with BytesIO() as buf:
                if lib_choice == "Plotly (Interactive)":
                    fig.write_image(buf, format="png")
                else:
                    plt.savefig(buf, format="png", bbox_inches='tight')
                buf.seek(0)
                img = Image.open(buf)

                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                    img.save(tmp_file, format="PNG")
                    tmp_img_path = tmp_file.name

            # Add image from temp file to PDF
            pdf.image(tmp_img_path, x=10, y=80, w=180)

            # Save final PDF
            import time
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            pdf_output_path = f"visualization_report_{timestamp}.pdf"
            pdf.output(pdf_output_path)

            # Clean up temp file
            os.remove(tmp_img_path)

            # Download link
            st.sidebar.markdown("[📥 Download PDF Report]./{pdf_output_path})")


else:
    st.write("Please upload a CSV file to begin.")
