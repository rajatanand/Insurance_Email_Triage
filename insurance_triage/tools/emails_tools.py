import re
import json
import datetime
from typing import Dict, List, Any

class EmailTools:
    """Tools for processing insurance-related emails."""
    
    @staticmethod
    def extract_email_data(email_content: str) -> Dict[str, Any]:
        """Extract key data points from email content."""
        structured_data = EmailTools._extract_policy_info(email_content)
        email_type = EmailTools._detect_email_type(email_content)
        urgency = EmailTools._detect_urgency(email_content)
        sentiment = EmailTools._analyze_sentiment(email_content)
        compliance_issues = EmailTools._detect_compliance_issues(email_content)
        
        return {
            "structured_data": structured_data,
            "email_type": email_type,
            "urgency": urgency,
            "sentiment": sentiment,
            "compliance_issues": compliance_issues
        }
    
    @staticmethod
    def generate_email_summary(email_content: str, extracted_data: Dict) -> str:
        """Create a concise summary of the email."""
        email_type = extracted_data["email_type"]
        urgency = extracted_data["urgency"]
        structured_data = extracted_data["structured_data"]
        compliance_issues = extracted_data["compliance_issues"]
        
        summary = f"This is a {urgency} priority {email_type} email"
        
        if structured_data["insured_name"]:
            summary += f" regarding {structured_data['insured_name']}"
        
        if structured_data["policy_number"]:
            summary += f" (Policy: {structured_data['policy_number']})"
        
        if structured_data["claim_id"]:
            summary += f" (Claim: {structured_data['claim_id']})"
        
        if structured_data["key_date"]:
            summary += f" with a key date of {structured_data['key_date']}"
        
        if compliance_issues:
            summary += f". Compliance flags: {', '.join(compliance_issues)}"
        
        # Add first 150 characters of the email for context
        short_preview = email_content[:150].replace("\n", " ").strip()
        if len(email_content) > 150:
            short_preview += "..."
        
        summary += f"\n\nPreview: {short_preview}"
        
        return summary
    
    @staticmethod
    def determine_routing(extracted_data: Dict) -> Dict[str, Any]:
        """Determine where the email should be routed."""
        email_type = extracted_data["email_type"]
        urgency = extracted_data["urgency"]
        compliance_issues = extracted_data["compliance_issues"]
        
        routing = {
            "team": None,
            "priority": urgency,
            "requires_manual_review": False,
            "reason": []
        }
        
        # Route based on email type
        if email_type == "Submission":
            routing["team"] = "Underwriting"
        elif email_type in ["Claim", "FNOL"]:
            routing["team"] = "Claims"
        elif email_type in ["Policy Change", "Renewal"]:
            routing["team"] = "Policy Administration"
        elif email_type == "Regulatory":
            routing["team"] = "Compliance"
            routing["requires_manual_review"] = True
            routing["reason"].append("Regulatory email requires compliance review")
        else:  # Inquiry or Other
            routing["team"] = "Customer Service"
        
        # Adjust for compliance issues
        if compliance_issues:
            routing["requires_manual_review"] = True
            routing["reason"].append(f"Compliance issues detected: {', '.join(compliance_issues)}")
        
        # High urgency emails might need special handling
        if urgency == "High":
            routing["requires_manual_review"] = True
            routing["reason"].append("High urgency email requires immediate attention")
        
        return routing
    
    @staticmethod
    def suggest_response_template(extracted_data: Dict) -> str:
        """Suggest a response template based on the email analysis."""
        email_type = extracted_data["email_type"]
        structured_data = extracted_data["structured_data"]
        
        templates = {
            "Submission": "Thank you for your submission. We have received your request and will review the details. A broker will contact you shortly regarding {policy_details}.",
            "Claim": "We acknowledge receipt of your claim notification. Your claim ({claim_id}) has been logged and assigned to a claims handler who will be in touch within 24 hours.",
            "FNOL": "We have received your First Notice of Loss. A claims representative will contact you within 24 hours to gather additional information and guide you through the next steps.",
            "Policy Change": "Thank you for your policy change request for Policy {policy_number}. We are processing your request and will confirm the changes shortly.",
            "Renewal": "We acknowledge receipt of your renewal request for Policy {policy_number}. We will process this promptly and provide updated terms before the renewal date.",
            "Regulatory": "Your message has been received and forwarded to our compliance team for immediate review.",
            "Inquiry": "Thank you for your inquiry. We aim to respond to all queries within 1 business day."
        }
        
        template = templates.get(email_type, templates["Inquiry"])
        
        # Fill in template placeholders with actual data
        if "{policy_number}" in template and structured_data["policy_number"]:
            template = template.replace("{policy_number}", structured_data["policy_number"])
        elif "{policy_number}" in template:
            template = template.replace("{policy_number}", "[Policy Number]")
            
        if "{claim_id}" in template and structured_data["claim_id"]:
            template = template.replace("{claim_id}", structured_data["claim_id"])
        elif "{claim_id}" in template:
            template = template.replace("{claim_id}", "[Claim ID]")
            
        if "{policy_details}" in template and structured_data["insured_name"]:
            template = template.replace("{policy_details}", f"insurance for {structured_data['insured_name']}")
        elif "{policy_details}" in template:
            template = template.replace("{policy_details}", "your insurance needs")
        
        return template
    
    # Private helper methods
    @staticmethod
    def _extract_policy_info(email_text: str) -> Dict[str, Any]:
        """Extract policy numbers, claim IDs, and other structured data from email text."""
        policy_pattern = r"Policy(?:\s+Number)?(?:\s*:)?\s*([A-Z0-9-]+)"
        claim_pattern = r"Claim(?:\s+Number|ID)?(?:\s*:)?\s*([A-Z0-9-]+)"
        date_pattern = r"(?:Due|Renewal|Effective)(?:\s+Date)?(?:\s*:)?\s*(\d{1,2}[\/\.-]\d{1,2}[\/\.-]\d{2,4})"
        
        policy_match = re.search(policy_pattern, email_text, re.IGNORECASE)
        claim_match = re.search(claim_pattern, email_text, re.IGNORECASE)
        date_match = re.search(date_pattern, email_text, re.IGNORECASE)
        
        # Extract insured name (simplified logic)
        insured_pattern = r"(?:Insured|Client|Customer)(?:\s+Name)?(?:\s*:)?\s*([A-Za-z0-9\s,\.]+?)(?:\n|,|;)"
        insured_match = re.search(insured_pattern, email_text, re.IGNORECASE)
        
        structured_data = {
            "policy_number": policy_match.group(1) if policy_match else None,
            "claim_id": claim_match.group(1) if claim_match else None,
            "key_date": date_match.group(1) if date_match else None,
            "insured_name": insured_match.group(1).strip() if insured_match else None,
        }
        
        return structured_data
    
    @staticmethod
    def _detect_email_type(email_text: str) -> str:
        """Determine the type of insurance email."""
        email_text_lower = email_text.lower()
        
        # Define keywords for different email types
        submission_keywords = ["new business", "submission", "quote request", "application", "risk details"]
        claim_keywords = ["claim notification", "claim report", "incident report", "loss report"]
        fnol_keywords = ["first notice", "fnol", "incident occurred", "accident report"]
        policy_change_keywords = ["endorsement", "policy change", "amend coverage", "update policy"]
        renewal_keywords = ["renewal", "policy expiring", "extend coverage"]
        regulatory_keywords = ["compliance", "regulation", "audit", "regulator", "regulatory"]
        
        # Check for each type
        if any(keyword in email_text_lower for keyword in submission_keywords):
            return "Submission"
        elif any(keyword in email_text_lower for keyword in fnol_keywords):
            return "FNOL"
        elif any(keyword in email_text_lower for keyword in claim_keywords):
            return "Claim"
        elif any(keyword in email_text_lower for keyword in policy_change_keywords):
            return "Policy Change"
        elif any(keyword in email_text_lower for keyword in renewal_keywords):
            return "Renewal"
        elif any(keyword in email_text_lower for keyword in regulatory_keywords):
            return "Regulatory"
        else:
            return "Inquiry"
    
    @staticmethod
    def _detect_urgency(email_text: str) -> str:
        """Determine the urgency level of the email."""
        email_text_lower = email_text.lower()
        
        urgent_keywords = ["urgent", "immediately", "asap", "emergency", "critical", 
                          "deadline", "today", "time sensitive", "expedite", "priority"]
        high_priority_count = sum(1 for keyword in urgent_keywords if keyword in email_text_lower)
        
        if high_priority_count >= 2 or "urgent" in email_text_lower:
            return "High"
        elif high_priority_count >= 1:
            return "Medium"
        else:
            return "Normal"
    
    @staticmethod
    def _analyze_sentiment(email_text: str) -> str:
        """Analyze sentiment of the email (simplified)."""
        email_text_lower = email_text.lower()
        
        negative_words = ["dissatisfied", "unhappy", "disappointed", "frustrated", 
                          "complaint", "error", "mistake", "delay", "poor", "issue"]
        positive_words = ["thank", "appreciate", "happy", "pleased", "satisfied", 
                          "excellent", "good", "great", "helpful"]
        
        negative_count = sum(1 for word in negative_words if word in email_text_lower)
        positive_count = sum(1 for word in positive_words if word in email_text_lower)
        
        if negative_count > positive_count + 1:
            return "Negative"
        elif positive_count > negative_count + 1:
            return "Positive"
        else:
            return "Neutral"
    
    @staticmethod
    def _detect_compliance_issues(email_text: str) -> List[str]:
        """Identify potential compliance or regulatory issues in the email."""
        email_text_lower = email_text.lower()
        
        compliance_keywords = {
            "GDPR": ["gdpr", "personal data", "data protection", "privacy", "right to be forgotten"],
            "Money Laundering": ["money laundering", "suspicious transaction", "aml", "kyc"],
            "Fraud": ["fraud", "suspicious", "misrepresentation", "false"],
            "Sanctions": ["sanction", "restricted", "ofac", "embargo"],
            "Regulatory": ["fca", "regulation", "compliance", "regulatory", "lloyd's market"]
        }
        
        issues = []
        for issue_type, keywords in compliance_keywords.items():
            if any(keyword in email_text_lower for keyword in keywords):
                issues.append(issue_type)
        
        return issues