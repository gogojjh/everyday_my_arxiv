"""
Parser for Arxiv papers to extract relevant information and match keywords.
"""
import json
import re
from typing import Dict, List, Tuple

class ArxivParser:
    def __init__(self, keywords_path: str = "config/keywords.json"):
        """Initialize the parser with keyword configuration."""
        with open(keywords_path, 'r') as f:
            self.keywords_config = json.load(f)
        
        self.primary_keywords = self.keywords_config['primary_keywords']
        self.secondary_keywords = self.keywords_config['secondary_keywords']
        self.exclude_keywords = self.keywords_config['exclude_keywords']
        self.author_preferences = self.keywords_config.get('author_preferences', [])
        self.weight_factors = self.keywords_config['weight_factors']
        self.minimum_match_score = self.keywords_config['minimum_match_score']
    
    def match_keywords(self, paper: Dict) -> Tuple[float, Dict]:
        """
        Match keywords in the paper title and abstract.
        
        Args:
            paper: Paper object with title and abstract
            
        Returns:
            Tuple of (match_score, match_details)
        """
        title = paper['title'].lower()
        abstract = paper['abstract'].lower()
        
        # Initialize match details
        match_details = {
            'primary_matches': [],
            'secondary_matches': [],
            'excluded_matches': [],
            'author_matches': []
        }
        
        # Check for primary keywords
        for keyword in self.primary_keywords:
            if keyword.lower() in title:
                match_details['primary_matches'].append({
                    'keyword': keyword,
                    'location': 'title',
                    'weight': self.weight_factors['title_match'] * self.weight_factors['primary_keyword_match']
                })
            elif keyword.lower() in abstract:
                match_details['primary_matches'].append({
                    'keyword': keyword,
                    'location': 'abstract',
                    'weight': self.weight_factors['abstract_match'] * self.weight_factors['primary_keyword_match']
                })
        
        # Check for secondary keywords
        for keyword in self.secondary_keywords:
            if keyword.lower() in title:
                match_details['secondary_matches'].append({
                    'keyword': keyword,
                    'location': 'title',
                    'weight': self.weight_factors['title_match'] * self.weight_factors['secondary_keyword_match']
                })
            elif keyword.lower() in abstract:
                match_details['secondary_matches'].append({
                    'keyword': keyword,
                    'location': 'abstract',
                    'weight': self.weight_factors['abstract_match'] * self.weight_factors['secondary_keyword_match']
                })
        
        # Check for excluded keywords
        for keyword in self.exclude_keywords:
            if keyword.lower() in title or keyword.lower() in abstract:
                match_details['excluded_matches'].append(keyword)
        
        # Check for preferred authors
        for author in self.author_preferences:
            if author.lower() in [a.lower() for a in paper['authors']]:
                match_details['author_matches'].append(author)
        
        # Calculate match score
        match_score = 0.0
        
        # Add scores from primary matches
        for match in match_details['primary_matches']:
            match_score += match['weight']
        
        # Add scores from secondary matches
        for match in match_details['secondary_matches']:
            match_score += match['weight']
        
        # Add bonus for preferred authors
        if match_details['author_matches']:
            match_score += 1.0
        
        # Penalize excluded keywords
        if match_details['excluded_matches']:
            match_score -= 2.0
        
        return match_score, match_details
    
    def filter_papers_by_keywords(self, papers: List[Dict]) -> List[Dict]:
        """
        Filter papers based on keyword matching.
        
        Args:
            papers: List of paper objects
            
        Returns:
            Filtered list of papers with match scores
        """
        filtered_papers = []
        
        for paper in papers:
            match_score, match_details = self.match_keywords(paper)
            
            # Only include papers that meet the minimum match score
            if match_score >= self.minimum_match_score:
                paper['match_score'] = match_score
                paper['match_details'] = match_details
                filtered_papers.append(paper)
        
        # Sort by match score (descending)
        filtered_papers.sort(key=lambda x: x['match_score'], reverse=True)
        
        return filtered_papers
    
    def extract_key_findings(self, abstract: str) -> List[str]:
        """
        Extract key findings from the abstract using simple heuristics.
        
        Args:
            abstract: Paper abstract
            
        Returns:
            List of key findings
        """
        # Split abstract into sentences
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', abstract)
        
        key_findings = []
        
        # Look for sentences with indicator phrases
        indicator_phrases = [
            "we propose", "we present", "we introduce", "we develop",
            "results show", "our approach", "our method", "we demonstrate",
            "we achieve", "we show", "outperforms", "state-of-the-art",
            "contribution", "novel", "new"
        ]
        
        for sentence in sentences:
            for phrase in indicator_phrases:
                if phrase.lower() in sentence.lower():
                    key_findings.append(sentence.strip())
                    break
        
        # If no key findings found, use the last 1-2 sentences (often contain conclusions)
        if not key_findings and len(sentences) > 1:
            key_findings = [sentences[-2].strip(), sentences[-1].strip()]
        elif not key_findings and sentences:
            key_findings = [sentences[-1].strip()]
        
        return key_findings
    
    def enrich_paper_data(self, paper: Dict) -> Dict:
        """
        Enrich paper data with additional information.
        
        Args:
            paper: Paper object
            
        Returns:
            Enriched paper object
        """
        # Extract key findings from abstract
        paper['key_findings'] = self.extract_key_findings(paper['abstract'])
        
        # Format author list
        if len(paper['authors']) > 3:
            paper['formatted_authors'] = f"{paper['authors'][0]} et al."
        else:
            paper['formatted_authors'] = ", ".join(paper['authors'])
        
        # Create a short ID for reference
        paper['short_id'] = paper['id'].split('.')[-1]
        
        # Add arxiv URL
        paper['arxiv_url'] = f"https://arxiv.org/abs/{paper['id']}"
        
        return paper