import pandas as pd
import json
import uuid
import os
from enhanced_chatbot import EnhancedChatbot, make_adapter

def main():
    excel_path = r'd:\Psyco Therapy\Criteria Evidence - model vs doctor criteria.xlsx'
    print(f"Reading excel file from {excel_path}...")
    df = pd.read_excel(excel_path, header=3)
    
    # Filter rows that have a client message
    df_filtered = df.dropna(subset=['Example client message (synthetic)'])
    print(f"Found {len(df_filtered)} messages to evaluate.")
    
    BACKEND = "ollama"
    MODEL   = "gemma4:26b"
    adapter = make_adapter(BACKEND, model=MODEL, api_key="")
    
    results = []
    
    # We create a single output file
    output_path = r'd:\Psyco Therapy\Therapy\part1_conversational\evaluation_results.json'
    
    for i, (idx, row) in enumerate(df_filtered.iterrows()):
        client_msg = str(row['Example client message (synthetic)'])
        domain = str(row.get('Domain', ''))
        criterion = str(row.get('Criterion', ''))
        
        print(f"[{i+1}/{len(df_filtered)}] Processing: {client_msg[:50]}...")
        
        # New bot for each message to avoid context leakage
        sid = f"eval_{uuid.uuid4().hex[:8]}"
        bot = EnhancedChatbot(llm=adapter, session_id=sid, log_dir=".")
        
        try:
            response, meta = bot.generate_response(client_msg)
        except Exception as e:
            response = f"ERROR: {e}"
            meta = {}
            
        results.append({
            'row_index': idx,
            'Domain': domain,
            'Criterion': criterion,
            'client_message': client_msg,
            'model_response': response,
            'metadata': meta
        })
        
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
        
    print(f"Evaluation complete. Results saved to {output_path}")

if __name__ == "__main__":
    main()
