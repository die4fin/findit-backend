import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle

# 1. Load Dataset
file_path = "matches_dataset.csv"
print("Membaca dataset...")
df = pd.read_csv(file_path)

features = [
    'B_B1', 'B_B2', 'B_B3', 'B_B4', 'B_B5', 
    'R_B1', 'R_B2', 'R_B3', 'R_B4', 'R_B5', 
    'B_P1', 'B_P2', 'B_P3', 'B_P4', 'B_P5', 
    'R_P1', 'R_P2', 'R_P3', 'R_P4', 'R_P5'
]
target = 'Blue_Win'

df = df[features + [target]].dropna()

# 2. Simpan Kategori Asli
categories_dict = {}
for col in features:
    df[col] = df[col].astype('category')
    # Simpan daftar nama hero yang sah di kolom ini
    categories_dict[col] = df[col].cat.categories

X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Training Model
model = xgb.XGBClassifier(
    enable_categorical=True,
    tree_method='hist',
    max_depth=4,
    learning_rate=0.05,
    n_estimators=300,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)

print("Mulai melatih AI... (Mohon tunggu)")
model.fit(X_train, y_train)

preds = model.predict(X_test)
print(f"AKURASI MODEL: {accuracy_score(y_test, preds) * 100:.2f}%")

# 4. BUNGKUS MODEL + KAMUS KATEGORI!
with open('genjutsu_model.pkl', 'wb') as f:
    pickle.dump({'model': model, 'categories': categories_dict}, f)
print("Model dan Kamus Kategori berhasil disimpan! 🔥")