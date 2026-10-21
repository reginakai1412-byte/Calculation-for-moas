import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from io import BytesIO
from scipy import stats

# ==================================================
# 1. KONFIGURASI APLIKASI
# ==================================================

st.set_page_config(
    page_title="Calculator for MOAs",
    page_icon="💚",
    layout="wide"
)

st.title("💚 Calculator for MOAs")
st.caption("Turn Data Into Dream")
st.write(
    "Aplikasi pengolahan data statistik untuk membantu "
    "pengguna memahami, menganalisis, dan memvisualisasikan data."
)

st.divider()

# ==================================================
# 2. FUNGSI BANTU
# ==================================================

def make_excel(dataframes):
    """Membuat file Excel dari beberapa tabel hasil analisis."""
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet_name, dataframe in dataframes.items():
            dataframe.to_excel(
                writer,
                sheet_name=sheet_name[:31],
                index=False
            )

    output.seek(0)
    return output.getvalue()


def get_numeric_data(df):
    """Mengambil kolom numerik dan mengubah nilai tak hingga menjadi NaN."""
    numeric = df.select_dtypes(include=np.number).copy()
    numeric = numeric.replace([np.inf, -np.inf], np.nan)
    return numeric


def calculate_statistics(data, ddof):
    """Menghitung statistik deskriptif untuk satu variabel."""
    data = pd.to_numeric(data, errors="coerce")
    data = data.replace([np.inf, -np.inf], np.nan).dropna()

    if data.empty:
        return None

    mode_values = data.mode()

    variance = data.var(ddof=ddof) if len(data) > ddof else np.nan
    std_dev = data.std(ddof=ddof) if len(data) > ddof else np.nan

    return {
        "Jumlah Data": len(data),
        "Mean": data.mean(),
        "Median": data.median(),
        "Modus": ", ".join(map(str, mode_values.tolist())),
        "Minimum": data.min(),
        "Maksimum": data.max(),
        "Rentang": data.max() - data.min(),
        "Kuartil 1": data.quantile(0.25),
        "Kuartil 2": data.quantile(0.50),
        "Kuartil 3": data.quantile(0.75),
        "Varians": variance,
        "Standar Deviasi": std_dev,
        "Skewness": data.skew() if len(data) >= 3 else np.nan,
        "Kurtosis": data.kurt() if len(data) >= 4 else np.nan
    }


# ==================================================
# 3. UPLOAD DATASET
# ==================================================

st.header("📂 Upload Dataset")

uploaded_file = st.file_uploader(
    "Unggah dataset dalam format CSV atau Excel",
    type=["csv", "xlsx"]
)

if uploaded_file is None:
    st.info(
        "Silakan unggah file CSV atau Excel untuk mulai "
        "menggunakan fitur analisis statistik."
    )

    st.markdown(
        """
        ### ✨ Fitur Calculator for MOAs

        - 📊 Statistik deskriptif
        - 📈 Histogram dan boxplot
        - 🔗 Analisis korelasi
        - 📉 Regresi linear sederhana
        - 🔎 Pemeriksaan data kosong
        - 📥 Unduh hasil analisis
        """
    )

    st.stop()


# ==================================================
# 4. MEMBACA DATASET
# ==================================================

try:
    if uploaded_file.name.lower().endswith(".csv"):
        try:
            df = pd.read_csv(uploaded_file)
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding="latin-1")
    else:
        df = pd.read_excel(uploaded_file)

    if df.empty or len(df.columns) == 0:
        st.error("Dataset kosong atau tidak memiliki kolom.")
        st.stop()

except Exception as e:
    st.error(f"Dataset gagal dibaca: {e}")
    st.stop()


# ==================================================
# 5. DASHBOARD DATASET
# ==================================================

st.success("Dataset berhasil dibaca!")

st.header("📌 Dashboard Dataset")

row_count = len(df)
column_count = len(df.columns)
missing_count = int(df.isna().sum().sum())
duplicate_count = int(df.duplicated().sum())

col1, col2, col3, col4 = st.columns(4)

col1.metric("Jumlah Baris", f"{row_count:,}")
col2.metric("Jumlah Kolom", f"{column_count:,}")
col3.metric("Data Kosong", f"{missing_count:,}")
col4.metric("Baris Duplikat", f"{duplicate_count:,}")

with st.expander("👀 Preview Dataset", expanded=True):
    st.dataframe(df, use_container_width=True)

with st.expander("ℹ️ Informasi Tipe Data"):
    information = pd.DataFrame({
        "Kolom": df.columns.astype(str),
        "Tipe Data": df.dtypes.astype(str).values,
        "Jumlah Data Terisi": df.notna().sum().values,
        "Jumlah Data Kosong": df.isna().sum().values
    })

    st.dataframe(information, use_container_width=True)


# ==================================================
# 6. PEMERIKSAAN DATA KOSONG
# ==================================================

st.divider()
st.header("🔎 Pemeriksaan Kualitas Data")

missing_table = pd.DataFrame({
    "Kolom": df.columns.astype(str),
    "Jumlah Data Kosong": df.isna().sum().values,
    "Persentase Data Kosong (%)": (
        df.isna().mean().values * 100
    ).round(2)
})

st.dataframe(missing_table, use_container_width=True)

if missing_count == 0:
    st.success("Tidak ditemukan data kosong.")
else:
    st.warning(
        f"Ditemukan {missing_count:,} sel kosong. "
        "Periksa kembali sebelum melakukan analisis."
    )

if duplicate_count > 0:
    st.info(
        f"Ditemukan {duplicate_count:,} baris duplikat. "
        "Baris tersebut tidak dihapus secara otomatis."
    )


# ==================================================
# 7. PERSIAPAN DATA NUMERIK
# ==================================================

numeric_df = get_numeric_data(df)
numeric_columns = numeric_df.columns.tolist()

if not numeric_columns:
    st.warning(
        "Dataset ini tidak memiliki kolom numerik "
        "yang dapat digunakan untuk analisis statistik."
    )

    st.stop()


# ==================================================
# 8. PILIHAN METODE PERHITUNGAN
# ==================================================

st.divider()
st.header("⚙️ Pengaturan Analisis")

variance_type = st.radio(
    "Pilih jenis perhitungan varians dan standar deviasi",
    ["Sampel", "Populasi"],
    horizontal=True
)

ddof = 1 if variance_type == "Sampel" else 0

st.caption(
    "Sampel menggunakan pembagi n − 1, sedangkan "
    "populasi menggunakan pembagi n."
)


# ==================================================
# 9. STATISTIK DESKRIPTIF
# ==================================================

st.divider()
st.header("📊 Statistik Deskriptif")

selected_column = st.selectbox(
    "Pilih variabel yang akan dianalisis",
    numeric_columns,
    key="descriptive_column"
)

selected_data = numeric_df[selected_column].dropna()

if not selected_data.empty:

    statistics_result = calculate_statistics(
        selected_data,
        ddof
    )

    if statistics_result is not None:

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Jumlah Data",
            f"{statistics_result['Jumlah Data']:,}"
        )

        col2.metric(
            "Mean",
            f"{statistics_result['Mean']:.4f}"
        )

        col3.metric(
            "Median",
            f"{statistics_result['Median']:.4f}"
        )

        col4.metric(
            "Standar Deviasi",
            (
                f"{statistics_result['Standar Deviasi']:.4f}"
                if pd.notna(statistics_result["Standar Deviasi"])
                else "Tidak tersedia"
            )
        )

        st.subheader("Tabel Statistik Lengkap")

        descriptive_table = pd.DataFrame({
            "Statistik": statistics_result.keys(),
            "Nilai": statistics_result.values()
        })

        st.dataframe(
            descriptive_table,
            use_container_width=True
        )

        st.caption(
            f"Modus: {statistics_result['Modus']}"
            if statistics_result["Modus"]
            else "Modus tidak tersedia."
        )

else:
    st.warning("Kolom ini tidak memiliki data numerik yang valid.")


# ==================================================
# 10. STATISTIK BEBERAPA VARIABEL
# ==================================================

st.divider()
st.header("📚 Analisis Beberapa Variabel")

selected_columns = st.multiselect(
    "Pilih satu atau beberapa variabel numerik",
    numeric_columns,
    default=numeric_columns
)

if selected_columns:

    all_statistics = []

    for col in selected_columns:
        result = calculate_statistics(numeric_df[col], ddof)

        if result is not None:
            result["Variabel"] = str(col)
            all_statistics.append(result)

    if all_statistics:
        multiple_statistics = pd.DataFrame(all_statistics)

        ordered_columns = ["Variabel"] + [
            col for col in multiple_statistics.columns
            if col != "Variabel"
        ]

        multiple_statistics = multiple_statistics[ordered_columns]

        st.dataframe(
            multiple_statistics,
            use_container_width=True
        )
    else:
        multiple_statistics = pd.DataFrame()
        st.warning("Tidak ada data numerik valid untuk dianalisis.")

else:
    multiple_statistics = pd.DataFrame()
    st.info("Pilih minimal satu variabel numerik.")


# ==================================================
# 11. VISUALISASI
# ==================================================

st.divider()
st.header("📈 Visualisasi Data")

chart_column = st.selectbox(
    "Pilih variabel untuk visualisasi",
    numeric_columns,
    key="chart_column"
)

chart_data = numeric_df[chart_column].dropna()

if not chart_data.empty:

    chart_tab1, chart_tab2 = st.tabs(
        ["Histogram", "Boxplot"]
    )

    with chart_tab1:

        bins = st.slider(
            "Jumlah kelompok histogram",
            min_value=5,
            max_value=50,
            value=20
        )

        histogram = px.histogram(
            x=chart_data,
            nbins=bins,
            title=f"Distribusi {chart_column}",
            labels={"x": str(chart_column), "y": "Frekuensi"}
        )

        st.plotly_chart(
            histogram,
            use_container_width=True
        )

    with chart_tab2:

        boxplot = px.box(
            y=chart_data,
            points="outliers",
            title=f"Boxplot {chart_column}",
            labels={"y": str(chart_column)}
        )

        st.plotly_chart(
            boxplot,
            use_container_width=True
        )

else:
    st.warning("Tidak ada data valid untuk dibuatkan grafik.")


# ==================================================
# 12. ANALISIS KORELASI
# ==================================================

st.divider()
st.header("🔗 Analisis Korelasi")

st.write(
    "Korelasi mengukur kekuatan dan arah hubungan "
    "antara dua variabel numerik."
)

if len(numeric_columns) >= 2:

    correlation_method = st.selectbox(
        "Metode korelasi",
        ["Pearson", "Spearman", "Kendall"]
    )

    if correlation_method == "Pearson":
        corr_method = "pearson"
    elif correlation_method == "Spearman":
        corr_method = "spearman"
    else:
        corr_method = "kendall"

    correlation_df = numeric_df[numeric_columns].corr(
        method=corr_method
    )

    st.subheader("Matriks Korelasi")

    correlation_fig = px.imshow(
        correlation_df,
        text_auto=".3f",
        aspect="auto",
        title=f"Matriks Korelasi {correlation_method}",
        color_continuous_scale="RdBu",
        zmin=-1,
        zmax=1
    )

    st.plotly_chart(
        correlation_fig,
        use_container_width=True
    )

    st.subheader("Korelasi Dua Variabel")

    corr_col1, corr_col2 = st.columns(2)

    with corr_col1:
        variable_x = st.selectbox(
            "Variabel pertama",
            numeric_columns,
            key="corr_x"
        )

    with corr_col2:
        variable_y = st.selectbox(
            "Variabel kedua",
            numeric_columns,
            index=1,
            key="corr_y"
        )

    if variable_x == variable_y:
        st.info(
            "Pilih dua variabel yang berbeda "
            "untuk menganalisis hubungan keduanya."
        )

    else:
        paired_data = numeric_df[
            [variable_x, variable_y]
        ].replace([np.inf, -np.inf], np.nan).dropna()

        if len(paired_data) < 2:
            st.warning(
                "Diperlukan minimal dua pasangan data valid."
            )

        elif (
            paired_data[variable_x].nunique() < 2
            or paired_data[variable_y].nunique() < 2
        ):
            st.warning(
                "Korelasi tidak dapat dihitung jika "
                "salah satu variabel konstan."
            )

        else:
            if corr_method == "pearson":
                coefficient, p_value = stats.pearsonr(
                    paired_data[variable_x],
                    paired_data[variable_y]
                )

            elif corr_method == "spearman":
                coefficient, p_value = stats.spearmanr(
                    paired_data[variable_x],
                    paired_data[variable_y]
                )

            else:
                coefficient, p_value = stats.kendalltau(
                    paired_data[variable_x],
                    paired_data[variable_y]
                )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Koefisien Korelasi",
                f"{coefficient:.4f}"
            )

            col2.metric(
                "P-value",
                f"{p_value:.4g}"
            )

            col3.metric(
                "Jumlah Pasangan Data",
                f"{len(paired_data):,}"
            )

            st.caption(
                "Korelasi menunjukkan hubungan statistik, "
                "bukan bukti bahwa satu variabel menyebabkan "
                "variabel lainnya."
            )

else:
    correlation_df = pd.DataFrame()

    st.info(
        "Analisis korelasi memerlukan minimal "
        "dua kolom numerik."
    )


# ==================================================
# 13. REGRESI LINEAR SEDERHANA
# ==================================================

st.divider()
st.header("📉 Regresi Linear Sederhana")

st.write(
    "Regresi linear sederhana memodelkan hubungan "
    "antara satu variabel X dan satu variabel Y."
)

if len(numeric_columns) >= 2:

    reg_col1, reg_col2 = st.columns(2)

    with reg_col1:
        regression_x = st.selectbox(
            "Variabel bebas (X)",
            numeric_columns,
            key="regression_x"
        )

    with reg_col2:
        regression_y = st.selectbox(
            "Variabel terikat (Y)",
            numeric_columns,
            index=1,
            key="regression_y"
        )

    if regression_x == regression_y:

        st.warning(
            "Variabel X dan Y harus berbeda."
        )

    else:

        regression_data = numeric_df[
            [regression_x, regression_y]
        ].replace([np.inf, -np.inf], np.nan).dropna()

        if len(regression_data) < 3:

            st.warning(
                "Regresi linear memerlukan setidaknya "
                "tiga pasangan data valid."
            )

        elif (
            regression_data[regression_x].nunique() < 2
            or regression_data[regression_y].nunique() < 2
        ):

            st.warning(
                "Regresi tidak dapat dihitung karena "
                "salah satu variabel tidak memiliki variasi."
            )

        else:

            x_values = regression_data[regression_x].to_numpy()
            y_values = regression_data[regression_y].to_numpy()

            regression = stats.linregress(
                x_values,
                y_values
            )

            y_predicted = (
                regression.intercept
                + regression.slope * x_values
            )

            residual_sum = np.sum(
                (y_values - y_predicted) ** 2
            )

            total_sum = np.sum(
                (y_values - np.mean(y_values)) ** 2
            )

            r_squared = (
                1 - residual_sum / total_sum
                if total_sum > 0
                else np.nan
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Slope",
                f"{regression.slope:.4f}"
            )

            col2.metric(
                "Intercept",
                f"{regression.intercept:.4f}"
            )

            col3.metric(
                "R-squared",
                f"{r_squared:.4f}"
                if pd.notna(r_squared)
                else "Tidak tersedia"
            )

            st.markdown("### Persamaan Regresi")

            st.latex(
                rf"\hat{{Y}} = "
                rf"{regression.intercept:.4f} "
                rf"+ ({regression.slope:.4f})X"
            )

            st.write(
                f"**P-value slope:** {regression.pvalue:.4g}"
            )

            st.write(
                f"**Jumlah pasangan data:** {len(regression_data):,}"
            )

            regression_plot_data = regression_data.copy()

            regression_plot_data["Prediksi Y"] = y_predicted

            regression_plot_data = regression_plot_data.sort_values(
                by=regression_x
            )

            regression_fig = px.scatter(
                regression_data,
                x=regression_x,
                y=regression_y,
                title="Scatter Plot dan Garis Regresi",
                labels={
                    regression_x: str(regression_x),
                    regression_y: str(regression_y)
                }
            )

            regression_fig.add_scatter(
                x=regression_plot_data[regression_x],
                y=regression_plot_data["Prediksi Y"],
                mode="lines",
                name="Garis Regresi"
            )

            st.plotly_chart(
                regression_fig,
                use_container_width=True
            )

            st.caption(
                "R-squared menunjukkan proporsi variasi Y "
                "yang dijelaskan model linear pada data ini. "
                "Hasil regresi tidak otomatis membuktikan "
                "hubungan sebab-akibat."
            )

else:
    st.info(
        "Regresi linear memerlukan minimal "
        "dua kolom numerik."
    )


# ==================================================
# 14. DOWNLOAD HASIL ANALISIS
# ==================================================

st.divider()
st.header("📥 Download Hasil Analisis")

download_tables = {
    "Data": df,
    "Data_Kosong": missing_table,
    "Info_Tipe_Data": information
}

if not descriptive_table.empty if "descriptive_table" in locals() else False:
    download_tables["Statistik_Pilihan"] = descriptive_table

if not multiple_statistics.empty:
    download_tables["Statistik_Semua"] = multiple_statistics

if "correlation_df" in locals() and not correlation_df.empty:
    download_tables["Korelasi"] = (
        correlation_df
        .rename_axis("Variabel")
        .reset_index()
    )

col1, col2 = st.columns(2)

with col1:

    csv_result = (
        multiple_statistics.to_csv(index=False).encode("utf-8")
        if not multiple_statistics.empty
        else pd.DataFrame().to_csv(index=False).encode("utf-8")
    )

    st.download_button(
        label="⬇️ Download Statistik (CSV)",
        data=csv_result,
        file_name="hasil_statistik_moa.csv",
        mime="text/csv"
    )

with col2:

    try:

        excel_result = make_excel(download_tables)

        st.download_button(
            label="⬇️ Download Hasil Lengkap (Excel)",
            data=excel_result,
            file_name="hasil_analisis_moa.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
        )

    except Exception as e:

        st.error(
            f"File Excel gagal dibuat: {e}"
        )


# ==================================================
# 15. FOOTER
# ==================================================

st.divider()

st.caption(
    "💚 Calculator for MOAs | Turn Data Into Dream"
)

st.caption(
    "Gunakan hasil analisis dengan mempertimbangkan "
    "kualitas data, metode statistik, dan konteks penelitian."
)