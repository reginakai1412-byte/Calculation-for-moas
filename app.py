import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Calculator for MOAs",
    page_icon="💚",
    layout="wide"
)

st.title("💚 Calculator for MOAs")
st.caption("Turn Data Into Dream")
st.write("Aplikasi pengolahan data statistik sederhana.")

st.divider()

st.subheader("📂 Upload Dataset")

file = st.file_uploader(
    "Unggah file CSV atau Excel",
    type=["csv", "xlsx"]
)

if file is not None:
    try:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        st.success("Dataset berhasil dibaca!")

        st.subheader("👀 Preview Data")
        st.dataframe(df, use_container_width=True)

        st.subheader("📊 Statistik Deskriptif")

        numeric_columns = df.select_dtypes(
            include=np.number
        ).columns.tolist()

        if numeric_columns:
            column = st.selectbox(
                "Pilih variabel numerik",
                numeric_columns
            )

            data = df[column].dropna()

            if not data.empty:
                col1, col2, col3 = st.columns(3)

                col1.metric("Jumlah Data", len(data))
                col2.metric("Mean", f"{data.mean():.4f}")
                col3.metric("Median", f"{data.median():.4f}")

                mode_values = data.mode()

                variance = data.var()
                std_dev = data.std()

                st.write("**Modus:**")
                st.write(
                    mode_values.tolist()
                    if not mode_values.empty
                    else "Tidak tersedia"
                )

                col4, col5, col6 = st.columns(3)

                col4.metric("Minimum", f"{data.min():.4f}")
                col5.metric("Maksimum", f"{data.max():.4f}")
                col6.metric("Standar Deviasi Sampel", f"{std_dev:.4f}")

                st.write(
                    f"**Varians sampel:** {variance:.4f}"
                )

                st.write("**Kuartil:**")
                st.write(data.quantile([0.25, 0.50, 0.75]))

                st.subheader("📈 Histogram")

                fig = px.histogram(
                    data,
                    x=data,
                    title=f"Distribusi {column}",
                    labels={"x": column}
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                st.subheader("📦 Boxplot")

                box = px.box(
                    data,
                    y=data,
                    title=f"Boxplot {column}"
                )

                st.plotly_chart(
                    box,
                    use_container_width=True
                )

                result = pd.DataFrame({
                    "Statistik": [
                        "Jumlah Data",
                        "Mean",
                        "Median",
                        "Minimum",
                        "Maksimum",
                        "Varians Sampel",
                        "Standar Deviasi Sampel"
                    ],
                    "Nilai": [
                        len(data),
                        data.mean(),
                        data.median(),
                        data.min(),
                        data.max(),
                        variance,
                        std_dev
                    ]
                })

                st.subheader("⬇️ Download Hasil")

                st.download_button(
                    "Download Hasil Statistik (CSV)",
                    data=result.to_csv(index=False).encode("utf-8"),
                    file_name="hasil_statistik.csv",
                    mime="text/csv"
                )

            else:
                st.warning(
                    "Kolom ini tidak memiliki data numerik yang valid."
                )

        else:
            st.warning(
                "Dataset tidak memiliki kolom numerik yang bisa dianalisis."
            )

        st.subheader("🔎 Informasi Data Kosong")
        st.dataframe(
            df.isnull().sum().rename("Jumlah Data Kosong"),
            use_container_width=True
        )

    except Exception as e:
        st.error(f"Dataset gagal diproses: {e}")

else:
    st.info(
        "Unggah file CSV atau Excel untuk mulai melakukan analisis."
    )