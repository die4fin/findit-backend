import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import re
import io

CSV_FILE = 'MATCH_HISTORY_DATA.xlsx - Sheet1.csv' 

def train_xgboost():
    print("1. Membaca dan Membersihkan Dataset...")
    try:
        with open(CSV_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        content = re.sub(r'\\s*', '', content)
        content = content.replace('"', '').replace('\t', ',')
        df = pd.read_csv(io.StringIO(content), sep=',')
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    df.columns = df.columns.str.strip()
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    y = df['Blue_Win']

    print("\n2. Membangun Fitur 'Bag-of-Heroes' (Picks & Bans)...")
    pick_cols_A = ['B_P1', 'B_P2', 'B_P3', 'B_P4', 'B_P5']
    pick_cols_B = ['R_P1', 'R_P2', 'R_P3', 'R_P4', 'R_P5']
    ban_cols_A = ['B_B1', 'B_B2', 'B_B3', 'B_B4', 'B_B5']
    ban_cols_B = ['R_B1', 'R_B2', 'R_B3', 'R_B4', 'R_B5']
    
    all_heroes = set()
    for col in pick_cols_A + pick_cols_B + ban_cols_A + ban_cols_B:
        all_heroes.update(df[col].dropna().unique())
    if 'None' in all_heroes:
        all_heroes.remove('None')

    feature_dict = {}
    for hero in all_heroes:
        feature_dict[f"TeamA_Pick_{hero}"] = df[pick_cols_A].isin([hero]).any(axis=1).astype(int)
        feature_dict[f"TeamB_Pick_{hero}"] = df[pick_cols_B].isin([hero]).any(axis=1).astype(int)
        feature_dict[f"TeamA_Ban_{hero}"] = df[ban_cols_A].isin([hero]).any(axis=1).astype(int)
        feature_dict[f"TeamB_Ban_{hero}"] = df[ban_cols_B].isin([hero]).any(axis=1).astype(int)
        
    X_encoded = pd.DataFrame(feature_dict)

    model_columns = list(X_encoded.columns)
    joblib.dump(model_columns, 'model_columns.pkl')

    X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)

    print("\n3. Melatih XGBoost dengan Anti-Overfitting Tingkat Tinggi...")
    model = xgb.XGBClassifier(
        eval_metric='logloss',
        learning_rate=0.01,       
        max_depth=2,              
        n_estimators=500,         
        subsample=0.6,            
        colsample_bytree=0.6,     
        gamma=1,                  
        reg_lambda=2              
    )
    
    model.fit(X_train, y_train)

    print("\n4. Evaluasi Akurasi...")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"🎯 Akurasi Prediksi: {accuracy * 100:.2f}%\n")
    
    joblib.dump(model, 'xgboost_draft_model.pkl')
    print("🎉 BOOM! Otak AI telah disempurnakan!")

if __name__ == "__main__":
    train_xgboost()