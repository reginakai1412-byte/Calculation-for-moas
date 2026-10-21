import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from io import BytesIO
from scipy import stats


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def make_excel(dataframes):
    """Menggabungkan beberapa tabel ke dalam satu file Excel."""
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet_name, dataframe in dataframes.items():
            if dataframe is not None and not dataframe.empty:
                dataframe.to_excel(
                    writer,
                    sheet_name=sheet_name[:31],
                    index=False
                )

    output.seek(0)
    return output.getvalue()


def get_numeric_data(df):
    """Mengambil kolom numerik dan membersihkan nilai tidak valid."""
    numeric_df = df.select_dtypes(include=np.number).copy()

    numeric_df = numeric_df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    return numeric_df


def calculate_statistics(data, ddof=1):
    """Menghitung statistik deskriptif."""
    data = pd.to_numeric(
        pd.Series(data),
        errors="coerce"
    ).replace([np.inf, -np.inf], np.nan).dropna()

    if data.empty:
        return {}

    variance = data.var(ddof=ddof)
    std_dev = data.std(ddof=ddof)

    return {
        "Jumlah Data": len(data),
        "Mean": data.mean(),
        "Median": data.median(),
        "Modus": data.mode().tolist(),
        "Minimum": data.min(),
        "Maksimum": data.max(),
        "Rentang": data.max() - data.min(),
        "Varians": variance,
        "Standar Deviasi": std_dev,
        "Q1": data.quantile(0.25),
        "Q2": data.quantile(0.50),
        "Q3": data.quantile(0.75),
    }


# ==========================================
# MAIN APP
# ==========================================

def run_app():

    st.title("📊 MOA Statistics")
    st.caption("Turn Data Into Dream 💚")
    st.write(
        "Aplikasi pengolahan data statistik untuk membantu "
        "menganalisis dataset secara praktis."
    )

    st.divider()

    # ======================================
    # UPLOAD DATASET
    # ======================================

    st.subheader("📂 Upload Dataset")

    uploaded_file = st.file_uploader(
        "Unggah file CSV atau Excel",
        type=["csv", "xlsx"],
        key="statistics_upload"
    )

    if uploaded_file is None:
        st.info(
            "Unggah dataset CSV atau Excel untuk mulai "
            "melakukan analisis statistik."
        )
        return

    # ======================================
    # READ DATA
    # ======================================

    try:
        if uploaded_file.name.lower().endswith(".csv"):
            try:
                df = pd.read_csv(uploaded_file)
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                df = pd.read_csv(
                    uploaded_file,
                    encoding="latin-1"
                )

        else:
            df = pd.read_excel(uploaded_file)

    except Exception as e:
        st.error(f"Dataset gagal dibaca: {e}")
        return

    if df.empty:
        st.warning("Dataset kosong. Silakan unggah dataset lain.")
        return

    # ======================================
    # DATA PREVIEW
    # ======================================

    st.success("Dataset berhasil dibaca!")

    st.subheader("👀 Preview Dataset")

    col1, col2, col3 = st.columns(3)

    col1.metric("Jumlah Baris", df.shape[0])
    col2.metric("Jumlah Kolom", df.shape[1])
    col3.metric("Total Sel", df.size)

    st.dataframe(
        df,
        use_container_width=True
    )

    # ======================================
    # DATA QUALITY
    # ======================================

    st.divider()
    st.subheader("🔎 Pemeriksaan Kualitas Data")

    missing_values = df.isnull().sum()

    missing_table = pd.DataFrame({
        "Kolom": missing_values.index,
        "Jumlah Data Kosong": missing_values.values
    })

    missing_table["Persentase Data Kosong (%)"] = (
        missing_table["Jumlah Data Kosong"]
        / len(df) * 100
    ).round(2)

    duplicate_count = int(df.duplicated().sum())

    col1, col2 = st.columns(2)

    col1.metric(
        "Total Data Kosong",
        int(df.isnull().sum().sum())
    )

    col2.metric(
        "Baris Duplikat",
        duplicate_count
    )

    st.write("**Rincian Data Kosong per Kolom**")

    st.dataframe(
        missing_table,
        use_container_width=True
    )

    # ======================================
    # NUMERIC DATA
    # ======================================

    numeric_df = get_numeric_data(df)

    st.divider()
    st.subheader("📊 Analisis Statistik Deskriptif")

    if numeric_df.empty:
        st.warning(
            "Dataset tidak memiliki kolom numerik yang "
            "bisa dianalisis."
        )
        return

    st.write(
        "Pilih apakah perhitungan varians dan standar deviasi "
        "menggunakan rumus sampel atau populasi."
    )

    calculation_type = st.radio(
        "Jenis Perhitungan",
        ["Sampel", "Populasi"],
        horizontal=True,
        key="statistics_calculation_type"
    )

    ddof = 1 if calculation_type == "Sampel" else 0

    # ======================================
    # SINGLE VARIABLE STATISTICS
    # ======================================

    selected_column = st.selectbox(
        "Pilih variabel numerik",
        numeric_df.columns.tolist(),
        key="statistics_selected_column"
    )

    data = numeric_df[selected_column].dropna()

    if data.empty:
        st.warning(
            "Kolom yang dipilih tidak memiliki data numerik valid."
        )
        return

    result = calculate_statistics(data, ddof)

    st.markdown(f"### Hasil untuk variabel: `{selected_column}`")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Jumlah Data",
        result["Jumlah Data"]
    )

    col2.metric(
        "Mean",
        f"{result['Mean']:.4f}"
    )

    col3.metric(
        "Median",
        f"{result['Median']:.4f}"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Minimum",
        f"{result['Minimum']:.4f}"
    )

    col2.metric(
        "Maksimum",
        f"{result['Maksimum']:.4f}"
    )

    col3.metric(
        "Rentang",
        f"{result['Rentang']:.4f}"
    )

    variance = result["Varians"]
    std_dev = result["Standar Deviasi"]

    col1, col2 = st.columns(2)

    col1.metric(
        f"Varians {calculation_type.lower()}",
        f"{variance:.4f}" if pd.notna(variance)
        else "Tidak tersedia"
    )

    col2.metric(
        f"Standar deviasi {calculation_type.lower()}",
        f"{std_dev:.4f}" if pd.notna(std_dev)
        else "Tidak tersedia"
    )

    st.write("**Modus:**", result["Modus"])
    st.write("**Kuartil:**")

    quartile_table = pd.DataFrame({
        "Kuartil": ["Q1 (25%)", "Q2 (50%)", "Q3 (75%)"],
        "Nilai": [
            result["Q1"],
            result["Q2"],
            result["Q3"]
        ]
    })

    st.dataframe(
        quartile_table,
        use_container_width=True
    )

    # ======================================
    # DESCRIPTIVE STATISTICS TABLE
    # ======================================

    descriptive_table = pd.DataFrame({
        "Statistik": list(result.keys()),
        "Nilai": [
            ", ".join(map(str, value))
            if isinstance(value, list)
            else value
            for value in result.values()
        ]
    })

    st.subheader("📋 Tabel Statistik Deskriptif")

    st.dataframe(
        descriptive_table,
        use_container_width=True
    )

    # ======================================
    # HISTOGRAM
    # ======================================

    st.divider()
    st.subheader("📈 Histogram")

    fig_hist = px.histogram(
        x=data,
        nbins="auto",
        title=f"Distribusi {selected_column}",
        labels={"x": selected_column, "y": "Frekuensi"}
    )

    st.plotly_chart(
        fig_hist,
        use_container_width=True
    )

    # ======================================
    # BOXPLOT
    # ======================================

    st.subheader("📦 Boxplot")

    fig_box = px.box(
        y=data,
        title=f"Boxplot {selected_column}",
        labels={"y": selected_column}
    )

    st.plotly_chart(
        fig_box,
        use_container_width=True
    )

    # ======================================
    # MULTIPLE VARIABLE STATISTICS
    # ======================================

    st.divider()
    st.subheader("📊 Statistik Beberapa Variabel")

    multi_rows = []

    for column in numeric_df.columns:
        column_data = numeric_df[column].dropna()

        if column_data.empty:
            continue

        column_result = calculate_statistics(
            column_data,
            ddof
        )

        multi_rows.append({
            "Variabel": column,
            "Jumlah Data": column_result["Jumlah Data"],
            "Mean": column_result["Mean"],
            "Median": column_result["Median"],
            "Minimum": column_result["Minimum"],
            "Maksimum": column_result["Maksimum"],
            "Varians": column_result["Varians"],
            "Standar Deviasi": column_result["Standar Deviasi"]
        })

    multiple_statistics = pd.DataFrame(multi_rows)

    st.dataframe(
        multiple_statistics,
        use_container_width=True
    )

    # ======================================
    # CORRELATION
    # ======================================

    st.divider()
    st.subheader("🔗 Analisis Korelasi")

    correlation_df = numeric_df.dropna(axis=1, how="all")

    if correlation_df.shape[1] >= 2:

        correlation_method = st.selectbox(
            "Pilih metode korelasi",
            ["Pearson", "Spearman", "Kendall"],
            key="statistics_correlation_method"
        )

        if correlation_method == "Pearson":
            correlation_matrix = correlation_df.corr(
                method="pearson"
            )
        elif correlation_method == "Spearman":
            correlation_matrix = correlation_df.corr(
                method="spearman"
            )
        else:
            correlation_matrix = correlation_df.corr(
                method="kendall"
            )

        st.write(
            f"Matriks korelasi menggunakan metode "
            f"**{correlation_method}**."
        )

        st.dataframe(
            correlation_matrix,
            use_container_width=True
        )

        fig_corr = px.imshow(
            correlation_matrix,
            text_auto=".2f",
            aspect="auto",
            title=f"Matriks Korelasi {correlation_method}"
        )

        st.plotly_chart(
            fig_corr,
            use_container_width=True
        )

        st.caption(
            "Korelasi menunjukkan hubungan antarvariabel, "
            "tetapi tidak otomatis membuktikan sebab-akibat."
        )

    else:
        st.info(
            "Analisis korelasi memerlukan setidaknya "
            "dua kolom numerik."
        )

    # ======================================
    # SIMPLE LINEAR REGRESSION
    # ======================================

    st.divider()
    st.subheader("📉 Regresi Linear Sederhana")

    if numeric_df.shape[1] >= 2:

        regression_columns = numeric_df.columns.tolist()

        x_column = st.selectbox(
            "Variabel bebas (X)",
            regression_columns,
            index=0,
            key="statistics_regression_x"
        )

        y_options = [
            column for column in regression_columns
            if column != x_column
        ]

        if y_options:

            y_column = st.selectbox(
                "Variabel terikat (Y)",
                y_options,
                key="statistics_regression_y"
            )

            regression_data = numeric_df[
                [x_column, y_column]
            ].dropna()

            if len(regression_data) >= 2:

                x = regression_data[x_column]
                y = regression_data[y_column]

                if x.nunique() >= 2:

                    regression = stats.linregress(x, y)

                    slope = regression.slope
                    intercept = regression.intercept
                    r_value = regression.rvalue
                    p_value = regression.pvalue
                    r_squared = r_value ** 2

                    st.write(
                        "**Persamaan regresi:** "
                        f"Y = {slope:.4f}X "
                        f"{intercept:+.4f}"
                    )

                    col1, col2, col3 = st.columns(3)

                    col1.metric(
                        "Slope",
                        f"{slope:.4f}"
                    )

                    col2.metric(
                        "Intercept",
                        f"{intercept:.4f}"
                    )

                    col3.metric(
                        "R²",
                        f"{r_squared:.4f}"
                    )

                    st.write(
                        f"**P-value:** {p_value:.6f}"
                    )

                    regression_plot = pd.DataFrame({
                        x_column: x,
                        y_column: y
                    })

                    fig_reg = px.scatter(
                        regression_plot,
                        x=x_column,
                        y=y_column,
                        title="Regresi Linear Sederhana",
                        trendline="ols"
                    )

                    st.plotly_chart(
                        fig_reg,
                        use_container_width=True
                    )

                else:
                    st.warning(
                        "Variabel X harus memiliki setidaknya "
                        "dua nilai berbeda."
                    )

            else:
                st.warning(
                    "Data valid terlalu sedikit untuk regresi."
                )

    else:
        st.info(
            "Regresi memerlukan setidaknya dua kolom numerik."
        )

    # ======================================
    # DOWNLOAD RESULTS
    # ======================================

    st.divider()
    st.subheader("⬇️ Download Hasil Analisis")

    csv_data = descriptive_table.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "Download Statistik Deskriptif (CSV)",
        data=csv_data,
        file_name="statistik_deskriptif.csv",
        mime="text/csv",
        key="statistics_download_csv"
    )

    excel_tables = {
        "Statistik Deskriptif": descriptive_table,
        "Statistik Semua Variabel": multiple_statistics,
        "Data Kosong": missing_table
    }

    if "correlation_matrix" in locals():
        excel_tables["Korelasi"] = (
            correlation_matrix
            .rename_axis("Variabel")
            .reset_index()
        )

    excel_data = make_excel(excel_tables)

    st.download_button(
        "Download Hasil Analisis (Excel)",
        data=excel_data,
        file_name="hasil_analisis_moa.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        key="statistics_download_excel"
    )

    st.divider()

    st.caption(
        "💚 Calculator for MOAs — Turn Data Into Dream"
    )
