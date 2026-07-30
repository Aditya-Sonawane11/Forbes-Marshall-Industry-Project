from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any
from data.database import Database

app = FastAPI(title="PCB Testing System API", description="API for PCB Testing Automation System")

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB instance
def get_db():
    try:
        db = Database()
        yield db
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

# --- Models ---
class LoginRequest(BaseModel):
    username: str
    password: str

class TestCaseCreate(BaseModel):
    name: str
    description: str
    min_voltage: float
    max_voltage: float
    current_limit: float
    timeout: float
    min_temp: float
    max_temp: float
    created_by: int

# --- Routes ---

@app.get("/")
def read_root():
    return {"status": "ok", "message": "PCB Testing System API is running"}

@app.post("/api/auth/login")
def login(req: LoginRequest, db: Database = Depends(get_db)):
    user_data = db.authenticate_user(req.username, req.password)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # In a real app, generate a JWT token here.
    return {
        "message": "Login successful",
        "user": {
            "id": user_data.get("id"),
            "username": user_data.get("username"),
            "role": user_data.get("role")
        }
    }

@app.get("/api/test-cases")
def get_test_cases(db: Database = Depends(get_db)):
    cases = db.get_test_cases()
    return {"test_cases": cases}

@app.post("/api/test-cases")
def create_test_case(case: TestCaseCreate, db: Database = Depends(get_db)):
    result = db.save_test_case(
        case.name, case.description, case.min_voltage, case.max_voltage,
        case.current_limit, case.timeout, case.min_temp, case.max_temp, case.created_by
    )
    if result:
        return {"message": "Test case created successfully"}
    raise HTTPException(status_code=500, detail="Failed to create test case")

@app.get("/api/test-cases/{case_id}")
def get_test_case(case_id: int, db: Database = Depends(get_db)):
    case = db.get_test_case_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Test case not found")
    return case

@app.get("/api/test-cases/{case_id}/stages")
def get_test_stages(case_id: int, db: Database = Depends(get_db)):
    stages = db.get_test_stages(case_id)
    return {"stages": stages}

@app.get("/api/results")
def get_results(db: Database = Depends(get_db)):
    results = db.get_test_results()
    return {"results": results}

@app.get("/api/diagrams")
def get_diagrams(db: Database = Depends(get_db)):
    diagrams = db.get_jig_diagrams()
    return {"diagrams": diagrams}

@app.get("/api/config")
def get_config(db: Database = Depends(get_db)):
    configs = db.get_all_comm_configs()
    return {"configs": configs}

@app.get("/api/stats/{case_id}")
def get_stats(case_id: int, db: Database = Depends(get_db)):
    stats = db.get_test_statistics(case_id)
    return {"statistics": stats}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
