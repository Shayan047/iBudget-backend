from fastapi import FastAPI
from app.modules.user.api import router as user_router
from app.modules.expense.api import router as expense_router
from app.modules.category.api import router as category_router
from app.modules.income.api import router as income_router
from app.modules.budget.api import router as budget_router
from app.modules.auth.api import router as auth_router
from app.modules.dashboard.api import router as dashboard_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="iBudget APIs",
    description="APIs for iBudget application",
    version="1.0.0",
    docs_url="/api",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(expense_router)
app.include_router(category_router)
app.include_router(income_router)
app.include_router(budget_router)
app.include_router(dashboard_router)

@app.get("/")
def read_root():
    return {"message": "FastAPI with PostgreSQL + Docker is working!"}