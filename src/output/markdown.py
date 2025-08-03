"""
Markdown report generator for Arxiv papers.
"""
import datetime
import json
import os
from typing import Dict, List, Optional

class MarkdownReportGenerator:
    def __init__(self, config_path: str = "config/config.json"):
        """Initialize the Markdown report generator with configuration."""
        with open(config_path, 'r') as f:
            self.config = json.load(f)['report']
        
        self.output_directory = self.config['output_directory']
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_directory, exist_ok=True)
    
    def generate_paper_section(self, paper: Dict) -> str:
        """
        Generate Markdown for a single paper.
        
        Args:
            paper: Paper object with metadata and analysis
            
        Returns:
            Markdown string for the paper
        """
        # Format the paper section
        markdown = f"## [{paper['title']}]({paper['arxiv_url']})\n\n"
        markdown += f"**Authors:** {', '.join(paper['authors'])}\n\n"
        markdown += f"**Published:** {paper['published_date']}\n\n"
        markdown += f"**Categories:** {', '.join(paper['categories'])}\n\n"
        
        # Add citation information if available
        if 'citation_count' in paper and paper['citation_count'] > 0:
            markdown += f"**Citations:** {paper['citation_count']}\n\n"
        
        # Add abstract
        markdown += f"**Abstract:**\n\n{paper['abstract']}\n\n"
        
        # Add AI analysis if available
        if 'analysis' in paper:
            markdown += f"**Analysis:**\n\n{paper['analysis']}\n\n"
        
        # Add key findings
        if 'key_findings' in paper and paper['key_findings']:
            markdown += "**Key Findings:**\n\n"
            for finding in paper['key_findings']:
                markdown += f"- {finding}\n"
            markdown += "\n"
        
        # Add links
        markdown += "**Links:**\n\n"
        markdown += f"- [PDF]({paper['pdf_url']})\n"
        markdown += f"- [arXiv]({paper['arxiv_url']})\n"
        
        if 'citation_url' in paper and paper['citation_url']:
            markdown += f"- [Citations]({paper['citation_url']})\n"
        
        markdown += "\n---\n\n"
        
        return markdown
    
    def generate_daily_report(self, papers: List[Dict], 
                             report_summary: Optional[str] = None,
                             date: Optional[str] = None) -> str:
        """
        Generate a daily report in Markdown format.
        
        Args:
            papers: List of paper objects
            report_summary: Optional executive summary of the report
            date: Optional date string (defaults to today)
            
        Returns:
            Markdown string for the report
        """
        # Use provided date or today's date
        if date is None:
            date = datetime.datetime.now().strftime('%Y-%m-%d')
        
        # Start with the report header
        markdown = f"# Arxiv Computer Vision Papers - {date}\n\n"
        
        # Add report summary if available
        if report_summary:
            markdown += "## Executive Summary\n\n"
            markdown += f"{report_summary}\n\n"
            markdown += "---\n\n"
        
        # Add table of contents
        markdown += "## Table of Contents\n\n"
        for i, paper in enumerate(papers, 1):
            markdown += f"{i}. [{paper['title']}](#{paper['id']})\n"
        markdown += "\n---\n\n"
        
        # Add each paper
        markdown += "## Papers\n\n"
        for paper in papers:
            # Add an anchor for the TOC
            markdown += f"<a id='{paper['id']}'></a>\n"
            markdown += self.generate_paper_section(paper)
        
        return markdown
    
    def save_report(self, markdown: str, filename: Optional[str] = None) -> str:
        """
        Save the Markdown report to a file.
        
        Args:
            markdown: Markdown content
            filename: Optional filename (defaults to date-based name)
            
        Returns:
            Path to the saved file
        """
        if filename is None:
            date = datetime.datetime.now().strftime('%Y-%m-%d')
            filename = f"arxiv_cv_report_{date}.md"
        
        filepath = os.path.join(self.output_directory, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        print(f"Report saved to {filepath}")
        return filepath
    
    def convert_to_html(self, markdown_path: str) -> str:
        """
        Convert Markdown report to HTML.
        
        Args:
            markdown_path: Path to the Markdown file
            
        Returns:
            Path to the HTML file
        """
        try:
            import markdown
            
            # Read the Markdown file
            with open(markdown_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Convert to HTML
            html = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
            
            # Add basic styling
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>Arxiv Computer Vision Report</title>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                        line-height: 1.6;
                        max-width: 900px;
                        margin: 0 auto;
                        padding: 20px;
                        color: #333;
                    }}
                    h1, h2, h3 {{
                        color: #2c3e50;
                    }}
                    a {{
                        color: #3498db;
                        text-decoration: none;
                    }}
                    a:hover {{
                        text-decoration: underline;
                    }}
                    code {{
                        background-color: #f8f8f8;
                        padding: 2px 4px;
                        border-radius: 3px;
                    }}
                    pre {{
                        background-color: #f8f8f8;
                        padding: 10px;
                        border-radius: 5px;
                        overflow-x: auto;
                    }}
                    blockquote {{
                        border-left: 4px solid #ccc;
                        padding-left: 15px;
                        color: #666;
                        margin: 15px 0;
                    }}
                    hr {{
                        border: 0;
                        border-top: 1px solid #eee;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                {html}
            </body>
            </html>
            """
            
            # Save the HTML file
            html_path = markdown_path.replace('.md', '.html')
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(styled_html)
            
            print(f"HTML report saved to {html_path}")
            return html_path
            
        except ImportError:
            print("Warning: 'markdown' package not installed. Skipping HTML conversion.")
            return ""