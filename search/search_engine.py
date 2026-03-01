import json
import re
from difflib import SequenceMatcher
from collections import Counter
from math import log

class SearchEngine:
    def __init__(self):
        self.load_index()
        
    def load_index(self):
        try:
            with open('search_index.json', 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    self.index = json.loads(content)
                else:
                    self.index = []
        except (FileNotFoundError, json.JSONDecodeError):
            self.index = []
            # Создаем пустой файл, если его нет
            with open('search_index.json', 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def tokenize(self, text):
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        tokens = text.split()
        return tokens
    
    def calculate_tf_idf(self, query_tokens, document_tokens):
        doc_counter = Counter(document_tokens)
        total_terms = len(document_tokens)
        score = 0
        for token in query_tokens:
            tf = doc_counter.get(token, 0) / max(total_terms, 1)
            doc_freq = sum(1 for item in self.index if token in item.get('search_text', ''))
            idf = log(len(self.index) / max(doc_freq, 1)) if len(self.index) > 0 else 0
            score += tf * idf
        return score
    
    def calculate_semantic_score(self, query, stone):
        query_words = set(self.tokenize(query))
        stone_words = set(self.tokenize(stone.get('search_text', '')))
        common = query_words & stone_words
        jaccard = len(common) / max(len(query_words | stone_words), 1)
        weighted_score = 0
        for word in common:
            max_ratio = max(
                SequenceMatcher(None, word, stone_word).ratio()
                for stone_word in stone_words
            )
            weighted_score += max_ratio
        return jaccard * 0.5 + weighted_score * 0.5
    
    def search(self, query, filters=None, sort_by='relevance', page=1, per_page=12):
        if not self.index:
            return {
                'results': [],
                'total': 0,
                'page': page,
                'pages': 0
            }
        
        if not query:
            return self.get_all_stones(filters, sort_by, page, per_page)
        
        query_tokens = self.tokenize(query)
        results = []
        for stone in self.index:
            doc_tokens = self.tokenize(stone.get('search_text', ''))
            tfidf_score = self.calculate_tf_idf(query_tokens, doc_tokens)
            semantic_score = self.calculate_semantic_score(query, stone)
            relevance = tfidf_score * 0.6 + semantic_score * 0.4
            
            if filters and not self.apply_filters(stone, filters):
                continue
            
            results.append({
                'id': stone['id'],
                'name': stone['name'],
                'slug': stone['slug'],
                'image': stone.get('main_image'),
                'relevance': relevance,
                'features': stone.get('features', {})
            })
        
        results.sort(key=lambda x: x['relevance'], reverse=True)
        
        if sort_by == 'price_asc':
            results.sort(key=lambda x: x['features'].get('price', 0))
        elif sort_by == 'price_desc':
            results.sort(key=lambda x: -x['features'].get('price', 0))
        elif sort_by == 'hardness':
            results.sort(key=lambda x: -x['features'].get('hardness', 0))
        elif sort_by == 'popularity':
            results.sort(key=lambda x: -x.get('popularity', 0))
        
        start = (page - 1) * per_page
        end = start + per_page
        
        return {
            'results': results[start:end],
            'total': len(results),
            'page': page,
            'pages': (len(results) + per_page - 1) // per_page if results else 0
        }
    
    def apply_filters(self, stone, filters):
        features = stone.get('features', {})
        
        if 'min_price' in filters and features.get('price', 0) < filters['min_price']:
            return False
        if 'max_price' in filters and features.get('price', 0) > filters['max_price']:
            return False
        if 'min_hardness' in filters and features.get('hardness', 0) < filters['min_hardness']:
            return False
        if 'max_hardness' in filters and features.get('hardness', 0) > filters['max_hardness']:
            return False
        if 'max_water' in filters and features.get('water_absorption', 0) > filters['max_water']:
            return False
        if 'category' in filters and features.get('category_id') != filters['category']:
            return False
        
        return True
    
    def get_all_stones(self, filters, sort_by, page, per_page):
        results = []
        for stone in self.index:
            if filters and not self.apply_filters(stone, filters):
                continue
            results.append({
                'id': stone['id'],
                'name': stone['name'],
                'slug': stone['slug'],
                'image': stone.get('main_image'),
                'relevance': 1.0,
                'features': stone.get('features', {})
            })
        
        if sort_by == 'price_asc':
            results.sort(key=lambda x: x['features'].get('price', 0))
        elif sort_by == 'price_desc':
            results.sort(key=lambda x: -x['features'].get('price', 0))
        elif sort_by == 'hardness':
            results.sort(key=lambda x: -x['features'].get('hardness', 0))
        
        start = (page - 1) * per_page
        end = start + per_page
        
        return {
            'results': results[start:end],
            'total': len(results),
            'page': page,
            'pages': (len(results) + per_page - 1) // per_page if results else 0
        }
    
    def suggest(self, query, limit=5):
        if len(query) < 2 or not self.index:
            return []
        
        query_lower = query.lower()
        suggestions = []
        
        for stone in self.index:
            name = stone.get('name', '').lower()
            if query_lower in name:
                suggestions.append({
                    'text': stone['name'],
                    'type': 'stone',
                    'slug': stone['slug']
                })
            if len(suggestions) >= limit:
                break
        
        return suggestions[:limit]