#!/usr/bin/env python3
"""
Local testing script for the Arxiv paper report system.
"""
import argparse
import json
import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Run a local test of the Arxiv paper report system."""
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Test the Arxiv paper report system locally")
    parser.add_argument("--config", default="config/config.json", help="Path to config file")
    parser.add_argument("--keywords", default="config/keywords.json", help="Path to keywords file")
    parser.add_argument("--papers", type=int, default=3, help="Number of papers to process")
    parser.add_argument("--no-email", action="store_true", help="Disable email notification")
    args = parser.parse_args()
    
    # Temporarily modify the config for testing
    with open(args.config, 'r') as f:
        config = json.load(f)
    
    # Reduce the number of papers for testing
    config['report']['max_papers'] = args.papers
    
    # Save the modified config to a temporary file
    temp_config_path = "config/temp_config.json"
    with open(temp_config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Run the main script with the temporary config
    cmd = [
        "python", "scripts/run_daily_report.py",
        "--config", temp_config_path,
        "--keywords", args.keywords
    ]
    
    if args.no_email:
        cmd.append("--no-email")
    
    print(f"Running command: {' '.join(cmd)}")
    os.system(" ".join(cmd))
    
    # Clean up
    if os.path.exists(temp_config_path):
        os.remove(temp_config_path)

if __name__ == "__main__":
    main()