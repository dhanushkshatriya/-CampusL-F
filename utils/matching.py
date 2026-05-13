"""
Auto-Matching Module
====================
Implements automatic matching between lost and found items.
Uses text similarity (Jaccard), category matching, and location comparison
to calculate a match score between 0-100%.
"""


def tokenize(text):
    """
    Convert text to a set of lowercase tokens (words).
    Removes common stop words for better matching.
    
    Args:
        text (str): Input text to tokenize.
    
    Returns:
        set: Set of cleaned word tokens.
    """
    if not text:
        return set()
    
    # Common stop words to ignore during matching
    stop_words = {
        'the', 'a', 'an', 'is', 'was', 'are', 'were', 'in', 'on', 'at',
        'to', 'for', 'of', 'with', 'and', 'or', 'it', 'my', 'i', 'me',
        'has', 'had', 'have', 'this', 'that', 'from', 'by', 'not', 'but'
    }
    
    # Tokenize: split on non-alphanumeric characters, convert to lowercase
    import re
    words = set(re.findall(r'[a-zA-Z0-9]+', text.lower()))
    return words - stop_words


def jaccard_similarity(set1, set2):
    """
    Calculate Jaccard Similarity between two sets.
    Jaccard = |Intersection| / |Union|
    
    Args:
        set1 (set): First set of tokens.
        set2 (set): Second set of tokens.
    
    Returns:
        float: Similarity score between 0.0 and 1.0.
    """
    if not set1 or not set2:
        return 0.0
    
    intersection = set1 & set2
    union = set1 | set2
    return len(intersection) / len(union)


def calculate_match_score(lost_item, found_item):
    """
    Calculate overall match score between a lost item and a found item.
    
    Scoring weights:
    - Category match:    30% (exact category match)
    - Name similarity:   25% (Jaccard similarity of item names)
    - Description match: 25% (Jaccard similarity of descriptions)
    - Location match:    20% (Jaccard similarity of locations)
    
    Args:
        lost_item (dict): Lost item data with keys: item_name, category, description, last_seen_location
        found_item (dict): Found item data with keys: item_name, category, description, found_location
    
    Returns:
        float: Match score between 0 and 100 (percentage).
    """
    score = 0.0
    
    # --- Category Match (30 points) ---
    # Exact category match gives full points
    if lost_item.get('category', '').lower() == found_item.get('category', '').lower():
        score += 30.0
    
    # --- Item Name Similarity (25 points) ---
    lost_name_tokens = tokenize(lost_item.get('item_name', ''))
    found_name_tokens = tokenize(found_item.get('item_name', ''))
    name_similarity = jaccard_similarity(lost_name_tokens, found_name_tokens)
    score += name_similarity * 25.0
    
    # --- Description Similarity (25 points) ---
    lost_desc_tokens = tokenize(lost_item.get('description', ''))
    found_desc_tokens = tokenize(found_item.get('description', ''))
    desc_similarity = jaccard_similarity(lost_desc_tokens, found_desc_tokens)
    score += desc_similarity * 25.0
    
    # --- Location Similarity (20 points) ---
    lost_location_tokens = tokenize(lost_item.get('last_seen_location', ''))
    found_location_tokens = tokenize(found_item.get('found_location', ''))
    location_similarity = jaccard_similarity(lost_location_tokens, found_location_tokens)
    score += location_similarity * 20.0
    
    return round(score, 1)


def find_matches(lost_item, found_items, threshold=20.0):
    """
    Find all found items that match a given lost item above a threshold.
    
    Args:
        lost_item (dict): The lost item to find matches for.
        found_items (list): List of found item dicts to compare against.
        threshold (float): Minimum match score to include (default: 20%).
    
    Returns:
        list: List of (found_item, score) tuples, sorted by score descending.
    """
    matches = []
    
    for found_item in found_items:
        # Skip already claimed/returned items
        if found_item.get('status') == 'returned':
            continue
        
        score = calculate_match_score(lost_item, found_item)
        if score >= threshold:
            matches.append((found_item, score))
    
    # Sort by score descending (best matches first)
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches


def find_reverse_matches(found_item, lost_items, threshold=20.0):
    """
    Find all lost items that match a given found item above a threshold.
    Called when a new found item is reported.
    
    Args:
        found_item (dict): The found item to find matches for.
        lost_items (list): List of lost item dicts to compare against.
        threshold (float): Minimum match score to include (default: 20%).
    
    Returns:
        list: List of (lost_item, score) tuples, sorted by score descending.
    """
    matches = []
    
    for lost_item in lost_items:
        # Skip already recovered items
        if lost_item.get('status') == 'recovered':
            continue
        
        score = calculate_match_score(lost_item, found_item)
        if score >= threshold:
            matches.append((lost_item, score))
    
    # Sort by score descending (best matches first)
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches
