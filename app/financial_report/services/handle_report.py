from datetime import date, datetime
from app.financial_report.schemas.frontendDTOs import (
    FinancialReportQuery,
    FinancialReportResponse,
    RealPayoutRow,
    RealTable,
    ExpectedOrderRow,
    ExpectedTable
)
from app.financial_report.schemas.ozonDTOs import (
    OzonBuyoutItem,
    OzonBuyoutReportRequest,
    OzonBuyoutReportResponse
)
class ReportHandle:
    def __init__(self, repo):
        self.repo = repo


    
