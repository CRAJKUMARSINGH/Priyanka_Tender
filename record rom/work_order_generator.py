from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging
from date_utils import DateUtils

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WorkOrderGenerator:
    """Generates official PWD format Work Order with enhanced date handling."""
    
    def __init__(self):
        self.date_utils = DateUtils()
        self.portrait_style = """
        <style>
            @page { 
                size: A4 portrait; 
                margin: 20mm; 
            }
            body {
                font-family: 'Arial', Arial, sans-serif;
                font-size: 11px;
                line-height: 1.4;
                margin: 0;
                padding: 0;
                color: black;
            }
            .header {
                text-align: center;
                font-weight: bold;
                font-size: 12px;
                margin-bottom: 20px;
            }
            .office-header {
                text-align: center;
                font-weight: bold;
                font-size: 12px;
                margin-bottom: 10px;
                border-bottom: 1px solid black;
                padding-bottom: 5px;
            }
            .office-text {
                text-align: center;
                font-weight: bold;
                font-size: 12px;
                margin: 0;
            }
            .work-order-content {
                text-align: justify;
                margin: 20px 0;
                line-height: 1.6;
            }
            .work-order-heading {
                text-align: center;
                font-weight: bold;
                margin: 20px 0;
            }
            .work-order-first-line {
                text-align: center;
                font-weight: bold;
                margin: 15px 0;
            }
            .work-order-ref {
                margin: 15px 0;
            }
            .signature-section {
                margin-top: 40px;
                text-align: right;
            }
            .address-section {
                margin: 20px 0;
            }
            .terms-table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            .terms-table td, .terms-table th {
                border: 1px solid black;
                padding: 8px;
                font-size: 10px;
                vertical-align: top;
            }
            .terms-table th {
                background-color: #f0f0f0;
                font-weight: bold;
                text-align: center;
            }
        </style>
        """
    
    def generate_work_order(self, work: Dict[str, Any], bidders: List[Dict[str, Any]]) -> str:
        """Generate official PWD Work Order format with enhanced date handling."""
        
        try:
            # Sort bidders by bid amount (lowest first)
            sorted_bidders = sorted(bidders, key=lambda x: x['bid_amount'])
            lowest_bidder = sorted_bidders[0]
            
            # Get work details
            work_name = work['work_name']
            nit_number = work['nit_number']
            work_info = work['work_info']
            estimated_cost = float(work_info['estimated_cost'])
            earnest_money = work_info['earnest_money']
            time_completion = work_info['time_of_completion']
            
            # Enhanced date parsing and handling
            original_date = work_info['date']
            parsed_date = self.date_utils.parse_date(original_date)
            
            if not parsed_date:
                logging.warning(f"Could not parse date '{original_date}', using current date")
                parsed_date = datetime.now()
            
            # Format date for display
            formatted_date = self.date_utils.format_display_date(parsed_date)
            
            # Calculate project timeline using DateUtils - stipulated start date is current processing date + 1
            current_processing_date = datetime.now()
            stipulated_start_date = self.date_utils.add_days(current_processing_date, 1)
            stipulated_start_formatted = self.date_utils.format_display_date(stipulated_start_date)
            
            try:
                timeline = self._calculate_project_timeline(current_processing_date, time_completion)
                # Override with stipulated start date
                timeline['commencement_date'] = stipulated_start_formatted
            except Exception as e:
                logging.error(f"Error calculating timeline: {e}")
                # Use fallback timeline with current processing date + 1
                timeline = {
                    'commencement_date': stipulated_start_formatted,
                    'completion_date': self.date_utils.format_display_date(self.date_utils.add_months(current_processing_date, 3))
                }
            
            # Format amount in words
            amount_words = self._amount_to_words(lowest_bidder['bid_amount'])
            
            # Calculate performance security (3% of contract value)
            performance_security = int(lowest_bidder['bid_amount'] * 0.03)
            
            # Generate current timestamp
            current_timestamp = self.date_utils.get_current_date()
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Work Order - {nit_number}</title>
                {self.portrait_style}
            </head>
            <body>
                <div class="office-header">
                    <div class="office-text">OFFICE OF THE EXECUTIVE ENGINEER PWD ELECTRIC DIVISION UDAIPUR</div>
                </div>
                
                <div class="work-order-ref">
                    No.- {nit_number}/WO/{datetime.now().year}<br>
                    Date- {formatted_date}<br>
                </div>
                
                <div class="work-order-content">
                    <div class="work-order-heading" style="text-align: center; font-weight: bold; font-size: 14px;">WRITTEN ORDER TO COMMENCE WORK</div>
                    <div class="work-order-first-line">To,</div>
                    <br>
                    {lowest_bidder['name']}<br>
                    [Complete Address]<br><br>
                    
                    Name of Work: {work_name}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;NIT No.:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{nit_number}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ITEM-{work.get('item_number', '1')}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;NIT Date:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{formatted_date}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Tender Receipt Date:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{formatted_date}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Your Tender / Negotiations dated:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{formatted_date}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Contract Amount:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Rs. {lowest_bidder['bid_amount']:,.0f}/- (Rupees {amount_words} Only)<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Performance Security:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Rs. {performance_security:,.0f}/-<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Earnest Money:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Rs. {earnest_money}/-<br><br>
                    
                    Dear Sir,<br><br>
                    
                    With reference to your tender dated {formatted_date} for the above work, I am pleased to inform you that your tender has been accepted by the competent authority for an amount of Rs. {lowest_bidder['bid_amount']:,.0f}/- ({lowest_bidder['percentage']:+.2f}% {'below' if lowest_bidder['percentage'] < 0 else 'above'} the estimated cost).
                    <br><br>
                    
                    You are therefore, requested to please contact the Assistant Engineer-in-Charge and start the work. The time allowed for commencement of work shall be reckoned from 1st day after the receipt of this order. This tender document shall form part of the agreement and shall be treated as executed between you and the Governor of Rajasthan.
                    <br><br>
                    
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Agreement No.:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{nit_number}/AGR/{datetime.now().year}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Stipulated date for commencement of work:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{timeline['commencement_date']}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Stipulated date for completion of work:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{timeline['completion_date']}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Administrative Sanction:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;As per sanction order<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Technical Sanction:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;As per technical sanction<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Budget Provision:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Adequate<br><br>
                    
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Yours Faithfully,<br><br>
                    
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Executive Engineer<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;On behalf of the Governor of State of Rajasthan
                    <br><br>
                    
                    Copy to the following for information & necessary action:<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. The Accountant General Raj Jaipur<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. The Addl Chief Engineer PWD Zone Udaipur.<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3. The Addl Chief Engineer PWD Electrical Zone Udaipur.<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;4. The Superintending Engineer PWD Electric Circle Udaipur.<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;5. The Assistant Engineer PWD Electric Sub.Dn I/II Udaipur/Rajsamand for similar action.<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;6. The Junior Engineer PWD Electric Sub Dn I/II Udaipur/Rajsamand for similar action.<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;7. Agreement clerk with original tender for preparing agreement at the earliest.<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;8. Auditor<br><br>
                    
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Executive Engineer,<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;PWD ELECTRICAL DIVISION- UDAIPUR<br>
                </div>
                
                <div class="signature-section">
                    <strong>Executive Engineer</strong><br>
                    PWD Electric Division<br>
                    Udaipur
                </div>
                
                <div style="margin-top: 20px; font-size: 9px; text-align: center; color: #666;">
                    Work Order generated on {current_timestamp}
                </div>
            </body>
            </html>
            """
            
            return html_content
            
        except Exception as e:
            logging.error(f"Error generating work order: {e}")
            raise
    
    def _calculate_project_timeline(self, start_date: datetime, time_completion: str) -> Dict[str, str]:
        """
        Calculate project timeline dates using DateUtils.
        
        Args:
            start_date: Project start date
            time_completion: Time completion string (e.g., "3 Months")
            
        Returns:
            Dictionary with formatted timeline dates
        """
        try:
            # Commencement date is the next day after start date
            commencement_date = self.date_utils.add_days(start_date, 1)
            
            # Calculate completion date based on time_completion
            completion_date = self.date_utils.calculate_completion_date(commencement_date, time_completion)
            
            return {
                'commencement_date': self.date_utils.format_display_date(commencement_date),
                'completion_date': self.date_utils.format_display_date(completion_date)
            }
            
        except Exception as e:
            logging.error(f"Error in timeline calculation: {e}")
            raise
    
    def _amount_to_words(self, amount: float) -> str:
        """Convert amount to words in Indian format with error handling."""
        try:
            amount = int(amount)
            
            # Simple conversion for common amounts
            if amount < 100000:  # Less than 1 lakh
                thousands = amount // 1000
                hundreds = (amount % 1000) // 100
                remainder = amount % 100
                
                words = []
                if thousands > 0:
                    words.append(f"{thousands} Thousand")
                if hundreds > 0:
                    words.append(f"{hundreds} Hundred")
                if remainder > 0:
                    words.append(str(remainder))
                
                return " ".join(words) if words else "Zero"
            
            elif amount < 10000000:  # Less than 1 crore
                lakhs = amount // 100000
                remainder = amount % 100000
                
                words = [f"{lakhs} Lakh"]
                if remainder >= 1000:
                    thousands = remainder // 1000
                    words.append(f"{thousands} Thousand")
                    remainder = remainder % 1000
                if remainder > 0:
                    words.append(str(remainder))
                
                return " ".join(words)
            
            else:
                crores = amount // 10000000
                remainder = amount % 10000000
                
                words = [f"{crores} Crore"]
                if remainder >= 100000:
                    lakhs = remainder // 100000
                    words.append(f"{lakhs} Lakh")
                    remainder = remainder % 100000
                if remainder >= 1000:
                    thousands = remainder // 1000
                    words.append(f"{thousands} Thousand")
                    remainder = remainder % 1000
                if remainder > 0:
                    words.append(str(remainder))
                
                return " ".join(words)
                
        except Exception as e:
            logging.error(f"Error converting amount to words: {e}")
            return f"{amount:,.0f}"
