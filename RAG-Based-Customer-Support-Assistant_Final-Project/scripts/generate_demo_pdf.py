from fpdf import FPDF
import os

class DemoPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'iSupport assistant - Knowledge Base', 0, 1, 'C')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, title, 0, 1, 'L', True)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 10, body)
        self.ln()

def generate_kb():
    pdf = DemoPDF()
    pdf.add_page()

    # Section 1: General Info
    pdf.chapter_title('1. General Company Information')
    pdf.chapter_body(
        'iSupport assistant Corp is a global leader in AI-driven customer support automation. '
        'Founded in 2022, we have quickly become the primary choice for enterprises looking to scale their support operations. '
        'Our headquarters are located at 123 Tech Drive, Silicon Valley, CA. '
        'We operate 24 hours a day, 7 days a week, ensuring that our customers always have access to top-tier assistance. '
        'Our core values include Innovation, Integrity, and Customer Obsession. '
        'We believe that AI should empower humans, not replace them. '
        'By automating routine queries, we free up human agents to focus on complex, emotionally sensitive issues.'
    )

    # Section 2: Return Policy
    pdf.chapter_title('2. Return and Refund Policy')
    pdf.chapter_body(
        'Customers can request a return within 30 days of the purchase date. '
        'To be eligible, items must be in their original packaging and unused. '
        'Refunds are processed within 5-7 business days after the item is received at our warehouse. '
        'Please note that software licenses and digital products are non-refundable once activated. '
        'Shipping costs for returns are the responsibility of the customer unless the product arrived damaged. '
        'For international returns, please contact our logistics team for specific customs instructions. '
        'If a refund is rejected, a store credit may be offered as a gesture of goodwill.'
    )

    # Section 3: Technical Support
    pdf.chapter_title('3. Technical Troubleshooting')
    pdf.chapter_body(
        'If you encounter a "Connection Error", please check your internet settings first. '
        'Restarting the application solves 90% of common issues. '
        'For hardware failures, please contact our maintenance team at tech-support@isupport.com. '
        'Always include your serial number in the subject line for faster processing. '
        'We recommend keeping your software updated to the latest version to ensure compatibility. '
        'If you are using our API, please refer to the developer portal for rate limit information. '
        'Unauthorized tampering with internal hardware components will void your warranty.'
    )
    
    pdf.add_page()
    # Section 4: Privacy and Security
    pdf.chapter_title('4. Privacy and Data Security')
    pdf.chapter_body(
        'We take data privacy very seriously. All customer interactions are encrypted end-to-end. '
        'We are GDPR and CCPA compliant. Customers have the right to request their data at any time. '
        'We do not sell personal information to third parties. '
        'Our security team performs regular penetration tests to ensure our systems are resilient against cyber threats. '
        'If you suspect a data breach, please report it immediately to security@isupport.com.'
    )

    # Section 5: Billing and Subscriptions
    pdf.chapter_title('5. Billing and Subscriptions')
    pdf.chapter_body(
        'Subscription fees are charged at the beginning of each billing cycle. '
        'We offer Monthly and Annual plans. Annual plans come with a 20% discount. '
        'Failed payments will be retried 3 times over a 15-day period before service suspension. '
        'You can update your payment method in the "Billing" section of your account dashboard. '
        'Taxes are calculated based on your billing address and will be displayed on your invoice.'
    )

    pdf.add_page()
    # Section 6: Employee Conduct
    pdf.chapter_title('6. Employee Conduct and Values')
    pdf.chapter_body(
        'Employees are expected to maintain professional standards at all times. '
        'We foster an inclusive environment where diversity is celebrated. '
        'Harassment of any kind is strictly prohibited and will result in disciplinary action. '
        'Employees should use company resources responsibly and only for business purposes. '
        'Transparency is key to our culture; we encourage open feedback across all levels of the organization.'
    )

    # Section 7: Future Roadmap
    pdf.chapter_title('7. 2026 Product Roadmap')
    pdf.chapter_body(
        'In 2026, we plan to launch our multi-modal support engine, capable of processing video and audio. '
        'We are also expanding our presence in the APAC and EMEA regions with new data centers. '
        'Integration with major CRM platforms like Salesforce and Zendesk will be enhanced with one-click setups. '
        'Our goal is to reach 99.99% availability for all cloud services.'
    )
    
    pdf.add_page()
    # Section 8: Legal Terms
    pdf.chapter_title('8. Terms of Service')
    pdf.chapter_body(
        'By using our services, you agree to abide by these terms. '
        'We reserve the right to modify these terms at any time with 30 days notice. '
        'Our liability is limited to the amount paid for the service in the previous 12 months. '
        'Governing law for all disputes is the state of California, USA. '
        'If any provision is found to be unenforceable, the remaining provisions will remain in effect.'
    )

    os.makedirs('data', exist_ok=True)
    output_path = 'data/iSupport_Guide.pdf'
    pdf.output(output_path)
    print(f"Demo PDF generated at: {output_path}")

if __name__ == '__main__':
    generate_kb()
