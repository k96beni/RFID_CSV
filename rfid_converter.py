import streamlit as st
import pandas as pd
import io
import re
from typing import Dict, List, Tuple, Optional

# ChargeNode färgschema
CHARGENODE_GREEN = "#00B894"
CHARGENODE_DARK = "#2D3436"
CHARGENODE_LIGHT = "#DFE6E9"

# Custom CSS för ChargeNode-stil
def load_custom_css():
    st.markdown(f"""
    <style>
        /* Huvudfärger */
        .stApp {{
            background-color: #F8F9FA;
        }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {CHARGENODE_DARK};
        }}
        
        [data-testid="stSidebar"] .css-1d391kg, 
        [data-testid="stSidebar"] .css-pkbazv {{
            color: white;
        }}
        
        /* Knappar */
        .stButton > button {{
            background-color: {CHARGENODE_GREEN};
            color: white;
            border: none;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.3s;
        }}
        
        .stButton > button:hover {{
            background-color: #00A383;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        /* Headers */
        h1, h2, h3 {{
            color: {CHARGENODE_DARK};
        }}
        
        /* Info boxes */
        .stAlert {{
            border-radius: 5px;
        }}
        
        /* File uploader */
        [data-testid="stFileUploader"] {{
            background-color: white;
            border-radius: 5px;
            padding: 1rem;
            border: 2px dashed {CHARGENODE_LIGHT};
        }}
        
        /* Dataframes */
        .dataframe {{
            border: 1px solid {CHARGENODE_LIGHT};
            border-radius: 5px;
        }}
        
        /* Success messages */
        .success-box {{
            background-color: #D4EDDA;
            border-left: 4px solid {CHARGENODE_GREEN};
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }}
        
        /* Error messages */
        .error-box {{
            background-color: #F8D7DA;
            border-left: 4px solid #DC3545;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }}
        
        /* Warning messages */
        .warning-box {{
            background-color: #FFF3CD;
            border-left: 4px solid #FFC107;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }}
    </style>
    """, unsafe_allow_html=True)

def sanitize_filename(filename: str) -> str:
    """Sanera filnamn för att undvika problem med specialtecken."""
    # Ersätt svenska tecken
    replacements = {
        'å': 'a', 'ä': 'a', 'ö': 'o',
        'Å': 'A', 'Ä': 'A', 'Ö': 'O',
        'é': 'e', 'è': 'e', 'ü': 'u'
    }
    for old, new in replacements.items():
        filename = filename.replace(old, new)
    
    # Ta bort eller ersätt specialtecken
    filename = re.sub(r'[&/\\#,+()$~%\'\":*?<>{}]', '_', filename)
    filename = re.sub(r'\s+', '_', filename)  # Ersätt mellanslag med underscore
    filename = re.sub(r'_+', '_', filename)   # Ersätt multipla underscores
    filename = filename.strip('_')             # Ta bort underscores i början/slut
    
    return filename

def validate_hex(hex_str: str) -> Tuple[bool, str]:
    """
    Validera HEX-format.
    Returnerar (är_giltig, rensat_hex)
    """
    if pd.isna(hex_str) or str(hex_str).strip() == '':
        return False, ''
    
    # Konvertera till string och rensa
    hex_str = str(hex_str).strip().upper()
    
    # Ta bort eventuella prefix
    hex_str = hex_str.replace('0X', '').replace('0x', '')
    
    # Kontrollera att det bara innehåller hex-tecken
    if not re.match(r'^[0-9A-F]+$', hex_str):
        return False, hex_str
    
    # Kontrollera längd (vanligtvis 8 tecken, men tillåt 6-10)
    if len(hex_str) < 6 or len(hex_str) > 10:
        return False, hex_str
    
    return True, hex_str

def clean_data(value: str) -> str:
    """Rensa data från extra mellanslag och specialtecken."""
    if pd.isna(value):
        return ''
    return str(value).strip()

def find_duplicates(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Hitta duplicerade värden i en kolumn."""
    duplicates = df[df.duplicated(subset=[column], keep=False)]
    return duplicates.sort_values(by=column)

def show_instructions():
    """Visa instruktioner på startsidan."""
    st.title("🔌 RFID CSV Konverterare")
    st.markdown(f"<h3 style='color: {CHARGENODE_GREEN};'>ChargeNode - RFID Data Formatting Tool</h3>", 
                unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 📋 Om programmet
        
        Detta verktyg hjälper dig att konvertera Excel-filer med RFID-data till standardiserat 
        CSV-format för ChargeNodes laddstolpar.
        
        ### ⚙️ Funktioner
        
        - ✅ Konvertera RFID-data från olika Excel-format
        - ✅ Hantera både HEX-nummer och TAGG ID
        - ✅ Validera och rensa data automatiskt
        - ✅ Dela upp per företag (om flera finns)
        - ✅ Detektera och rapportera fel
        
        ### 📊 Stödda format
        
        **Indatafiler:**
        - Excel (.xlsx) med en eller flera flikar
        - RFID-nummer (HEX) eller TAGG ID
        - Regnummer/Referens (Identifieringsnummer)
        - Företagsnamn (valfritt)
        
        **Utdataformat:**
        ```
        RFID;Identifieringsnummer
        1A2B3C4D;ABC123
        5E6F7890;XYZ789
        ```
        """)
    
    with col2:
        st.info("""
        **💡 Tips**
        
        1. Förbered din Excel-fil
        2. Se till att data är i rätt kolumner
        3. Kontrollera företagsnamn om det finns flera
        4. Följ stegen i sidomenyn
        """)
        
        st.success("""
        **📥 CSV-format**
        
        - Semikolon (;) som separator
        - UTF-8 encoding
        - Två kolumner: RFID & Identifieringsnummer
        """)

def main():
    # Ladda custom CSS
    load_custom_css()
    
    # Sidebar navigation
    st.sidebar.image("https://via.placeholder.com/200x60/2D3436/00B894?text=ChargeNode", 
                     use_container_width=True)
    st.sidebar.markdown("---")
    
    # Session state initiering
    if 'step' not in st.session_state:
        st.session_state.step = 'instructions'
    if 'df_main' not in st.session_state:
        st.session_state.df_main = None
    if 'df_mer' not in st.session_state:
        st.session_state.df_mer = None
    if 'column_mapping' not in st.session_state:
        st.session_state.column_mapping = {}
    
    # Navigation
    menu_options = {
        'Instruktioner': 'instructions',
        'Ladda upp fil': 'upload',
        'Kolumnmappning': 'mapping',
        'Validering': 'validation',
        'Resultat': 'result'
    }
    
    selected = st.sidebar.radio(
        "Navigation",
        list(menu_options.keys()),
        index=list(menu_options.values()).index(st.session_state.step)
    )
    st.session_state.step = menu_options[selected]
    
    # Visa rätt steg
    if st.session_state.step == 'instructions':
        show_instructions()
    elif st.session_state.step == 'upload':
        upload_step()
    elif st.session_state.step == 'mapping':
        mapping_step()
    elif st.session_state.step == 'validation':
        validation_step()
    elif st.session_state.step == 'result':
        result_step()

def upload_step():
    st.title("📤 Ladda upp fil")
    
    st.markdown("""
    Ladda upp din Excel-fil (.xlsx) som innehåller RFID-data.
    """)
    
    uploaded_file = st.file_uploader(
        "Välj Excel-fil",
        type=['xlsx'],
        help="Endast .xlsx format stöds"
    )
    
    if uploaded_file is not None:
        try:
            # Läs Excel-fil
            xls = pd.ExcelFile(uploaded_file)
            
            st.success(f"✅ Fil uppladdad: {uploaded_file.name}")
            
            # Visa tillgängliga flikar
            st.markdown("### 📑 Tillgängliga flikar")
            sheet_name = st.selectbox(
                "Välj flik att processera",
                xls.sheet_names
            )
            
            # Läs vald flik
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
            
            # Spara i session state
            st.session_state.df_main = df
            st.session_state.selected_sheet = sheet_name
            
            # Visa förhandsgranskning
            st.markdown("### 👀 Förhandsgranskning")
            st.info(f"**Antal rader:** {len(df)} | **Antal kolumner:** {len(df.columns)}")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Nästa-knapp
            if st.button("➡️ Fortsätt till Kolumnmappning", type="primary"):
                st.session_state.step = 'mapping'
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Fel vid uppladdning av fil: {str(e)}")
    else:
        st.info("👆 Vänligen ladda upp en Excel-fil för att fortsätta")

def mapping_step():
    st.title("🗺️ Kolumnmappning")
    
    if st.session_state.df_main is None:
        st.warning("⚠️ Ingen fil uppladdad. Vänligen gå tillbaka till 'Ladda upp fil'.")
        return
    
    df = st.session_state.df_main
    columns = [''] + list(df.columns)
    
    st.markdown("""
    Ange vilka kolumner som innehåller respektive data.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Obligatoriska fält")
        
        # RFID eller TAGG ID (måste välja ett)
        match_type = st.radio(
            "Matchning sker på:",
            ["RFID/HEX-nummer", "TAGG ID"],
            help="Välj om din fil innehåller RFID-nummer direkt eller TAGG ID som behöver konverteras"
        )
        
        if match_type == "RFID/HEX-nummer":
            rfid_col = st.selectbox(
                "RFID/HEX-nummer kolumn *",
                columns,
                help="Ex: AAC02A7B"
            )
            st.session_state.column_mapping['rfid'] = rfid_col if rfid_col != '' else None
            st.session_state.column_mapping['tagg_id'] = None
        else:
            tagg_col = st.selectbox(
                "TAGG ID kolumn *",
                columns,
                help="Ex: SE-MER-C30020428-F"
            )
            st.session_state.column_mapping['tagg_id'] = tagg_col if tagg_col != '' else None
            st.session_state.column_mapping['rfid'] = None
        
        identifier_col = st.selectbox(
            "Regnummer/Referens (Identifieringsnummer) *",
            columns,
            help="Detta blir 'Identifieringsnummer' i CSV-filen"
        )
        st.session_state.column_mapping['identifier'] = identifier_col if identifier_col != '' else None
    
    with col2:
        st.markdown("#### Valfria fält")
        
        company_col = st.selectbox(
            "Företagsnamn",
            columns,
            help="Om flera företag finns skapas separata filer"
        )
        st.session_state.column_mapping['company'] = company_col if company_col != '' else None
        
        if company_col == '':
            st.info("💡 Om företagsnamn saknas skapas en gemensam fil")
    
    # Validera mappning
    st.markdown("---")
    st.markdown("### ✓ Mappningsöversikt")
    
    mapping_valid = True
    
    # Kontrollera att antingen RFID eller TAGG ID är valt
    if not st.session_state.column_mapping.get('rfid') and not st.session_state.column_mapping.get('tagg_id'):
        st.error("❌ Du måste välja antingen RFID/HEX-nummer eller TAGG ID kolumn")
        mapping_valid = False
    
    if not st.session_state.column_mapping.get('identifier'):
        st.error("❌ Du måste välja Regnummer/Referens kolumn")
        mapping_valid = False
    
    # Visa mappning
    if mapping_valid:
        col1, col2 = st.columns(2)
        with col1:
            if st.session_state.column_mapping.get('rfid'):
                st.success(f"✅ RFID: **{st.session_state.column_mapping['rfid']}**")
            else:
                st.success(f"✅ TAGG ID: **{st.session_state.column_mapping['tagg_id']}**")
            
            st.success(f"✅ Identifieringsnummer: **{st.session_state.column_mapping['identifier']}**")
        
        with col2:
            if st.session_state.column_mapping.get('company'):
                st.info(f"ℹ️ Företagsnamn: **{st.session_state.column_mapping['company']}**")
            else:
                st.info("ℹ️ Inget företagsnamn valt")
    
    # Nästa steg - kolla om vi behöver MER-fil
    st.markdown("---")
    
    if mapping_valid:
        if st.session_state.column_mapping.get('tagg_id'):
            # Behöver MER-fil
            st.markdown("### 📁 RFID MER-fil krävs")
            st.info("""
            Din fil innehåller TAGG ID. För att konvertera till RFID-nummer behöver vi 
            MER-filen som innehåller mappningen mellan TAGG ID och RFID.
            """)
            
            mer_file = st.file_uploader(
                "Ladda upp RFID MER.xlsx",
                type=['xlsx'],
                help="Filen ska innehålla kolumnerna 'Visible Number' och 'Key/Card number'"
            )
            
            if mer_file is not None:
                try:
                    df_mer = pd.read_excel(mer_file)
                    
                    # Kontrollera att rätt kolumner finns
                    required_cols = ['Visible Number', 'Key/Card number']
                    missing_cols = [col for col in required_cols if col not in df_mer.columns]
                    
                    if missing_cols:
                        st.error(f"❌ Följande kolumner saknas i MER-filen: {', '.join(missing_cols)}")
                    else:
                        st.session_state.df_mer = df_mer
                        st.success("✅ MER-fil uppladdad")
                        
                        # Visa förhandsgranskning
                        with st.expander("👀 Förhandsgranska MER-fil"):
                            st.dataframe(df_mer.head(10), use_container_width=True)
                        
                        if st.button("➡️ Fortsätt till Validering", type="primary"):
                            st.session_state.step = 'validation'
                            st.rerun()
                            
                except Exception as e:
                    st.error(f"❌ Fel vid uppladdning av MER-fil: {str(e)}")
        else:
            # Ingen MER-fil behövs
            if st.button("➡️ Fortsätt till Validering", type="primary"):
                st.session_state.step = 'validation'
                st.rerun()

def validation_step():
    st.title("✅ Validering & Datarensning")
    
    if st.session_state.df_main is None:
        st.warning("⚠️ Ingen fil uppladdad. Vänligen gå tillbaka till 'Ladda upp fil'.")
        return
    
    df = st.session_state.df_main.copy()
    mapping = st.session_state.column_mapping
    
    st.markdown("Validerar och rensar data...")
    
    with st.spinner("Processar data..."):
        # Skapa progress bar
        progress_bar = st.progress(0)
        
        # 1. Skapa arbetskolumner
        progress_bar.progress(10)
        
        errors = []
        warnings = []
        
        # 2. Hantera RFID (antingen från RFID-kolumn eller via MER-fil)
        progress_bar.progress(20)
        
        if mapping.get('rfid'):
            # Direkt RFID
            df['RFID_RAW'] = df[mapping['rfid']]
        elif mapping.get('tagg_id'):
            # Hämta RFID från MER-fil
            if st.session_state.df_mer is None:
                st.error("❌ MER-fil saknas men krävs för TAGG ID matchning")
                return
            
            df_mer = st.session_state.df_mer
            
            # Skapa mapping dictionary
            mer_mapping = dict(zip(df_mer['Visible Number'], df_mer['Key/Card number']))
            
            # Matcha TAGG ID
            df['RFID_RAW'] = df[mapping['tagg_id']].map(mer_mapping)
            
            # Hitta omatchade
            unmatched = df[df['RFID_RAW'].isna() & df[mapping['tagg_id']].notna()]
            if len(unmatched) > 0:
                for idx, row in unmatched.iterrows():
                    errors.append({
                        'Rad': idx + 2,  # +2 för Excel-radnummer (header + 0-index)
                        'Problem': 'TAGG ID saknas i MER-fil',
                        'TAGG ID': row[mapping['tagg_id']],
                        'Identifieringsnummer': row[mapping['identifier']] if not pd.isna(row[mapping['identifier']]) else 'Saknas'
                    })
        
        progress_bar.progress(40)
        
        # 3. Rensa och validera RFID
        df['RFID_VALID'] = False
        df['RFID_CLEAN'] = ''
        
        for idx, row in df.iterrows():
            if pd.notna(row['RFID_RAW']):
                is_valid, clean_rfid = validate_hex(row['RFID_RAW'])
                df.at[idx, 'RFID_VALID'] = is_valid
                df.at[idx, 'RFID_CLEAN'] = clean_rfid
                
                if not is_valid:
                    errors.append({
                        'Rad': idx + 2,
                        'Problem': 'Ogiltigt HEX-format',
                        'RFID': row['RFID_RAW'],
                        'Identifieringsnummer': row[mapping['identifier']] if not pd.isna(row[mapping['identifier']]) else 'Saknas'
                    })
        
        progress_bar.progress(60)
        
        # 4. Hantera Identifieringsnummer
        df['Identifieringsnummer'] = df[mapping['identifier']].apply(clean_data)
        
        # Varna om Identifieringsnummer saknas
        missing_id = df[df['Identifieringsnummer'] == '']
        if len(missing_id) > 0:
            for idx, row in missing_id.iterrows():
                warnings.append({
                    'Rad': idx + 2,
                    'Problem': 'Identifieringsnummer saknas',
                    'RFID': row['RFID_CLEAN'] if row['RFID_CLEAN'] else 'Saknas',
                    'Företag': row[mapping['company']] if mapping.get('company') and not pd.isna(row[mapping['company']]) else 'N/A'
                })
        
        progress_bar.progress(80)
        
        # 5. Hantera företagsnamn
        if mapping.get('company'):
            df['Företag'] = df[mapping['company']].apply(clean_data)
            df['Företag'] = df['Företag'].replace('', 'Utan_foretag')
        else:
            df['Företag'] = 'Alla'
        
        # 6. Ta bort tomma rader (där både RFID och Identifieringsnummer saknas)
        df_filtered = df[~((df['RFID_CLEAN'] == '') & (df['Identifieringsnummer'] == ''))]
        
        # 7. Hitta duplicerade RFID
        df_valid = df_filtered[df_filtered['RFID_VALID']]
        duplicates = find_duplicates(df_valid, 'RFID_CLEAN')
        
        if len(duplicates) > 0:
            st.warning(f"⚠️ {len(duplicates)} duplicerade RFID-nummer hittade")
            
            for rfid in duplicates['RFID_CLEAN'].unique():
                dup_rows = df_filtered[df_filtered['RFID_CLEAN'] == rfid]
                for idx, row in dup_rows.iterrows():
                    warnings.append({
                        'Rad': idx + 2,
                        'Problem': 'Duplicerat RFID',
                        'RFID': row['RFID_CLEAN'],
                        'Identifieringsnummer': row['Identifieringsnummer']
                    })
        
        progress_bar.progress(100)
        
        # Spara i session state
        st.session_state.df_processed = df_filtered
        st.session_state.errors = errors
        st.session_state.warnings = warnings
    
    # Visa resultat
    st.markdown("---")
    st.markdown("### 📊 Valideringsresultat")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_rows = len(df_filtered[df_filtered['RFID_VALID']])
        st.metric("✅ Giltiga rader", total_rows)
    
    with col2:
        st.metric("❌ Fel", len(errors))
    
    with col3:
        st.metric("⚠️ Varningar", len(warnings))
    
    # Visa fel
    if len(errors) > 0:
        st.markdown("### ❌ Fel som måste åtgärdas")
        st.markdown("""
        <div class='error-box'>
        Följande rader innehåller fel som hindrar export. Vänligen åtgärda dessa i din ursprungsfil.
        </div>
        """, unsafe_allow_html=True)
        
        df_errors = pd.DataFrame(errors)
        st.dataframe(df_errors, use_container_width=True)
        
        # Möjlighet att ladda ner felrapport
        csv_errors = df_errors.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Ladda ner felrapport (CSV)",
            data=csv_errors,
            file_name="felrapport.csv",
            mime="text/csv"
        )
    
    # Visa varningar
    if len(warnings) > 0:
        st.markdown("### ⚠️ Varningar")
        st.markdown("""
        <div class='warning-box'>
        Följande rader har varningar men kan fortfarande exporteras.
        </div>
        """, unsafe_allow_html=True)
        
        df_warnings = pd.DataFrame(warnings)
        st.dataframe(df_warnings, use_container_width=True)
    
    # Statistik
    st.markdown("### 📈 Statistik")
    
    if len(df_filtered[df_filtered['RFID_VALID']]) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**RFID-information:**")
            unique_rfid = df_filtered[df_filtered['RFID_VALID']]['RFID_CLEAN'].nunique()
            st.write(f"- Unika RFID: {unique_rfid}")
            st.write(f"- Totala rader: {len(df_filtered[df_filtered['RFID_VALID']])}")
            st.write(f"- Duplicat: {len(duplicates)}")
        
        with col2:
            st.markdown("**Företagsfördelning:**")
            company_counts = df_filtered[df_filtered['RFID_VALID']]['Företag'].value_counts()
            for company, count in company_counts.items():
                st.write(f"- {company}: {count} rader")
    
    # Nästa steg
    st.markdown("---")
    
    if len(errors) == 0:
        st.success("✅ Inga kritiska fel hittade. Redo att generera CSV-filer!")
        if st.button("➡️ Fortsätt till Resultat", type="primary"):
            st.session_state.step = 'result'
            st.rerun()
    else:
        st.error("❌ Åtgärda fel innan du kan fortsätta till export.")

def result_step():
    st.title("📥 Resultat & Nedladdning")
    
    if 'df_processed' not in st.session_state or st.session_state.df_processed is None:
        st.warning("⚠️ Ingen data att exportera. Vänligen gå igenom valideringssteg först.")
        return
    
    df = st.session_state.df_processed
    df_valid = df[df['RFID_VALID']].copy()
    
    if len(df_valid) == 0:
        st.error("❌ Inga giltiga rader att exportera.")
        return
    
    # Förhandsgranska data
    st.markdown("### 👀 Förhandsgranska exportdata")
    
    preview_df = df_valid[['RFID_CLEAN', 'Identifieringsnummer', 'Företag']].copy()
    preview_df.columns = ['RFID', 'Identifieringsnummer', 'Företag']
    
    st.dataframe(preview_df, use_container_width=True)
    
    # Generera CSV-filer
    st.markdown("---")
    st.markdown("### 💾 Generera CSV-filer")
    
    companies = df_valid['Företag'].unique()
    
    if len(companies) == 1 and companies[0] == 'Alla':
        st.info("📄 En fil kommer att genereras (inget företagsnamn specificerat)")
    else:
        st.info(f"📄 {len(companies)} filer kommer att genereras (en per företag)")
    
    # Skapa CSV-filer
    csv_files = {}
    
    for company in companies:
        company_data = df_valid[df_valid['Företag'] == company][['RFID_CLEAN', 'Identifieringsnummer']].copy()
        company_data.columns = ['RFID', 'Identifieringsnummer']
        
        # Ta bort duplicat (behåll första)
        company_data = company_data.drop_duplicates(subset=['RFID'], keep='first')
        
        # Skapa CSV med semikolon och UTF-8 BOM
        csv_buffer = io.StringIO()
        company_data.to_csv(csv_buffer, index=False, sep=';', encoding='utf-8-sig')
        csv_string = csv_buffer.getvalue()
        
        # Generera filnamn
        if company == 'Alla':
            filename = "output.csv"
        else:
            filename = f"{sanitize_filename(company)}.csv"
        
        csv_files[filename] = csv_string.encode('utf-8-sig')
    
    # Visa nedladdningsknappar
    st.markdown("### 📥 Ladda ner filer")
    
    cols = st.columns(min(len(csv_files), 3))
    
    for idx, (filename, csv_data) in enumerate(csv_files.items()):
        col = cols[idx % len(cols)]
        
        with col:
            # Räkna rader i filen
            row_count = csv_data.decode('utf-8-sig').count('\n') - 1
            
            st.markdown(f"""
            <div style='background-color: white; padding: 1rem; border-radius: 5px; border: 1px solid {CHARGENODE_LIGHT}; margin-bottom: 1rem;'>
                <h4 style='margin: 0; color: {CHARGENODE_GREEN};'>{filename}</h4>
                <p style='margin: 0.5rem 0; color: {CHARGENODE_DARK};'>{row_count} rader</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.download_button(
                label=f"⬇️ Ladda ner {filename}",
                data=csv_data,
                file_name=filename,
                mime="text/csv",
                key=f"download_{filename}"
            )
    
    # Sammanfattning
    st.markdown("---")
    st.markdown("### ✅ Sammanfattning")
    
    st.markdown(f"""
    <div class='success-box'>
        <h4 style='margin-top: 0; color: {CHARGENODE_GREEN};'>Export slutförd!</h4>
        <ul>
            <li><strong>{len(csv_files)}</strong> fil(er) genererade</li>
            <li><strong>{len(df_valid)}</strong> totala rader exporterade</li>
            <li><strong>{df_valid['RFID_CLEAN'].nunique()}</strong> unika RFID</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Varningar och fel från validering
    if len(st.session_state.warnings) > 0:
        st.warning(f"⚠️ {len(st.session_state.warnings)} varningar rapporterade under validering")
    
    if len(st.session_state.errors) > 0:
        st.info(f"ℹ️ {len(st.session_state.errors)} rader exkluderades på grund av fel")
    
    # Starta om knapp
    st.markdown("---")
    if st.button("🔄 Processera ny fil"):
        # Rensa session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.step = 'instructions'
        st.rerun()

if __name__ == "__main__":
    st.set_page_config(
        page_title="ChargeNode - RFID CSV Converter",
        page_icon="🔌",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    main()
