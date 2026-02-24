
################################################################################
CELL 2
################################################################################
import sys
import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
import pickle
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Plotting
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# NLP and embeddings
from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity, cosine_distances
from scipy.spatial.distance import cdist
from tqdm import tqdm

# Statistics
from scipy import stats
from scipy.stats import mannwhitneyu
import itertools

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 11

print("✓ Imports successful")
print(f"✓ Working directory: {os.getcwd()}")
print(f"✓ PyTorch version: {torch.__version__}")
print(f"✓ CUDA available: {torch.cuda.is_available()}")

# Visualization: 2D Embedding Space with UMAP
# Install umap-learn if not already installed
try:
    import umap
except ImportError:
    import subprocess
    subprocess.check_call(['pip', 'install', 'umap-learn'])
    import umap

################################################################################
CELL 4
################################################################################
# Define DISTINCT colors for each group
colors = {
    'Human': '#DC143C',  # Crimson red (PROMINENT)
    'claude-opus-4-5': '#4A90E2',  # Blue
    'gemini-3-pro-preview': '#7B68EE',  # Purple
    'gpt-5.2': '#FF8C00',  # Dark orange
}

################################################################################
CELL 5
################################################################################
def retrieve_embeddings(path_to_embeddings):
    with open(path_to_embeddings, 'rb') as f:
        embeddings_data = pickle.load(f)
    return embeddings_data

################################################################################
CELL 6
################################################################################
def cliffs_delta(group1, group2):
    """
    Calculate Cliff's Delta effect size.
    
    Interpretation:
    - |δ| < 0.147: negligible
    - |δ| < 0.33: small
    - |δ| < 0.474: medium
    - |δ| ≥ 0.474: large
    """
    n1, n2 = len(group1), len(group2)
    
    # Count pairs where group1 > group2 and group1 < group2
    dominance = 0
    for x in group1:
        for y in group2:
            if x > y:
                dominance += 1
            elif x < y:
                dominance -= 1
    
    delta = dominance / (n1 * n2)
    return delta

def interpret_cliffs_delta(delta):
    """Interpret Cliff's Delta magnitude"""
    abs_delta = abs(delta)
    if abs_delta < 0.147:
        return "negligible"
    elif abs_delta < 0.33:
        return "small"
    elif abs_delta < 0.474:
        return "medium"
    else:
        return "large"

def permutation_test(group1, group2, n_permutations=10000, random_state=42):
    """
    Perform permutation test for difference in means.
    """
    np.random.seed(random_state)
    
    # Observed difference
    obs_diff = np.mean(group1) - np.mean(group2)
    
    # Combine groups
    combined = np.concatenate([group1, group2])
    n1 = len(group1)
    
    # Permutation distribution
    perm_diffs = []
    for _ in range(n_permutations):
        np.random.shuffle(combined)
        perm_group1 = combined[:n1]
        perm_group2 = combined[n1:]
        perm_diff = np.mean(perm_group1) - np.mean(perm_group2)
        perm_diffs.append(perm_diff)
    
    perm_diffs = np.array(perm_diffs)
    
    # Two-tailed p-value
    p_value = np.mean(np.abs(perm_diffs) >= np.abs(obs_diff))
    
    return p_value, obs_diff, perm_diffs

print("✓ Helper functions defined")

################################################################################
CELL 8
################################################################################
# Load AI proposals
ai_proposals_path = Path('data/ai-proposals/baseline')
ai_files = sorted(ai_proposals_path.glob('ai_proposals_baseline_complete_*.csv'))

if not ai_files:
    raise FileNotFoundError("No AI proposal files found. Run gen_proposals.ipynb first.")

# Use the most recent file
ai_df = pd.read_csv(ai_files[-1])
print(f"✓ Loaded AI proposals from: {ai_files[-1].name}")
print(f"  Shape: {ai_df.shape}")
print(f"  Models: {ai_df['model'].value_counts().to_dict()}")

# Load human proposals
human_proposals_path = Path('data/human-proposals')
human_files = list(human_proposals_path.glob('*.json'))

human_proposals = []
for file in human_files:
    with open(file, 'r') as f:
        data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(data, list):
            # Case 1: JSON is a flat list of proposals
            for proposal in data:
                proposal['source_file'] = file.name
                human_proposals.append(proposal)
        elif 'proposals' in data:
            # Case 2: JSON has a 'proposals' key (most common structure)
            for proposal in data['proposals']:
                proposal['source_file'] = file.name
                human_proposals.append(proposal)
        else:
            # Case 3: JSON is a single proposal object
            data['source_file'] = file.name
            human_proposals.append(data)

human_df = pd.DataFrame(human_proposals)
print(f"\n✓ Loaded human proposals from {len(human_files)} files")
print(f"  Total proposals: {len(human_df)}")
print(f"  Source files: {human_df['source_file'].unique().tolist()}")

################################################################################
CELL 10
################################################################################
def create_full_text(row, is_ai=True):
    """
    Create full proposal text from components.
    """
    if is_ai:
        # AI proposals structure
        sections = [
            f"Title: {row.get('title', '')}",
            f"Abstract: {row.get('abstract', '')}",
            f"Background: {row.get('background_and_significance', '')}",
            f"Research Questions: {row.get('research_questions_and_hypotheses', '')}",
            f"Methods: {row.get('methods_and_approach', '')}",
            f"Outcomes: {row.get('expected_outcomes_and_impact', '')}",
            f"Open Science: {row.get('open_science_and_reproducibility', '')}",
            f"Budget: {row.get('budget_and_resources', '')}"
        ]
    else:
        # Human proposals structure (based on actual JSON structure)
        sections = [
            f"Title: {row.get('proposal_title', row.get('title', ''))}",
            f"Abstract: {row.get('abstract', '')}",
            f"Full Proposal: {row.get('full_draft', row.get('full_text', row.get('full_proposal', '')))}"
        ]
    
    # Filter out empty sections and join
    text = " ".join([s for s in sections if s.split(': ', 1)[1].strip()])
    return text

# Create full texts
ai_df['full_text'] = ai_df.apply(lambda row: create_full_text(row, is_ai=True), axis=1)
human_df['full_text'] = human_df.apply(lambda row: create_full_text(row, is_ai=False), axis=1)

# Add group labels
ai_df['group'] = 'AI'
human_df['group'] = 'Human'

print(f"✓ Created full proposal texts")
print(f"  AI avg length: {ai_df['full_text'].str.len().mean():.0f} characters")
print(f"  Human avg length: {human_df['full_text'].str.len().mean():.0f} characters")

################################################################################
CELL 12
################################################################################
# Load BioLinkBERT model (state-of-the-art for biomedical tasks)
# BioLinkBERT was pretrained on PubMed with citation links
# Paper: https://arxiv.org/abs/2203.15827
# GitHub: https://github.com/michiyasunaga/LinkBERT
model_name = "michiyasunaga/BioLinkBERT-large"  # 340M params, best performance

print(f"Loading BioLinkBERT model: {model_name}")
print("Note: BioLinkBERT outperforms PubMedBERT on all biomedical benchmarks")
tokenizer = AutoTokenizer.from_pretrained(model_name)
# Use 'embedding_model' so loops like "for model in ai_models" don't overwrite it
embedding_model = AutoModel.from_pretrained(model_name)

# Move to GPU if available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
embedding_model = embedding_model.to(device)
embedding_model.eval()

print(f"✓ Model loaded on: {device}")
print(f"✓ Model parameters: {sum(p.numel() for p in embedding_model.parameters()):,}")

################################################################################
CELL 13
################################################################################
def get_embeddings_with_chunking(texts, chunk_size=400, overlap=50, batch_size=8):
    """
    Generate embeddings for long texts using chunking approach.
    
    This handles proposals that are longer than the 512 token limit by:
    1. Splitting each proposal into overlapping chunks (~400 words each)
    2. Embedding each chunk with BioLinkBERT
    3. Averaging chunk embeddings to get one embedding per proposal
    
    This ensures we use 100% of the proposal text, not just the first 15%.
    
    Args:
        texts: List of text strings (full proposals)
        chunk_size: Number of words per chunk (default: 400 ≈ 500 tokens)
        overlap: Number of overlapping words between chunks (default: 50)
        batch_size: Batch size for processing chunks
    
    Returns:
        numpy array of embeddings (shape: [n_texts, embedding_dim])
    """
    from tqdm import tqdm
    all_doc_embeddings = []
    
    for text in tqdm(texts, desc="Embedding proposals"):
        # Split text into words
        words = text.split()
        
        # Create overlapping chunks
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            if len(chunk_words) > 10:  # Skip very small chunks
                chunks.append(' '.join(chunk_words))
        
        if not chunks:  # Handle empty text
            chunks = [text if text else "empty"]
        
        # Embed each chunk in batches
        chunk_embeddings = []
        with torch.no_grad():
            for j in range(0, len(chunks), batch_size):
                batch_chunks = chunks[j:j+batch_size]
                
                # Tokenize
                encoded = tokenizer(
                    batch_chunks,
                    padding=True,
                    truncation=True,
                    max_length=512,
                    return_tensors='pt'
                ).to(device)
                
                # Get embeddings
                outputs = embedding_model(**encoded)
                
                # Use [CLS] token embedding (first token)
                cls_embeddings = outputs.last_hidden_state[:, 0, :]
                chunk_embeddings.append(cls_embeddings.cpu().numpy())
        
        # Average all chunk embeddings for this document
        all_chunk_embeds = np.vstack(chunk_embeddings)
        doc_embedding = all_chunk_embeds.mean(axis=0)
        all_doc_embeddings.append(doc_embedding)
    
    return np.vstack(all_doc_embeddings)

print("✓ Chunked embedding function defined")
print("  Splits each proposal into ~400-word chunks with 50-word overlap")
print("  Embeds each chunk, then averages to get one embedding per proposal")
print("  This uses 100% of proposal text instead of just 15%!")

################################################################################
CELL 14
################################################################################
# Generate embeddings using chunking approach
print("="*70)
print("GENERATING EMBEDDINGS WITH BIOLINKBERT + CHUNKING")
print("="*70)
print(f"Proposals are ~{ai_df['full_text'].str.len().mean():.0f} chars (AI) and ~{human_df['full_text'].str.len().mean():.0f} chars (human)")
print("Chunking ensures we use 100% of text, not just first 15%")
print()

# Generate embeddings for AI proposals
print("Embedding AI proposals (this may take a few minutes)...")
ai_embeddings = get_embeddings_with_chunking(ai_df['full_text'].tolist())
print(f"✓ AI embeddings shape: {ai_embeddings.shape}")

# Generate embeddings for human proposals
print("\nEmbedding human proposals...")
human_embeddings = get_embeddings_with_chunking(human_df['full_text'].tolist())
print(f"✓ Human embeddings shape: {human_embeddings.shape}")

print("\n✓ All embeddings generated successfully!")
print("="*70)

################################################################################
CELL 16
################################################################################
# Create output directory
embeddings_dir = Path('data/embeddings')
embeddings_dir.mkdir(parents=True, exist_ok=True)

# Save embeddings with timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

embeddings_data = {
    'ai_embeddings': ai_embeddings,
    'human_embeddings': human_embeddings,
    'ai_metadata': ai_df[['model', 'title', 'group']].to_dict('records'),
    'human_metadata': human_df[['proposal_title', 'group', 'source_file']].to_dict('records'),
    'model_name': model_name,
    'timestamp': timestamp
}

embeddings_file = embeddings_dir / f'proposal_embeddings_{timestamp}.pkl'
with open(embeddings_file, 'wb') as f:
    pickle.dump(embeddings_data, f)

print(f"✓ Saved embeddings to: {embeddings_file}")
print(f"  File size: {embeddings_file.stat().st_size / 1024 / 1024:.2f} MB")

################################################################################
CELL 18
################################################################################
# embeddings_data = retrieve_embeddings('/Users/eveyhuang/Documents/NICO/human-AI-proposal/data/embeddings/full_proposals/proposal_embeddings_human_ai_baseline.pkl')

# ai_embeddings = embeddings_data['ai_embeddings']
# human_embeddings = embeddings_data['human_embeddings']
# ai_metadata = embeddings_data['ai_metadata']
# human_metadata = embeddings_data['human_metadata']


