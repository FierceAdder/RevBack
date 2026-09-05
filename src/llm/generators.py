"""Communication Message Generation Engine.

Generates channel-specific, tone-adjusted recovery communications
(WhatsApp, Email, SMS, Formal Demand Notice) with Razorpay payment links.
"""

from typing import Optional
from src.models.db_models import CommunicationChannel, ToneType


class MessageGenerator:
    """Generates personalized recovery communications across channels and tones."""

    @classmethod
    def generate_message(
        cls,
        channel: CommunicationChannel,
        tone: ToneType,
        customer_name: str,
        invoice_number: str,
        amount_paise: int,
        days_overdue: int,
        payment_link_url: str,
        due_date_str: str,
        merchant_name: str = "RevBack Technologies",
    ) -> tuple[str, Optional[str]]:
        """
        Returns:
            (content, subject)
        """
        amount_inr = f"₹{amount_paise / 100:,.2f}"

        if channel == CommunicationChannel.WHATSAPP:
            subject = None
            if tone == ToneType.COLLABORATIVE:
                content = (
                    f"Hi {customer_name}! 👋 Gentle courtesy note regarding invoice #{invoice_number} "
                    f"for {amount_inr} with {merchant_name}. To settle easily via UPI, Card, or NetBanking, "
                    f"you can use this secure Razorpay link: {payment_link_url}\n\n"
                    f"Please let us know if you need any assistance with reconciliation!"
                )
            elif tone == ToneType.PROFESSIONAL:
                content = (
                    f"Hello {customer_name}, this is a reminder that invoice #{invoice_number} ({amount_inr}) "
                    f"was due on {due_date_str} ({days_overdue} days ago). Please complete your payment securely "
                    f"via Razorpay here: {payment_link_url}\n\nThank you for your prompt attention."
                )
            elif tone == ToneType.FIRM:
                content = (
                    f"Attention: {customer_name}. Invoice #{invoice_number} ({amount_inr}) is now {days_overdue} days overdue. "
                    f"To prevent account suspension, please settle immediately using your dedicated Razorpay link: {payment_link_url}"
                )
            else:
                content = (
                    f"URGENT: {customer_name}. Payment of {amount_inr} for #{invoice_number} is critically overdue ({days_overdue} days). "
                    f"Final settlement link: {payment_link_url}. Continued delay will initiate formal recovery proceedings."
                )

        elif channel == CommunicationChannel.SMS:
            subject = None
            content = (
                f"{merchant_name}: Inv #{invoice_number} for {amount_inr} is {days_overdue}d overdue. "
                f"Pay securely now via Razorpay: {payment_link_url}"
            )

        elif channel == CommunicationChannel.FORMAL_NOTICE:
            subject = f"FORMAL DEMAND NOTICE: Final Call for Remittance of Outstanding Dues — Inv #{invoice_number}"
            content = (
                f"WITHOUT PREJUDICE\n\n"
                f"To: The Finance Director / Authorized Signatory\n"
                f"{customer_name}\n\n"
                f"RE: FORMAL DEMAND FOR SETTLEMENT OF INVOICE #{invoice_number}\n\n"
                f"Sir/Madam,\n\n"
                f"We write on behalf of {merchant_name}. Despite repeated reminders, the amount of {amount_inr} "
                f"in respect of invoice #{invoice_number} (originally due on {due_date_str}, now {days_overdue} days overdue) "
                f"remains completely unpaid.\n\n"
                f"TAKE NOTICE that you are hereby called upon to pay the entire outstanding sum of {amount_inr} "
                f"within seven (7) days of receipt of this notice through the verified Razorpay payment channel below:\n\n"
                f"Instant Settlement Link: {payment_link_url}\n\n"
                f"PLEASE NOTE: In the event of default, our client shall have no recourse but to initiate legal proceedings "
                f"for commercial recovery under applicable laws, including claiming statutory interest and legal fees.\n\n"
                f"Yours faithfully,\n"
                f"Legal & Recovery Compliance Team\n{merchant_name}"
            )

        else:  # EMAIL
            subject = f"Follow-up: Invoice #{invoice_number} for {amount_inr} — {merchant_name}"
            if tone == ToneType.COLLABORATIVE:
                content = (
                    f"Dear {customer_name},\n\n"
                    f"We hope you are having a productive week.\n\n"
                    f"This is a quick courtesy note regarding invoice #{invoice_number} for {amount_inr}, which was due on {due_date_str}.\n\n"
                    f"For your convenience, you can review the invoice and complete settlement instantly via our secure Razorpay gateway:\n"
                    f"{payment_link_url}\n\n"
                    f"If the payment is already in transit or if you have any questions, please feel free to reply to this email.\n\n"
                    f"Warm regards,\nFinance Team, {merchant_name}"
                )
            elif tone == ToneType.PROFESSIONAL:
                content = (
                    f"Dear {customer_name},\n\n"
                    f"We are writing to follow up on the outstanding balance for invoice #{invoice_number}.\n\n"
                    f"• Invoice Number: #{invoice_number}\n"
                    f"• Amount Due: {amount_inr}\n"
                    f"• Due Date: {due_date_str} ({days_overdue} days overdue)\n\n"
                    f"Please settle this invoice at your earliest convenience using the secure Razorpay payment link below:\n"
                    f"{payment_link_url}\n\n"
                    f"Thank you for your ongoing partnership.\n\n"
                    f"Sincerely,\nAccounts Receivable, {merchant_name}"
                )
            elif tone == ToneType.FIRM:
                content = (
                    f"Dear {customer_name},\n\n"
                    f"According to our records, invoice #{invoice_number} in the amount of {amount_inr} is now {days_overdue} days overdue.\n\n"
                    f"Timely receipt of payments is essential to ensure uninterrupted services on your account. Please remit payment "
                    f"immediately via this secure link:\n{payment_link_url}\n\n"
                    f"If you are experiencing temporary cash flow constraints, please reply immediately so we can evaluate a structured payment plan.\n\n"
                    f"Regards,\nCredit Control Department, {merchant_name}"
                )
            else:  # URGENT
                content = (
                    f"URGENT: OVERDUE NOTICE — Invoice #{invoice_number}\n\n"
                    f"Dear {customer_name},\n\n"
                    f"This is an urgent notice regarding invoice #{invoice_number} for {amount_inr}, now {days_overdue} days overdue.\n\n"
                    f"Continued non-payment poses immediate risk of account suspension and referral to our legal recovery partners. "
                    f"To prevent further escalation, you must complete settlement today using the link below:\n\n"
                    f"Payment Link: {payment_link_url}\n\n"
                    f"Immediate action is required.\n\n"
                    f"Senior Collections Manager, {merchant_name}"
                )

        return content, subject

    @classmethod
    def generate_payment_plan_offer(
        cls,
        channel: CommunicationChannel,
        customer_name: str,
        invoice_number: str,
        total_amount_paise: int,
        installments: list,
        merchant_name: str = "RevBack Technologies",
    ) -> tuple[str, Optional[str]]:
        """Generates communication offering a structured installment plan with per-installment Razorpay links."""
        total_inr = f"₹{total_amount_paise / 100:,.2f}"
        inst_summary_lines = []
        for inst in installments:
            due_str = inst.get("due_date_iso", "")[:10] if isinstance(inst.get("due_date_iso"), str) else str(inst.get("due_date", ""))[:10]
            link_str = f" [Pay: {inst['payment_link_url']}]" if inst.get("payment_link_url") else ""
            inst_summary_lines.append(
                f"  • Installment {inst['installment_number']}: ₹{inst['amount_paise']/100:,.2f} due on {due_str}{link_str}"
            )
        inst_summary = "\n".join(inst_summary_lines)

        first_link = installments[0].get("payment_link_url", "")

        if channel in (CommunicationChannel.WHATSAPP, CommunicationChannel.SMS):
            subject = None
            content = (
                f"Hello {customer_name}! In response to your payment plan request for invoice #{invoice_number} ({total_inr}), "
                f"we have approved a {len(installments)}-part structured installment schedule:\n\n"
                f"{inst_summary}\n\n"
                f"You can settle Installment 1 right away here: {first_link}\n"
                f"Thank you for working with us!"
            )
        else:
            subject = f"Structured Payment Plan Offer: Invoice #{invoice_number} — {merchant_name}"
            content = (
                f"Dear {customer_name},\n\n"
                f"Thank you for reaching out regarding your account. In light of your request for payment flexibility, "
                f"we are pleased to offer a structured {len(installments)}-part installment plan for invoice #{invoice_number} ({total_inr}):\n\n"
                f"Installment Schedule:\n"
                f"{inst_summary}\n\n"
                f"Please settle the first installment by the due date to activate this agreement. "
                f"Each installment includes an individual secure Razorpay payment link.\n\n"
                f"Warm regards,\nCredit Control Team, {merchant_name}"
            )

        return content, subject

