"""
Document Loader Service
Loads and processes HR policy PDF documents for RAG
"""
import os
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class HRDocumentLoader:
    """Loads and processes HR policy documents"""

    def __init__(self, policies_path: str):
        self.policies_path = policies_path
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def load_documents(self) -> List[Document]:
        """Load all documents from HR policies directory"""
        documents = []

        # Ensure directory exists
        os.makedirs(self.policies_path, exist_ok=True)

        # Load PDF documents
        for filename in os.listdir(self.policies_path):
            if filename.endswith(".pdf"):
                file_path = os.path.join(self.policies_path, filename)
                try:
                    loader = PyPDFLoader(file_path)
                    docs = loader.load()
                    for doc in docs:
                        doc.metadata["source"] = filename
                        doc.metadata["policy_type"] = self._classify_policy(filename)
                    documents.extend(docs)
                    print(f"✓ Loaded: {filename} ({len(docs)} pages)")
                except Exception as e:
                    print(f"✗ Error loading {filename}: {e}")

        # If no PDFs found, use sample policies
        if not documents:
            print("No PDF documents found. Loading sample HR policies...")
            documents = self._create_sample_policies()

        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)
        print(f"✓ Created {len(chunks)} document chunks")

        return chunks

    def _classify_policy(self, filename: str) -> str:
        """Classify policy type based on filename"""
        filename_lower = filename.lower()
        if "leave" in filename_lower or "pto" in filename_lower or "time-off" in filename_lower:
            return "leave_policy"
        elif "health" in filename_lower or "medical" in filename_lower or "insurance" in filename_lower:
            return "healthcare_benefits"
        elif "retire" in filename_lower or "401k" in filename_lower or "pension" in filename_lower:
            return "retirement_benefits"
        elif "payroll" in filename_lower or "salary" in filename_lower or "compensation" in filename_lower:
            return "payroll_policy"
        return "general_policy"

    def _create_sample_policies(self) -> List[Document]:
        """Create comprehensive sample HR policy documents"""
        policies = [
            # Leave Policy
            Document(
                page_content="""
COMPANY LEAVE POLICY
Effective Date: January 1, 2024
Last Updated: January 15, 2024

1. ANNUAL LEAVE (PAID TIME OFF)

1.1 Eligibility
All full-time employees are eligible for annual leave benefits starting from their first day of employment.

1.2 Accrual Rates
- Years 0-2: 15 days per year (1.25 days/month)
- Years 3-5: 20 days per year (1.67 days/month)  
- Years 6-10: 25 days per year (2.08 days/month)
- Years 10+: 30 days per year (2.5 days/month)

1.3 Carryover Policy
- Maximum of 5 unused days may be carried over to the next calendar year
- Carried over days must be used by March 31st
- Unused days beyond the carryover limit will be forfeited

1.4 Request Process
- Submit leave requests through the HR portal or AI Assistant
- Requests for 1-3 days: Submit at least 5 business days in advance
- Requests for 4+ days: Submit at least 2 weeks in advance
- Manager approval required within 48 hours

2. SICK LEAVE

2.1 Allocation
- All employees receive 10 days of paid sick leave per year
- Sick leave does not accrue; full allocation available January 1st
- Unused sick leave does not carry over

2.2 Documentation Requirements
- 1-2 days: Self-certification accepted
- 3+ consecutive days: Medical certificate required
- Submit documentation within 3 days of return to work

2.3 Eligible Use
- Personal illness or injury
- Medical appointments
- Care for immediate family members
- Mental health days (up to 3 per year)

3. PERSONAL LEAVE

3.1 Allocation
- 5 days of personal leave per year
- For personal matters that don't qualify as sick or annual leave

3.2 Examples of Use
- Family emergencies
- Moving house
- Legal appointments
- Religious observances
- Personal celebrations

4. PARENTAL LEAVE

4.1 Maternity Leave
- 16 weeks of paid maternity leave
- Additional 4 weeks unpaid leave available
- Must notify HR at least 30 days before expected leave date
- Flexible return-to-work options available

4.2 Paternity Leave
- 6 weeks of paid paternity leave
- Must be taken within 12 months of child's birth/adoption
- Can be taken in blocks (minimum 1 week)

4.3 Adoption Leave
- Same benefits as biological parents
- Leave begins from date of placement

5. BEREAVEMENT LEAVE

- Immediate family (spouse, children, parents): 5 days
- Extended family (siblings, grandparents): 3 days
- Close friends: 1 day (manager discretion)

6. JURY DUTY AND VOTING LEAVE

- Full pay maintained during jury duty
- Up to 2 hours paid leave for voting

7. LEAVE WITHOUT PAY

- Available after exhausting paid leave options
- Maximum 30 days per year
- Requires VP-level approval
- Benefits continue during approved LWOP
                """,
                metadata={"source": "leave_policy.pdf", "policy_type": "leave_policy"}
            ),

            # Healthcare Benefits
            Document(
                page_content="""
HEALTHCARE BENEFITS GUIDE
Effective Date: January 1, 2024

1. MEDICAL INSURANCE

1.1 Coverage Overview
- Provider: BlueCross BlueShield PPO
- Coverage begins on first day of employment
- Pre-existing conditions covered

1.2 Premium Contributions (Monthly)
- Employee Only: $150
- Employee + Spouse: $350
- Employee + Children: $300
- Family: $500

1.3 Plan Details
- Annual Deductible: $500 individual / $1,500 family
- Out-of-Pocket Maximum: $3,000 individual / $6,000 family
- Preventive Care: 100% covered (no deductible)
- Primary Care Visit: $25 copay
- Specialist Visit: $50 copay
- Emergency Room: $150 copay (waived if admitted)
- Prescription Drugs:
  * Generic: $10 copay
  * Preferred Brand: $35 copay
  * Non-Preferred Brand: $60 copay

1.4 In-Network vs Out-of-Network
- In-Network: 80% coverage after deductible
- Out-of-Network: 60% coverage after deductible

2. DENTAL INSURANCE

2.1 Provider: Delta Dental PPO Plus Premier

2.2 Coverage
- Preventive Care (cleanings, x-rays): 100% covered
- Basic Procedures (fillings, extractions): 80% covered
- Major Procedures (crowns, bridges): 50% covered
- Orthodontia (children under 19): 50% covered, $2,000 lifetime max

2.3 Annual Maximum
- $2,500 per person per year

3. VISION INSURANCE

3.1 Provider: VSP Choice

3.2 Benefits
- Annual Eye Exam: $10 copay
- Glasses:
  * Frames: $200 allowance every 24 months
  * Lenses: $25 copay
- Contact Lenses: $150 allowance per year
- LASIK: 15% discount at participating providers

4. HEALTH SAVINGS ACCOUNT (HSA)

4.1 Eligibility
- Must be enrolled in high-deductible health plan
- Company contributes $500/year (individual) or $1,000/year (family)
- Employee contributions are tax-deductible

5. FLEXIBLE SPENDING ACCOUNT (FSA)

5.1 Healthcare FSA
- Maximum contribution: $3,050 per year
- Use for medical, dental, vision expenses
- $610 carryover allowed

5.2 Dependent Care FSA
- Maximum contribution: $5,000 per year
- Use for daycare, after-school care, elder care

6. MENTAL HEALTH BENEFITS

6.1 Employee Assistance Program (EAP)
- 8 free counseling sessions per year
- 24/7 crisis hotline
- Financial and legal consultation services
- Work-life balance resources

6.2 Mental Health Coverage
- Therapy visits: $25 copay (in-network)
- Psychiatry: $50 copay
- Telehealth mental health available
- No prior authorization for first 6 visits

7. WELLNESS PROGRAM

7.1 Gym Membership Reimbursement
- Up to $75/month reimbursement
- Any accredited gym or fitness center

7.2 Wellness Incentives
- Annual health screening: $200 wellness credit
- Complete health assessment: $100 credit
- Smoking cessation program: $200 credit

7.3 On-site Wellness
- Weekly yoga classes
- Monthly health seminars
- Annual flu shots
- Ergonomic assessments
                """,
                metadata={"source": "healthcare_benefits.pdf", "policy_type": "healthcare_benefits"}
            ),

            # Retirement Benefits
            Document(
                page_content="""
RETIREMENT BENEFITS PLAN
Effective Date: January 1, 2024

1. 401(K) RETIREMENT PLAN

1.1 Eligibility
- Eligible after 30 days of employment
- Automatic enrollment at 3% (opt-out available)
- Immediate vesting of employee contributions

1.2 Company Match
- 100% match on first 4% of salary
- 50% match on next 2% of salary
- Maximum company match: 5% of salary

Example: If you contribute 6% of a $100,000 salary:
- Your contribution: $6,000
- Company match: $5,000 (4% x 100% + 2% x 50%)
- Total annual contribution: $11,000

1.3 Vesting Schedule for Company Match
- Year 1: 25% vested
- Year 2: 50% vested
- Year 3: 75% vested
- Year 4+: 100% vested

1.4 Contribution Limits (2024)
- Under 50: $23,000 per year
- Age 50+: $30,500 per year (includes $7,500 catch-up)

1.5 Roth 401(k) Option
- After-tax contributions available
- Same matching rules as traditional 401(k)
- Tax-free qualified withdrawals in retirement

2. INVESTMENT OPTIONS

2.1 Target Date Funds
- Automatically adjust allocation based on retirement date
- Low expense ratios (0.10% - 0.15%)
- Default option for auto-enrollment

2.2 Index Funds
- S&P 500 Index Fund (0.03% expense ratio)
- Total Bond Market Index (0.05% expense ratio)
- International Stock Index (0.07% expense ratio)
- Small Cap Index (0.05% expense ratio)

2.3 Self-Directed Brokerage
- Access to individual stocks and ETFs
- $500 minimum balance required
- $25 annual fee

3. PENSION PLAN (LEGACY EMPLOYEES)

3.1 Eligibility
- Employees hired before January 1, 2015
- Frozen to new participants

3.2 Benefit Formula
- 1.5% x Years of Service x Final Average Salary
- Final Average Salary = highest 5 consecutive years

4. EMPLOYEE STOCK PURCHASE PLAN (ESPP)

4.1 Eligibility
- All employees with 6+ months tenure

4.2 Plan Details
- Contribute 1-15% of salary
- 15% discount on stock price
- Purchase periods: June 30 and December 31

5. RETIREMENT PLANNING RESOURCES

5.1 Financial Advisor Access
- Quarterly one-on-one sessions (free)
- Retirement readiness reviews
- Social Security optimization guidance

5.2 Educational Resources
- Monthly retirement planning webinars
- Online planning tools and calculators
- Annual retirement planning workshops

5.3 Retirement Readiness Checkpoints
- Age 45: Comprehensive retirement review
- Age 55: Catch-up contribution counseling
- Age 60: Pre-retirement planning session
- Age 63: Medicare and Social Security workshop

6. RETIREE BENEFITS

6.1 Healthcare
- Retiree medical coverage available (age 55+ with 10 years service)
- Premium sharing based on years of service

6.2 Life Insurance
- $10,000 coverage continues in retirement
- Optional additional coverage available

7. REQUIRED MINIMUM DISTRIBUTIONS (RMDs)

- RMDs begin at age 73
- Company plan allows in-service withdrawals at 59½
- Hardship withdrawals available (restrictions apply)
                """,
                metadata={"source": "retirement_benefits.pdf", "policy_type": "retirement_benefits"}
            ),

            # Payroll Policy
            Document(
                page_content="""
PAYROLL AND COMPENSATION POLICY
Effective Date: January 1, 2024

1. PAY SCHEDULE

1.1 Pay Frequency
- All employees are paid bi-weekly (every two weeks)
- 26 pay periods per year
- Pay day: Every other Friday

1.2 Pay Stub Availability
- Electronic pay stubs available 2 days before pay day
- Access through HR portal or AI Assistant
- Paper stubs available upon request

2. DIRECT DEPOSIT

2.1 Enrollment
- Direct deposit is mandatory for all employees
- Up to 3 bank accounts allowed
- Changes take effect within 2 pay periods

3. DEDUCTIONS

3.1 Mandatory Deductions
- Federal Income Tax (based on W-4)
- State Income Tax
- Social Security (6.2% up to wage base)
- Medicare (1.45%, additional 0.9% over $200,000)

3.2 Voluntary Deductions
- Health Insurance Premiums
- Dental/Vision Insurance
- 401(k) Contributions
- HSA/FSA Contributions
- Life Insurance
- Charitable Contributions

4. OVERTIME

4.1 Non-Exempt Employees
- Time and a half (1.5x) for hours over 40/week
- Double time (2x) for holidays
- Must be pre-approved by manager

4.2 Exempt Employees
- Not eligible for overtime pay
- Compensatory time may be available

5. BONUSES

5.1 Annual Performance Bonus
- Paid in March for previous year
- Based on individual and company performance
- Target: 5-20% of base salary

5.2 Spot Bonuses
- Manager discretion up to $500
- VP approval for $501-$2,000
- HR approval required over $2,000

6. TAX INFORMATION

6.1 W-2 Forms
- Issued by January 31st
- Electronic delivery default
- Paper copy available upon request

6.2 W-4 Updates
- Update anytime through HR portal
- Changes effective next pay period

7. PAYCHECK INQUIRIES

7.1 Discrepancies
- Report within 30 days of pay date
- Contact HR or use AI Assistant
- Resolution within 5 business days

7.2 Corrections
- Overpayments: Repayment plan available
- Underpayments: Corrected in next pay period or special check
                """,
                metadata={"source": "payroll_policy.pdf", "policy_type": "payroll_policy"}
            ),
        ]

        return policies
