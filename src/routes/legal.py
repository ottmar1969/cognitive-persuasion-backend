from flask import Blueprint, jsonify

legal_bp = Blueprint('legal', __name__)

@legal_bp.route('/terms')
def terms_of_service():
    """Get Terms of Service content"""
    return jsonify({
        "title": "Terms of Service",
        "slug": "terms",
        "content": """
# Terms of Service

## 1. Acceptance of Terms
By accessing and using the Cognitive Persuasion Engine service, you accept and agree to be bound by the terms and provision of this agreement.

## 2. Service Description
The Cognitive Persuasion Engine is an AI-powered business communication platform that helps businesses create targeted messaging for different audiences.

## 3. Use License
Permission is granted to temporarily use the service for personal, non-commercial transitory viewing only. This is the grant of a license, not a transfer of title.

## 4. Disclaimer
The materials on the Cognitive Persuasion Engine are provided on an 'as is' basis. We make no warranties, expressed or implied, and hereby disclaim and negate all other warranties including without limitation, implied warranties or conditions of merchantability, fitness for a particular purpose, or non-infringement of intellectual property or other violation of rights.

## 5. Limitations
In no event shall VisitorIntel or its suppliers be liable for any damages (including, without limitation, damages for loss of data or profit, or due to business interruption) arising out of the use or inability to use the materials on the service, even if VisitorIntel or an authorized representative has been notified orally or in writing of the possibility of such damage.

## 6. Contact Information
For questions about these Terms of Service, please contact:
- Name: O. Francisca
- Company: VisitorIntel
- WhatsApp: +31628073996

## 7. Governing Law
These terms and conditions are governed by and construed in accordance with the laws of the Netherlands.

Last updated: June 30, 2025
        """,
        "last_updated": "2025-06-30"
    })

@legal_bp.route('/privacy')
def privacy_policy():
    """Get Privacy Policy content"""
    return jsonify({
        "title": "Privacy Policy",
        "slug": "privacy",
        "content": """
# Privacy Policy

## 1. Information We Collect
We collect information you provide directly to us, such as when you create an account, use our services, or contact us for support.

### Types of Information:
- Business information and descriptions
- Target audience data
- Usage analytics and session data
- IP addresses and browser fingerprints for security purposes

## 2. How We Use Your Information
We use the information we collect to:
- Provide, maintain, and improve our services
- Process transactions and send related information
- Send technical notices and support messages
- Respond to your comments and questions

## 3. Information Sharing
We do not sell, trade, or otherwise transfer your personal information to third parties without your consent, except as described in this policy.

## 4. Data Security
We implement appropriate security measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction.

## 5. Your Rights
You have the right to:
- Access your personal data
- Correct inaccurate data
- Delete your data
- Object to processing
- Data portability

## 6. Cookies and Tracking
We use cookies and similar tracking technologies to track activity on our service and hold certain information for security and functionality purposes.

## 7. Contact Us
If you have any questions about this Privacy Policy, please contact us:
- Name: O. Francisca
- Company: VisitorIntel
- WhatsApp: +31628073996

Last updated: June 30, 2025
        """,
        "last_updated": "2025-06-30"
    })

@legal_bp.route('/gdpr')
def gdpr_compliance():
    """Get GDPR Compliance information"""
    return jsonify({
        "title": "GDPR Compliance",
        "slug": "gdpr",
        "content": """
# GDPR Compliance

## 1. Legal Basis for Processing
We process personal data under the following legal bases:
- Consent: When you explicitly agree to our processing
- Legitimate Interest: For security, fraud prevention, and service improvement
- Contract: To provide the services you've requested

## 2. Data Subject Rights
Under GDPR, you have the following rights:

### Right to Information
You have the right to know what personal data we collect and how we use it.

### Right of Access
You can request a copy of your personal data we hold.

### Right to Rectification
You can request correction of inaccurate or incomplete data.

### Right to Erasure
You can request deletion of your personal data under certain circumstances.

### Right to Restrict Processing
You can request limitation of processing under certain conditions.

### Right to Data Portability
You can request your data in a structured, machine-readable format.

### Right to Object
You can object to processing based on legitimate interests.

## 3. Data Protection Officer
For GDPR-related inquiries, contact:
- Name: O. Francisca
- Company: VisitorIntel
- WhatsApp: +31628073996

## 4. Data Retention
We retain personal data only as long as necessary for the purposes outlined in our Privacy Policy.

## 5. International Transfers
Any international data transfers are conducted with appropriate safeguards in place.

## 6. Complaints
You have the right to lodge a complaint with your local data protection authority.

Last updated: June 30, 2025
        """,
        "last_updated": "2025-06-30"
    })

@legal_bp.route('/cookies')
def cookie_policy():
    """Get Cookie Policy content"""
    return jsonify({
        "title": "Cookie Policy",
        "slug": "cookies",
        "content": """
# Cookie Policy

## 1. What Are Cookies
Cookies are small text files that are placed on your computer or mobile device when you visit our website. They are widely used to make websites work more efficiently and provide information to website owners.

## 2. How We Use Cookies
We use cookies for the following purposes:

### Essential Cookies
These cookies are necessary for the website to function properly:
- Session management
- Security features
- Basic functionality

### Analytics Cookies
These help us understand how visitors interact with our website:
- Page views and user behavior
- Performance monitoring
- Error tracking

### Security Cookies
These help us maintain security:
- Fraud prevention
- User authentication
- IP and fingerprint tracking

## 3. Types of Cookies We Use

### Session Cookies
Temporary cookies that expire when you close your browser.

### Persistent Cookies
Cookies that remain on your device for a set period or until you delete them.

### First-Party Cookies
Cookies set by our website directly.

### Third-Party Cookies
Cookies set by external services we use (if any).

## 4. Managing Cookies
You can control cookies through your browser settings:
- Block all cookies
- Block third-party cookies
- Delete existing cookies
- Receive notifications when cookies are set

## 5. Cookie Consent
By using our website, you consent to our use of cookies as described in this policy.

## 6. Contact Us
For questions about our cookie policy:
- Name: O. Francisca
- Company: VisitorIntel
- WhatsApp: +31628073996

Last updated: June 30, 2025
        """,
        "last_updated": "2025-06-30"
    })

@legal_bp.route('/legal')
def legal_information():
    """Get Legal Information content"""
    return jsonify({
        "title": "Legal Information",
        "slug": "legal",
        "content": """
# Legal Information

## 1. Company Information
- Company: VisitorIntel
- Contact Person: O. Francisca
- WhatsApp: +31628073996

## 2. Service Description
The Cognitive Persuasion Engine is a software-as-a-service platform that provides AI-powered business communication tools.

## 3. Intellectual Property
All content, features, and functionality of the service are owned by VisitorIntel and are protected by international copyright, trademark, and other intellectual property laws.

## 4. Liability Limitations
Our liability is limited to the maximum extent permitted by applicable law. We are not liable for any indirect, incidental, special, or consequential damages.

## 5. Indemnification
You agree to indemnify and hold harmless VisitorIntel from any claims, damages, or expenses arising from your use of the service.

## 6. Termination
We may terminate or suspend your access to the service at any time, with or without cause, with or without notice.

## 7. Governing Law
These terms are governed by the laws of the Netherlands, without regard to conflict of law principles.

## 8. Dispute Resolution
Any disputes arising from the use of this service will be resolved through binding arbitration in the Netherlands.

## 9. Severability
If any provision of these terms is found to be unenforceable, the remaining provisions will remain in full force and effect.

## 10. Contact Information
For legal inquiries:
- Name: O. Francisca
- Company: VisitorIntel
- WhatsApp: +31628073996

Last updated: June 30, 2025
        """,
        "last_updated": "2025-06-30"
    })

@legal_bp.route('')
def legal_index():
    """Get list of all legal pages"""
    return jsonify({
        "legal_pages": [
            {
                "title": "Terms of Service",
                "slug": "terms",
                "description": "Terms and conditions for using our service"
            },
            {
                "title": "Privacy Policy", 
                "slug": "privacy",
                "description": "How we collect, use, and protect your data"
            },
            {
                "title": "GDPR Compliance",
                "slug": "gdpr", 
                "description": "Your rights under GDPR and our compliance measures"
            },
            {
                "title": "Cookie Policy",
                "slug": "cookies",
                "description": "How we use cookies and tracking technologies"
            },
            {
                "title": "Legal Information",
                "slug": "legal",
                "description": "Company information and legal notices"
            }
        ],
        "contact": {
            "name": "O. Francisca",
            "company": "VisitorIntel", 
            "whatsapp": "+31628073996"
        }
    })

