"""
Export API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import io

from ...db.database import get_db
from ...services.auth_service import AuthService
from ...services.export_service import ExportService
from ...core.security import oauth2_scheme

router = APIRouter(prefix="/export", tags=["Export"])


def get_current_user_id(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> str:
    """Dependency to get current user ID."""
    auth_service = AuthService(db)
    user = auth_service.get_current_user(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return user.id


@router.get("/csv")
def export_csv(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Export all workout data as CSV.
    
    **Query parameters:**
    - start_date: Optional start date filter
    - end_date: Optional end date filter
    
    Returns a downloadable CSV file containing:
    - All workout records
    - Computed metrics for each workout
    """
    export_service = ExportService(db)
    
    csv_content = export_service.export_csv(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Generate filename with date
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    filename = f"crossfit_export_{date_str}.csv"
    
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/json")
def export_json(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    include_distributions: bool = False,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Export all workout data as JSON.
    
    **Query parameters:**
    - start_date: Optional start date filter
    - end_date: Optional end date filter
    - include_distributions: Include raw distribution data
    
    Returns a downloadable JSON file containing:
    - All workout records with movements and splits
    - Computed metrics for each workout
    - Domain scores
    - Optionally, raw distribution data
    """
    export_service = ExportService(db)
    
    export_data = export_service.export_json(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        include_distributions=include_distributions
    )
    
    # Return JSON with download headers
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    filename = f"crossfit_export_{date_str}.json"
    
    return JSONResponse(
        content=export_data,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
