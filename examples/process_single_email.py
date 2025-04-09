import os
import sys
import json
from dotenv import load_dotenv

# Add the parent directory to the path so we can import our package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from insurance_triage import InsuranceEmailTriageCrew

def main():
    # Load environment variables
    load_dotenv()
    
    # Example email
    sample_email = """ From: client@example.com
    Subject: Claim Notification - Policy ABC123456
    
    Dear Insurance Broker,
    
    I am writing to notify you of an incident that occurred on 04/02/2025 at our business premises.
    
    Policy Number: ABC123456
    Insured Name: Acme Corporation
    Claim ID: CLM20250402
    
    Water damage occurred due to a burst pipe in our warehouse section. We have taken steps
    to minimize the damage, but require an adjuster to assess the situation as soon as possible.
    
    This is urgent as we need to resume operations quickly.
    
    Regards,
    John Smith
    Operations Manager
    Acme Corporation """
    
    # Initialize the email triage crew
    triage_crew = InsuranceEmailTriageCrew()
    
    # Process the email
    email_metadata = {
        "sender": "client@example.com",
        "received_time": "2025-04-02T09:15:00",
        "subject": "Claim Notification - Policy ABC123456",
        "has_attachments": False
    }
    
    print("Processing email...")
    result = triage_crew.process_single_email(sample_email, email_metadata)
    
    # Display the results
    print("\n===== Email Triage Results =====")
    print(f"Email Type: {result['classification']['email_type']}")
    print(f"Urgency: {result['classification']['urgency']}")
    print(f"Sentiment: {result['classification']['sentiment']}")
    print(f"\nPolicy Number: {result['classification']['structured_data']['policy_number']}")
    print(f"Claim ID: {result['classification']['structured_data']['claim_id']}")
    print(f"Insured Name: {result['classification']['structured_data']['insured_name']}")
    
    print(f"\nSummary: {result['summary']}")
    print(f"\nRouting: {result['routing']['team']} (Priority: {result['routing']['priority']})")
    print(f"Manual Review: {'Yes' if result['routing']['requires_manual_review'] else 'No'}")
    if result['routing']['reason']:
        print(f"Reason: {', '.join(result['routing']['reason'])}")
    
    print(f"\nSuggested Response:\n{result['suggested_response']}")
    
    if result['compliance_issues']:
        print(f"\nCompliance Issues: {result['compliance_issues']}")
    else:
        print("\nNo compliance issues detected.")
    
    # Save the results to a file
    with open("triage_result.json", "w") as f:
        json.dump(result, f, indent=2)
    print("\nResults saved to triage_result.json")

if __name__ == "__main__":
    main()