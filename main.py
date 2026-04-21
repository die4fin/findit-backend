from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import xgboost as xgb
import pickle

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def root():
    return {"status": "FINDIT API is Online"}

# Load AI dan Kamus Kategori
try:
    with open('genjutsu_model.pkl', 'rb') as f:
        data = pickle.load(f)
        model = data['model']
        categories_dict = data['categories']
    print("✅ Genjutsu Model & Categories Loaded Successfully!")
except Exception as e:
    print("❌ Model gagal dimuat! Error:", e)

class DraftData(BaseModel):
    teamA: list[str]
    teamB: list[str]
    teamABans: list[str]
    teamBBans: list[str]

# SMART AUTO-CORRECTOR
def match_hero_name(input_name, valid_categories):
    if input_name == 'None' or not input_name:
        return valid_categories[0]
    
    clean_input = input_name.lower().replace('-', '').replace(' ', '').replace('.', '')
    
    for valid_name in valid_categories:
        clean_valid = str(valid_name).lower().replace('-', '').replace(' ', '').replace('.', '')
        if clean_input == clean_valid:
            return valid_name
            
    return valid_categories[0] 

@app.post("/predict")
def predict_draft(draft: DraftData):
    def pad_list(lst):
        return lst + ['None'] * (5 - len(lst))
        
    b_bans = pad_list(draft.teamABans)
    r_bans = pad_list(draft.teamBBans)
    b_picks = pad_list(draft.teamA)
    r_picks = pad_list(draft.teamB)
    
    data_dict = {}
    
    for i in range(5):
        b_b_col, r_b_col = f'B_B{i+1}', f'R_B{i+1}'
        b_p_col, r_p_col = f'B_P{i+1}', f'R_P{i+1}'
        
        data_dict[b_b_col] = [match_hero_name(b_bans[i], categories_dict[b_b_col])]
        data_dict[r_b_col] = [match_hero_name(r_bans[i], categories_dict[r_b_col])]
        data_dict[b_p_col] = [match_hero_name(b_picks[i], categories_dict[b_p_col])]
        data_dict[r_p_col] = [match_hero_name(r_picks[i], categories_dict[r_p_col])]
        
    features = [
        'B_B1', 'B_B2', 'B_B3', 'B_B4', 'B_B5', 
        'R_B1', 'R_B2', 'R_B3', 'R_B4', 'R_B5', 
        'B_P1', 'B_P2', 'B_P3', 'B_P4', 'B_P5', 
        'R_P1', 'R_P2', 'R_P3', 'R_P4', 'R_P5'
    ]
                
    input_df = pd.DataFrame(data_dict)
    
    # ---> INI DIA FIX-NYA! <---
    # Urutkan secara paksa biar susunan kolomnya identik 100% sama pas training
    input_df = input_df[features]
    
    # SET CATEGORY SESUAI TRAINING
    for col in features:
        input_df[col] = pd.Categorical(input_df[col], categories=categories_dict[col])
        
    prob = model.predict_proba(input_df)[0]
    
    win_prob_A = float(prob[1])
    win_prob_B = float(prob[0])
    
    insight = "Draft Tim Biru memiliki keunggulan formasi dan sinergi teamfight." if win_prob_A > 0.5 else "Tim Merah mengamankan counter krusial yang menyulitkan pergerakan core musuh."
    recommendations = ["Prioritaskan Turtle pertama", "Bermain agresif di mid-game", "Kunci pergerakan Jungler musuh"]
    
    return {
        "winProbability": {
            "teamA": win_prob_A,
            "teamB": win_prob_B
        },
        "insight": insight,
        "recommendations": recommendations
    }