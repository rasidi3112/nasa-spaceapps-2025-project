from sentence_transformers import SentenceTransformer, util # type: ignore

# Load model sekali saja biar ga berat
model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_summary(text: str, max_sentences: int = 3) -> str:
    """
    Fungsi untuk bikin ringkasan sederhana dari teks.
    Param:
        text (str): teks panjang dari publikasi
        max_sentences (int): jumlah kalimat ringkasan
    Return:
        str: ringkasan pendek
    """
    if not text:
        return "Tidak ada teks untuk diringkas."

    # Pisah teks jadi kalimat
    sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 10]

    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    # Encode kalimat
    embeddings = model.encode(sentences, convert_to_tensor=True)

    # Cari kalimat yang paling representatif
    centroid = embeddings.mean(dim=0)
    scores = util.cos_sim(centroid, embeddings)[0]

    top_idx = scores.argsort(descending=True)[:max_sentences]
    selected_sentences = [sentences[i] for i in top_idx]

    return " ".join(selected_sentences)
