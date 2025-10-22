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

    # --- Sort amino acids alphabetically ---
    freq_df = freq_df.sort_index()  # ordina le righe (amminoacidi) in ordine A-Z

    # --- Visualization ---
    st.subheader("Amino Acid Frequencies (sorted A–Z)")
    st.dataframe(freq_df)

    st.subheader("Specific Amino Acid Ratios")
    st.dataframe(ratio_df)

    # --- Plot ---
    st.subheader("Bar Plot Comparison (A–Z)")
    fig, ax = plt.subplots(figsize=(10, 5))
    freq_df.plot(kind="bar", ax=ax)
    plt.xlabel("Amino acid")
    plt.ylabel("Relative frequency")
    plt.legend(title="Protein (Entry name)")
    plt.xticks(rotation=0)
    st.pyplot(fig)

    # --- Excel download ---
    st.subheader("📊 Download Results (Excel)")

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        # Write sorted tables
        freq_df.to_excel(writer, sheet_name="AminoAcidFrequencies")
        ratio_df.to_excel(writer, sheet_name="SpecificRatios")

        # Export the sorted plot to Excel
        figfile = BytesIO()
        fig.savefig(figfile, format="png", bbox_inches="tight")
        figfile.seek(0)

        worksheet = writer.sheets["AminoAcidFrequencies"]
        worksheet.insert_image("K2", "barplot.png", {"image_data": figfile})

    excel_data = output.getvalue()

    st.download_button(
        label="⬇️ Download Excel file (sorted A–Z)",
        data=excel_data,
        file_name="UniProt_comparison_results_sorted.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

