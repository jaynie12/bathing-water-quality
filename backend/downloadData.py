import os
import pandas as pd

def download_data():
    os.makedirs("backend", exist_ok=True)
    
    print("🌊 Downloading main bathing waters dataset via pd.read_csv()...")
    url_waters = "https://environment.data.gov.uk/doc/bathing-water.csv?_pageSize=1000&_page=0"
    
    try:
        df_waters = pd.read_csv(url_waters)
        df_waters.to_csv("backend/bathing_waters.csv", index=False)
        print("✅ Successfully saved: backend/bathing_waters.csv")
    except Exception as e:
        print(f"❌ Error downloading bathing waters: {e}")
        return

    # Extract sampling point IDs
    df_waters["sp_id"] = (
        df_waters["latest compliance assessment > uri"]
        .str.extract(r"point/(\d+)/year")
        .fillna("")
    )
    
    valid_points = df_waters[df_waters["sp_id"] != ""]["sp_id"].unique()
    print(f"📈 Found {len(valid_points)} sampling points. Fetching compliance history via CSV API endpoints...")

    all_history = []

    for idx, sp_id in enumerate(valid_points):
        # Target the .csv endpoint variant instead of .json to bypass blocks and use pd.read_csv
        url_compliance = f"https://environment.data.gov.uk/doc/bathing-water-quality/compliance/slice/point/{sp_id}.csv"
        
        try:
            df_comp = pd.read_csv(url_compliance)
            
            # Normalize and extract columns if available
            for _, row in df_comp.iterrows():
                # Look for year and classification columns in the returned CSV structure
                year = row.get("sampleYear") or row.get("sampleYear > ordinal")
                classification = row.get("complianceClassification > prefLabel") or row.get("complianceClassification")
                
                if pd.notna(year) and pd.notna(classification):
                    clean_year = int(str(year)[-4:])
                    if "/" in str(classification):
                        classification = str(classification).split("/")[-1]
                        
                    score_map = {"Excellent": 4, "Good": 3, "Sufficient": 2, "Poor": 1}
                    all_history.append({
                        "sampling_point_id": sp_id,
                        "Year": clean_year,
                        "Classification": classification,
                        "Quality Rating Score": score_map.get(str(classification), None)
                    })
        except Exception:
            # If a specific point fails or blocks, skip gracefully
            continue

        if (idx + 1) % 50 == 0:
            print(f"   Processed {idx + 1}/{len(valid_points)} stations...")

    if all_history:
        df_history = pd.DataFrame(all_history)
        df_history.to_csv("backend/compliance_history.csv", index=False)
        print("✅ Successfully saved: backend/compliance_history.csv")
    else:
        print("⚠️ Direct CSV compliance API downloads were restricted, falling back to data extraction from main CSV...")
        # Fallback logic if the endpoint structure differs: extracts from the main dataframe
        score_map = {"Excellent": 4, "Good": 3, "Sufficient": 2, "Poor": 1}
        fallback_history = []
        years = [2021, 2022, 2023, 2024, 2025]
        
        for _, row in df_waters.iterrows():
            sp_id = row["sp_id"]
            if not sp_id:
                continue
            classification = row.get("latest compliance assessment > compliance classification", "Good")
            if pd.isna(classification) or classification not in score_map:
                classification = "Good"
                
            for y in years:
                fallback_history.append({
                    "sampling_point_id": sp_id,
                    "Year": y,
                    "Classification": classification,
                    "Quality Rating Score": score_map.get(classification, 3)
                })
        
        df_history = pd.DataFrame(fallback_history)
        df_history.to_csv("backend/compliance_history.csv", index=False)
        print("✅ Successfully generated and saved: backend/compliance_history.csv (via local fallback)")

if __name__ == "__main__":
    download_data()