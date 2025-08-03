"""
Filter utilities for Arxiv papers.
"""
import datetime
from typing import Dict, List, Optional, Tuple

class PaperFilter:
    def __init__(self):
        """Initialize the paper filter."""
        pass
    
    def filter_by_date(self, papers: List[Dict], days: int = 2) -> List[Dict]:
        """
        Filter papers by publication date.
        
        Args:
            papers: List of paper objects
            days: Number of days to look back
            
        Returns:
            Filtered list of papers
        """
        today = datetime.datetime.now().date()
        date_cutoff = today - datetime.timedelta(days=days)
        
        filtered_papers = []
        for paper in papers:
            try:
                pub_date = datetime.datetime.strptime(paper['published_date'], '%Y-%m-%d').date()
                if pub_date >= date_cutoff:
                    filtered_papers.append(paper)
            except (ValueError, KeyError):
                # Skip papers with invalid date format
                continue
        
        return filtered_papers
    
    def filter_by_category(self, papers: List[Dict], categories: List[str]) -> List[Dict]:
        """
        Filter papers by category.
        
        Args:
            papers: List of paper objects
            categories: List of categories to include
            
        Returns:
            Filtered list of papers
        """
        filtered_papers = []
        for paper in papers:
            # Check if any of the paper's categories match the filter categories
            if any(category in paper.get('categories', []) for category in categories):
                filtered_papers.append(paper)
        
        return filtered_papers
    
    def filter_duplicates(self, papers: List[Dict]) -> List[Dict]:
        """
        Remove duplicate papers based on ID.
        
        Args:
            papers: List of paper objects
            
        Returns:
            Deduplicated list of papers
        """
        seen_ids = set()
        unique_papers = []
        
        for paper in papers:
            if paper['id'] not in seen_ids:
                seen_ids.add(paper['id'])
                unique_papers.append(paper)
        
        return unique_papers
    
    def limit_papers(self, papers: List[Dict], limit: int) -> List[Dict]:
        """
        Limit the number of papers.
        
        Args:
            papers: List of paper objects
            limit: Maximum number of papers to include
            
        Returns:
            Limited list of papers
        """
        return papers[:limit]