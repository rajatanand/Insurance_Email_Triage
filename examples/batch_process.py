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
    
    # Sample emails for batch processing
    sample_emails = [
        {
            "content": """
            Subject: New Business Application - Commercial Property
            
            Dear Underwriter,
            
            I would like to submit a new business application for commercial property insurance.
            
            Insured Name: TechInnov Ltd
            Property Address: 123 Business Park, London, EC1A 1BB
            Business Type: Software Development Office
            Coverage Required: Building, Contents, Business Interruption
            
            Please find attached our completed application form and risk assessment.
            
            We would appreciate receiving a quote at your earliest convenience.
            
            Best regards,
            Robert Johnson
            Financial Director
            TechInnov Ltd
            """,
            "sender": "robert.johnson@techinnov.example.com",
            "subject": "New Business Application - Commercial Property",
            "received_time": "2025-04-01T14:30:00",
            "has_attachments": True
        },
        {
            "content": """
            Subject: URGENT - First Notice of Loss - Policy REF78901
            
            Dear Claims Department,
            
            This is to notify you of an incident that occurred today at our retail store.
            
            Policy Number: REF78901
            Insured Name: Fashion Boutique Ltd
            
            At approximately 9:30 AM today, a vehicle crashed through our storefront window,
            causing significant damage to our premises and inventory. Fortunately, no one was injured.
            
            The police have been notified (Incident #POL-2025-04-02-339) and we have secured the 
            premises as best as possible.
            
            This is urgent as we need to make repairs immediately to secure the property.
            
            Please contact me ASAP to discuss next steps.
            
            Regards,
            Sarah Williams
            Store Manager
            Fashion Boutique Ltd
            Tel: 07700 900123
            """,
            "sender": "s.williams@fashionboutique.example.com",
            "subject": "URGENT - First Notice of Loss - Policy REF78901",
            "received_time": "2025-04-02T10:45:00",
            "has_attachments": False
        },
        {
            "content": """
            Subject: Policy Renewal - Policy Number DPL543210
            
            Dear Insurance Broker,
            
            Our professional indemnity insurance policy is due for renewal on 01/05/2025.
            
            Policy Number: DPL543210
            Insured Name: Smith & Partners Legal LLP
            Policy Type: Professional Indemnity
            Renewal Date: 01/05/2025
            
            We would like to proceed with renewal. Please let us know if you need any updated information.
            
            Our business operations remain largely unchanged from last year, with a slight increase in
            staff (now 24 employees) and revenue (projected £3.2M).
            
            Kind regards,
            Michael Carter
            Office Manager
            Smith & Partners Legal LLP
            """,
            "sender": "m.carter@smithpartners.example.com",
            "subject": "Policy Renewal - Policy Number DPL543210",
            "received_time": "2025-04-01T16:20:00",
            "has_attachments": False
        }
    ]
    
    # Initialize the email triage crew
    triage_crew = InsuranceEmailTriageCrew()
    
    # Process the batch of emails
    print("Processing email batch...")
    results = triage_crew.batch_process_emails(sample_emails)
    
    # Display summary results
    print("\n===== Batch Processing Results =====")
    for i, result in enumerate(results):
        print(f"\nEmail {i+1} - {result['email_metadata']['subject']}")
        print(f"Type: {result['classification']['email_type']}")
        print(f"Urgency: {result['classification']['urgency']}")
        print(f"Routing: {result['routing']['team']} (Priority: {result['routing']['priority']})")
    
    # Save detailed results to a file
    with open("batch_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nDetailed results saved to batch_results.json")

if __name__ == "__main__":
    main()