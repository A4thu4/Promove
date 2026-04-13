from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

try:
    from app.schemas.evolution import EvolutionInput, EvolutionOutput
    from app.services.calculator import run_calculation
    from app.api.auth import get_current_user
    from app.models.user import User
    from app.models.history import History
    from app.db.session import get_db
except ImportError:
    from backend.app.schemas.evolution import EvolutionInput, EvolutionOutput
    from backend.app.services.calculator import run_calculation
    from backend.app.api.auth import get_current_user
    from backend.app.models.user import User
    from backend.app.models.history import History
    from backend.app.db.session import get_db

router = APIRouter()

@router.post("/calculate", response_model=EvolutionOutput)
async def calculate_evolution(input_data: EvolutionInput):
    return run_calculation(input_data)

@router.post("/calculate-save", response_model=EvolutionOutput)
async def calculate_and_save(
    input_data: EvolutionInput, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    result = run_calculation(input_data)
    
    # Save to history
    input_dict = input_data.model_dump(mode="json")
    result_dict = result.model_dump(mode="json")
    
    db_history = History(
        user_id=current_user.id,
        input_data=input_dict,
        result_data=result_dict
    )
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    
    return result

@router.get("/history")
async def get_user_history(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return db.query(History).filter(History.user_id == current_user.id).all()
