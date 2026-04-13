def compute_confidence(llm_confidence: int, cosine_distance: float, all_distances: list[float]) -> float:
    """Composite confidence: 0.5 * normalized_cosine + 0.5 * normalized_llm
    ChromaDB cosine space distances in [0, 2]. similarity = 1 - distance.
    """
    similarity = 1.0 - cosine_distance
    all_similarities = [1.0 - d for d in all_distances]
    sim_min = min(all_similarities)
    sim_max = max(all_similarities)
    if sim_max == sim_min:
        normalized_cosine = 0.5
    else:
        normalized_cosine = (similarity - sim_min) / (sim_max - sim_min)
    normalized_llm = llm_confidence / 100.0
    return round(0.5 * normalized_cosine + 0.5 * normalized_llm, 4)
