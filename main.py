from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import os
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

# Configuración de la base de datos
SQLALCHEMY_DATABASE_URL = "sqlite:///./voting_system.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Configuración JWT
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Modelos de Base de Datos
class Voter(Base):
    __tablename__ = "voters"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    has_voted = Column(Boolean, default=False)
    
    votes = relationship("Vote", back_populates="voter")

class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    party = Column(String, nullable=True)
    votes_count = Column(Integer, default=0)
    
    votes = relationship("Vote", back_populates="candidate")

class Vote(Base):
    __tablename__ = "votes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    voter_id = Column(Integer, ForeignKey("voters.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    
    voter = relationship("Voter", back_populates="votes")
    candidate = relationship("Candidate", back_populates="votes")

# Crear tablas
Base.metadata.create_all(bind=engine)

# Modelos Pydantic
class VoterBase(BaseModel):
    name: str
    email: EmailStr

class VoterCreate(VoterBase):
    pass

class VoterResponse(VoterBase):
    id: int
    has_voted: bool
    
    class Config:
        orm_mode = True

class CandidateBase(BaseModel):
    name: str
    party: Optional[str] = None

class CandidateCreate(CandidateBase):
    pass

class CandidateResponse(CandidateBase):
    id: int
    votes_count: int
    
    class Config:
        orm_mode = True

class VoteCreate(BaseModel):
    voter_id: int
    candidate_id: int

class VoteResponse(BaseModel):
    id: int
    voter_id: int
    candidate_id: int
    
    class Config:
        orm_mode = True

class VotingStats(BaseModel):
    total_votes_by_candidate: int
    vote_percentage_by_candidate: float
    total_voters_who_voted: int

class Token(BaseModel):
    access_token: str
    token_type: str

# Funciones de utilidad
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Inicializar FastAPI
app = FastAPI(
    title="Sistema de Votaciones",
    description="API RESTful para gestionar un sistema de votaciones",
    version="1.0.0"
)

# Endpoints para Votantes

@app.post("/voters", response_model=VoterResponse, summary="Registrar un nuevo votante")
def create_voter(voter: VoterCreate, db: Session = Depends(get_db)):
    """Registra un nuevo votante en el sistema."""
    # Verificar que el email no esté ya registrado
    db_voter = db.query(Voter).filter(Voter.email == voter.email).first()
    if db_voter:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    db_voter = Voter(name=voter.name, email=voter.email)
    db.add(db_voter)
    db.commit()
    db.refresh(db_voter)
    return db_voter

@app.get("/voters", response_model=List[VoterResponse], summary="Obtener lista de votantes")
def get_voters(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtiene la lista de todos los votantes registrados."""
    voters = db.query(Voter).offset(skip).limit(limit).all()
    return voters

@app.get("/voters/{voter_id}", response_model=VoterResponse, summary="Obtener detalles de un votante")
def get_voter(voter_id: int, db: Session = Depends(get_db)):
    """Obtiene los detalles de un votante específico por ID."""
    voter = db.query(Voter).filter(Voter.id == voter_id).first()
    if voter is None:
        raise HTTPException(status_code=404, detail="Votante no encontrado")
    return voter

@app.delete("/voters/{voter_id}", summary="Eliminar un votante")
def delete_voter(voter_id: int, db: Session = Depends(get_db)):
    """Elimina un votante del sistema."""
    voter = db.query(Voter).filter(Voter.id == voter_id).first()
    if voter is None:
        raise HTTPException(status_code=404, detail="Votante no encontrado")
    
    # Verificar que no haya votado
    if voter.has_voted:
        raise HTTPException(status_code=400, detail="No se puede eliminar un votante que ya ha votado")
    
    db.delete(voter)
    db.commit()
    return {"message": "Votante eliminado exitosamente"}

# Endpoints para Candidatos

@app.post("/candidates", response_model=CandidateResponse, summary="Registrar un nuevo candidato")
def create_candidate(candidate: CandidateCreate, db: Session = Depends(get_db)):
    """Registra un nuevo candidato en el sistema."""
    db_candidate = Candidate(name=candidate.name, party=candidate.party)
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate

@app.get("/candidates", response_model=List[CandidateResponse], summary="Obtener lista de candidatos")
def get_candidates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtiene la lista de todos los candidatos registrados."""
    candidates = db.query(Candidate).offset(skip).limit(limit).all()
    return candidates

@app.get("/candidates/{candidate_id}", response_model=CandidateResponse, summary="Obtener detalles de un candidato")
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Obtiene los detalles de un candidato específico por ID."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidato no encontrado")
    return candidate

@app.delete("/candidates/{candidate_id}", summary="Eliminar un candidato")
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Elimina un candidato del sistema."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidato no encontrado")
    
    db.delete(candidate)
    db.commit()
    return {"message": "Candidato eliminado exitosamente"}

# Endpoints para Votos

@app.post("/votes", response_model=VoteResponse, summary="Emitir un voto")
def create_vote(vote: VoteCreate, db: Session = Depends(get_db)):
    """Permite a un votante emitir su voto por un candidato."""
    # Validaciones
    
    # 1. Verificar que el votante existe
    voter = db.query(Voter).filter(Voter.id == vote.voter_id).first()
    if not voter:
        raise HTTPException(status_code=404, detail="Votante no encontrado")
    
    # 2. Verificar que el candidato existe
    candidate = db.query(Candidate).filter(Candidate.id == vote.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidato no encontrado")
    
    # 3. Verificar que el votante no sea candidato (Restricción del documento)
    voter_as_candidate = db.query(Candidate).filter(Candidate.name == voter.name).first()
    if voter_as_candidate:
        raise HTTPException(status_code=400, detail="Un votante no puede ser candidato y viceversa")
    
    # 4. Verificar que el votante no haya votado previamente
    if voter.has_voted:
        raise HTTPException(status_code=400, detail="El votante ya ha emitido su voto")
    
    # 5. Verificar integridad: actualizar automáticamente has_voted
    voter.has_voted = True
    
    # 6. Crear el voto
    db_vote = Vote(voter_id=vote.voter_id, candidate_id=vote.candidate_id)
    db.add(db_vote)
    
    # 7. Incrementar contador de votos del candidato seleccionado
    candidate.votes_count += 1
    
    db.commit()
    db.refresh(db_vote)
    
    return db_vote

@app.get("/votes", response_model=List[VoteResponse], summary="Obtener todos los votos emitidos")
def get_votes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtiene la lista de todos los votos emitidos."""
    votes = db.query(Vote).offset(skip).limit(limit).all()
    return votes

@app.get("/votes/statistics", summary="Obtener estadísticas de la votación")
def get_voting_statistics(db: Session = Depends(get_db)):
    """Obtiene estadísticas completas de la votación."""
    # Total de votantes que han votado
    total_voters_who_voted = db.query(Voter).filter(Voter.has_voted == True).count()
    
    # Estadísticas por candidato
    candidates_stats = []
    candidates = db.query(Candidate).all()
    
    for candidate in candidates:
        vote_percentage = (candidate.votes_count / total_voters_who_voted * 100) if total_voters_who_voted > 0 else 0
        candidates_stats.append({
            "candidate_id": candidate.id,
            "candidate_name": candidate.name,
            "party": candidate.party,
            "total_votes": candidate.votes_count,
            "vote_percentage": round(vote_percentage, 2)
        })
    
    return {
        "total_voters_who_voted": total_voters_who_voted,
        "candidates_statistics": candidates_stats
    }

# Endpoints adicionales para validaciones y extras

@app.get("/validations/voter-candidate-check/{voter_id}")
def check_voter_not_candidate(voter_id: int, db: Session = Depends(get_db)):
    """Verifica que un votante no sea candidato y viceversa."""
    voter = db.query(Voter).filter(Voter.id == voter_id).first()
    if not voter:
        raise HTTPException(status_code=404, detail="Votante no encontrado")
    
    # Buscar si existe un candidato con el mismo nombre
    candidate_with_same_name = db.query(Candidate).filter(Candidate.name == voter.name).first()
    
    return {
        "voter_id": voter_id,
        "voter_name": voter.name,
        "is_also_candidate": candidate_with_same_name is not None,
        "can_vote": candidate_with_same_name is None
    }

@app.get("/health")
def health_check():
    """Endpoint de verificación de salud de la API."""
    return {"status": "healthy", "message": "Sistema de votaciones funcionando correctamente"}

# Documentación adicional
@app.get("/")
def root():
    """Endpoint raíz con información básica de la API."""
    return {
        "message": "Sistema de Votaciones API",
        "version": "1.0.0",
        "documentation": "/docs",
        "features": [
            "Gestión de votantes",
            "Gestión de candidatos", 
            "Emisión de votos",
            "Estadísticas de votación",
            "Validaciones de integridad"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)