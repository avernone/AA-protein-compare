# AA-protein-compare
# 🧬 UniProt Protein Comparison App

### Comparative analysis of amino acid composition and residue-specific ratios across UniProt protein sequences

---

## 🔍 Overview

This web application, **fully developed in Python** and **deployed on Streamlit Cloud**, enables researchers to **compare the amino acid composition** and **specific residue ratios** (E/Q, E/P, Y/F, D/N, G/S) across multiple protein sequences retrieved from the [UniProt](https://www.uniprot.org/) database.

The app provides:
- Quantitative **amino acid frequency tables** for each protein  
- Computed **residue ratio tables** for selected amino acid pairs  
- **Comparative bar plots** for visual inspection of amino acid distribution  
- A downloadable **Excel file** including all tables and plots  

This tool facilitates **rapid exploratory analysis** of protein sequence composition using direct integration with UniProt REST APIs.

---

## ⚙️ Implementation and Methodology

The application is implemented in **Python 3.11** using:

| Library | Function |
|----------|-----------|
| `streamlit` | Interactive web interface |
| `requests` | UniProt REST API access |
| `pandas` | Data processing and table handling |
| `matplotlib` | Comparative bar plot generation |
| `XlsxWriter` | Excel export with embedded graphics |

For each UniProt Accession Code (AC) provided by the user, the app:
1. Fetches the **FASTA sequence** and **metadata** from the UniProt REST API.  
2. Computes amino acid counts and relative frequencies.  
3. Calculates specific amino acid ratios (E/Q, E/P, Y/F, D/N, G/S).  
4. Aggregates results into `pandas` DataFrames.  
5. Displays sortable tables and bar plots (amino acids sorted alphabetically A–Z).  
6. Exports all results to an Excel file using `XlsxWriter`.

---

## 🧠 Scientific Rationale

Residue composition and residue-specific ratios (e.g., E/Q, D/N) can reflect:
- Differences in **protein stability** and **structure**  
- **Evolutionary adaptations** to environmental or functional constraints  
- **Homology-based variations** across species  

This tool enables **rapid quantitative comparisons** without the need for advanced bioinformatics software, ideal for **teaching**, **exploratory research**, and **preliminary data inspection**.



