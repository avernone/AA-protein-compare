import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# --- Streamlit page config ---
st.set_page_config(page_title="UniProt Protein Comparison", page_icon="🧬", layout="wide")

st.title("🧬 Amino Acid Composition Comparison (UniProt)")

st.write("""
Enter **one or more UniProt accession codes (AC)** separated by commas to compare 
relative amino acid frequencies and specific ratios (E/Q, E/P, Y/F, D/N, G/S) across proteins.

Example: `P69905, P68871, P02042`
""")

# --- Text input (Enter to submit) ---
ac_input = st.text_input("UniProt accession codes (AC):", "")

if ac_input:
    ac_list = [x.strip() for x in ac_input.split(",") if x.strip()]
    results = {}
    ratio_results = {}

    def ratio(a, b, aa_counts):
        return (aa_counts.get(a, 0) / aa_counts.get(b, 1)) if aa_counts.get(b, 0) != 0 else 0

    for ac in ac_list:
        url_fasta = f"https://rest.uniprot.org/uniprotkb/{ac}.fasta"
        url_json = f"https://rest.uniprot.org/uniprotkb/{ac}.json"

        fasta_response = requests.get(url_fasta)
        json_response = requests.get(url_json)

        if fasta_response.status_code == 200 and ">" in fasta_response.text:
            # Extract sequence
            lines = fasta_response.text.splitlines()
            sequence = "".join([l.strip() for l in lines if not l.startswith(">")])

            # Get entry name from JSON metadata
            if json_response.status_code == 200:
                data = json_response.json()
                entry_name = data.get("uniProtkbId", ac)
            else:
                entry_name = ac

            # Count amino acids
            aa_counts = {}
            for aa in sequence:
                aa_counts[aa] = aa_counts.get(aa, 0) + 1

            total = len(sequence)
            aa_freq = {aa: count / total for aa, count in aa_counts.items()}
            results[entry_name] = aa_freq

            # Compute ratios
            ratios = {
                "E/Q": ratio('E', 'Q', aa_counts),
                "E/P": ratio('E', 'P', aa_counts),
                "Y/F": ratio('Y', 'F', aa_counts),
                "D/N": ratio('D', 'N', aa_counts),
                "G/S": ratio('G', 'S', aa_counts)
            }
            ratio_results[entry_name] = ratios

        else:
            st.warning(f"⚠️ Invalid UniProt AC or sequence not found: {ac}")

    # --- DataFrames ---
    freq_df = pd.DataFrame(results).fillna(0)
    ratio_df = pd.DataFrame(ratio_results).T

    # --- Sort alphabetically (A-Z) ---
    freq_df = freq_df.sort_index()

    # --- Visualization ---
    st.subheader("Amino Acid Frequencies (sorted A–Z)")
    st.dataframe(freq_df)

    st.subheader("Specific Amino Acid Ratios")
    st.dataframe(ratio_df)

    # --- Plot 1: Amino Acid Frequencies ---
    st.subheader("Bar Plot: Amino Acid Frequencies (A–Z)")
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    freq_df.plot(kind="bar", ax=ax1)
    plt.xlabel("Amino acid")
    plt.ylabel("Relative frequency")
    plt.legend(title="Protein (Entry name)")
    plt.xticks(rotation=0)
    st.pyplot(fig1)

    # --- Plot 2: Specific Ratios ---
    st.subheader("Bar Plot: Specific Amino Acid Ratios")
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ratio_df.plot(kind="bar", ax=ax2)
    plt.xlabel("Ratio type")
    plt.ylabel("Value")
    plt.legend(title="Protein (Entry name)")
    plt.xticks(rotation=0)
    st.pyplot(fig2)

    # --- Excel download ---
    st.subheader("📊 Download Results (Excel)")

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        # Write tables
        freq_df.to_excel(writer, sheet_name="AminoAcidFrequencies")
        ratio_df.to_excel(writer, sheet_name="SpecificRatios")

        # Save first plot (frequencies)
        figfile1 = BytesIO()
        fig1.savefig(figfile1, format="png", bbox_inches="tight")
        figfile1.seek(0)

        # Save second plot (ratios)
        figfile2 = BytesIO()
        fig2.savefig(figfile2, format="png", bbox_inches="tight")
        figfile2.seek(0)

        # Insert plots in respective sheets
        worksheet1 = writer.sheets["AminoAcidFrequencies"]
        worksheet1.insert_image("K2", "freq_plot.png", {"image_data": figfile1})

        worksheet2 = writer.sheets["SpecificRatios"]
        worksheet2.insert_image("H2", "ratio_plot.png", {"image_data": figfile2})

    excel_data = output.getvalue()

    st.download_button(
        label="⬇️ Download Excel file (with plots)",
        data=excel_data,
        file_name="UniProt_comparison_results_with_plots.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

