"""
Email notification module for Arxiv paper reports.
"""
import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Optional

class EmailNotifier:
    def __init__(self, config_path: str = "config/config.json"):
        """Initialize the email notifier with configuration."""
        with open(config_path, 'r') as f:
            self.config = json.load(f)['email']
        
        self.enabled = self.config['enabled']
        self.subject_prefix = self.config['subject_prefix']
        self.include_full_report = self.config['include_full_report']
        self.include_summary = self.config['include_summary']
        
        # Get email credentials from environment variables
        self.smtp_server = os.environ.get("EMAIL_SMTP_SERVER")
        self.smtp_port = int(os.environ.get("EMAIL_SMTP_PORT", "587"))
        self.sender_email = os.environ.get("EMAIL_SENDER")
        self.sender_password = os.environ.get("EMAIL_PASSWORD")
        self.recipient_email = os.environ.get("EMAIL_RECIPIENT")
        
        # Validate required environment variables
        if self.enabled and (not self.smtp_server or not self.sender_email or 
                           not self.sender_password or not self.recipient_email):
            print("Warning: Email notification is enabled but required environment variables are missing.")
            self.enabled = False
    
    def send_report_email(self, 
                         subject: str, 
                         summary: str, 
                         full_report: Optional[str] = None,
                         html_report_path: Optional[str] = None) -> bool:
        """
        Send an email with the report.
        
        Args:
            subject: Email subject
            summary: Report summary
            full_report: Optional full report content
            html_report_path: Optional path to HTML report file
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        if not self.enabled:
            print("Email notification is disabled.")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"{self.subject_prefix} {subject}"
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            
            # Create plain text content
            text_content = summary
            
            if self.include_full_report and full_report:
                text_content += "\n\n--- FULL REPORT ---\n\n" + full_report
            
            msg.attach(MIMEText(text_content, 'plain'))
            
            # Add HTML content if available
            if html_report_path and os.path.exists(html_report_path):
                with open(html_report_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                msg.attach(MIMEText(html_content, 'html'))
            
            # Connect to server and send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            
            print(f"Email sent successfully to {self.recipient_email}")
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_report_notification(self, 
                               date: str, 
                               paper_count: int,
                               report_summary: str,
                               markdown_report_path: str,
                               html_report_path: Optional[str] = None) -> bool:
        """
        Send a notification email about the generated report.
        
        Args:
            date: Report date
            paper_count: Number of papers in the report
            report_summary: Summary of the report
            markdown_report_path: Path to the Markdown report
            html_report_path: Optional path to the HTML report
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        subject = f"CV Papers Report for {date} - {paper_count} papers"
        
        # Read the full report if needed
        full_report = None
        if self.include_full_report:
            try:
                with open(markdown_report_path, 'r', encoding='utf-8') as f:
                    full_report = f.read()
            except Exception as e:
                print(f"Error reading report file: {e}")
        
        # Send the email
        return self.send_report_email(
            subject=subject,
            summary=report_summary,
            full_report=full_report,
            html_report_path=html_report_path
        )