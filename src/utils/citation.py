"""
Citation metrics utilities for Arxiv papers.
"""
import datetime
from typing import Dict, List, Optional, Tuple

class CitationAnalyzer:
    def __init__(self, min_citations_for_highlight: int = 5):
        """Initialize the citation analyzer."""
        self.min_citations_for_highlight = min_citations_for_highlight
    
    def identify_highly_cited_papers(self, papers: List[Dict]) -> List[Dict]:
        """
        Identify highly cited papers from a list.
        
        Args:
            papers: List of paper objects with citation data
            
        Returns:
            List of highly cited papers
        """
        highly_cited = []
        
        for paper in papers:
            if paper.get('citation_count', 0) >= self.min_citations_for_highlight:
                highly_cited.append(paper)
        
        # Sort by citation count (descending)
        highly_cited.sort(key=lambda x: x.get('citation_count', 0), reverse=True)
        
        return highly_cited
    
    def calculate_citation_velocity(self, papers: List[Dict]) -> List[Dict]:
        """
        Calculate citation velocity (citations per day) for papers.
        
        Args:
            papers: List of paper objects with citation data and published date
            
        Returns:
            List of papers with citation velocity added
        """
        today = datetime.datetime.now().date()
        
        for paper in papers:
            if 'citation_count' in paper and 'published_date' in paper:
                # Parse published date
                try:
                    pub_date = datetime.datetime.strptime(paper['published_date'], '%Y-%m-%d').date()
                    days_since_pub = max(1, (today - pub_date).days)  # Avoid division by zero
                    
                    # Calculate velocity
                    paper['citation_velocity'] = paper['citation_count'] / days_since_pub
                except (ValueError, TypeError):
                    paper['citation_velocity'] = 0
            else:
                paper['citation_velocity'] = 0
        
        return papers
    
    def rank_papers_by_impact(self, papers: List[Dict]) -> List[Dict]:
        """
        Rank papers by estimated impact (combination of citations and recency).
        
        Args:
            papers: List of paper objects with citation data
            
        Returns:
            List of papers sorted by impact score
        """
        # First calculate citation velocity
        papers_with_velocity = self.calculate_citation_velocity(papers)
        
        # Calculate impact score (weighted combination of citation count and velocity)
        for paper in papers_with_velocity:
            citation_count = paper.get('citation_count', 0)
            citation_velocity = paper.get('citation_velocity', 0)
            
            # Impact score formula: weight both raw count and velocity
            paper['impact_score'] = (0.7 * citation_count) + (0.3 * citation_velocity * 10)
        
        # Sort by impact score
        sorted_papers = sorted(papers_with_velocity, key=lambda x: x.get('impact_score', 0), reverse=True)
        
        return sorted_papers