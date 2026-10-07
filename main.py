from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

import models
import schemas
from database import DATABASE_URL, Base, engine, get_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    # This creates the workbook's three tables on first connection to Supabase.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Ledger API — FastAPI + Supabase",
    description="Cloud Computing Week 4: account, category, and transaction API.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", tags=["health"])
def root():
    return {"message": "Ledger API is running", "database": "postgresql" if DATABASE_URL.startswith("postgresql") else "sqlite"}


@app.get("/health", tags=["health"])
def health(db: Session = Depends(get_db)):
    db.execute(select(1))
    return {"status": "ok", "database": "postgresql" if DATABASE_URL.startswith("postgresql") else "sqlite"}


@app.post("/accounts", response_model=schemas.AccountRead, status_code=status.HTTP_201_CREATED, tags=["accounts"])
def create_account(payload: schemas.AccountCreate, db: Session = Depends(get_db)):
    account = models.Account(**payload.model_dump())
    db.add(account)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="이미 같은 이름의 계좌가 있습니다.")
    db.refresh(account)
    return account


@app.get("/accounts", response_model=list[schemas.AccountRead], tags=["accounts"])
def list_accounts(db: Session = Depends(get_db)):
    return db.scalars(select(models.Account).order_by(models.Account.id)).all()


@app.get("/accounts-with-tx", response_model=list[schemas.AccountReadWithTransactions], tags=["accounts"])
def accounts_with_transactions(db: Session = Depends(get_db)):
    stmt = select(models.Account).options(selectinload(models.Account.transactions)).order_by(models.Account.id)
    return db.scalars(stmt).all()


@app.get("/accounts/{account_id}", response_model=schemas.AccountRead, tags=["accounts"])
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = db.get(models.Account, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="해당 계좌가 없습니다.")
    return account


@app.post("/categories", response_model=schemas.CategoryRead, status_code=status.HTTP_201_CREATED, tags=["categories"])
def create_category(payload: schemas.CategoryCreate, db: Session = Depends(get_db)):
    category = models.Category(**payload.model_dump())
    db.add(category)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="이미 같은 이름의 카테고리가 있습니다.")
    db.refresh(category)
    return category


@app.get("/categories", response_model=list[schemas.CategoryRead], tags=["categories"])
def list_categories(db: Session = Depends(get_db)):
    return db.scalars(select(models.Category).order_by(models.Category.id)).all()


@app.post("/transactions", response_model=schemas.TransactionRead, status_code=status.HTTP_201_CREATED, tags=["transactions"])
def create_transaction(payload: schemas.TransactionCreate, db: Session = Depends(get_db)):
    if db.get(models.Account, payload.account_id) is None:
        raise HTTPException(status_code=404, detail="해당 계좌가 없습니다.")
    if payload.category_id is not None and db.get(models.Category, payload.category_id) is None:
        raise HTTPException(status_code=404, detail="해당 카테고리가 없습니다.")
    transaction = models.Transaction(**payload.model_dump())
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@app.get("/accounts/{account_id}/transactions", response_model=list[schemas.TransactionRead], tags=["transactions"])
def account_transactions(account_id: int, db: Session = Depends(get_db)):
    if db.get(models.Account, account_id) is None:
        raise HTTPException(status_code=404, detail="해당 계좌가 없습니다.")
    stmt = select(models.Transaction).where(models.Transaction.account_id == account_id).order_by(models.Transaction.occurred_at.desc())
    return db.scalars(stmt).all()


@app.get("/stats/by-category", response_model=list[schemas.CategoryStats], tags=["statistics"])
def by_category(db: Session = Depends(get_db)):
    stmt = (
        select(models.Category.name, func.sum(models.Transaction.amount), func.count(models.Transaction.id))
        .select_from(models.Transaction)
        .join(models.Category, models.Transaction.category_id == models.Category.id, isouter=True)
        .where(models.Transaction.amount < 0)
        .group_by(models.Category.name)
        .order_by(models.Category.name)
    )
    return [
        {"category": name, "total": total, "count": count}
        for name, total, count in db.execute(stmt).all()
    ]
