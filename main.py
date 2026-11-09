from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pydantic import EmailStr
from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
#==========
# CONEXION A POSTGRESQL
#==========
DATABASE_URL = "postgresql+psycopg://postgres:root@localhost:5432/usuariosdb"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
#==========
# MODELO
#==========
class UsuarioDB(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    fecha_registro = Column(DateTime, server_default=func.now())
Base.metadata.create_all(bind=engine)
#==========
# VALIDACION
#==========

class Usuario(BaseModel):
    nombre: str
    email: EmailStr
#==========
# API
#==========
app = FastAPI()
#==========
# CORS
#==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
#==========
# INICIO
#==========

@app.get("/")
def inicio():
    return "Datos Usuarios"
#==========
# LISTAR USUARIOS
#==========
@app.get("/api/usuarios")
def listar(
    page: int = 1,
    limit: int = 5,
    search: str = ""
):
    db = SessionLocal()
    consulta = db.query(UsuarioDB)
    if search != "":
        consulta = consulta.filter(
            (UsuarioDB.nombre.ilike(f"%{search}%"))
            (UsuarioDB.email.ilike(f"%{search}%"))
        )
    total = consulta.count()
    usuarios = consulta.offset(
        (page-1)*limit
    ).limit(limit).all()
    db.close()
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "usuarios": usuarios
    }
#==========
# AGREGAR USUARIO
#==========
@app.post("/api/usuarios")
def agregar(usuario: Usuario):
    db = SessionLocal()
    existe = db.query(UsuarioDB).filter(
        UsuarioDB.email == usuario.email
    ).first()
    if existe:
        db.close()
        raise HTTPException(
            status_code=400,
            detail="El correo ya esta registrado"
        )
    nuevo = UsuarioDB(
        nombre = usuario.nombre,
        email = usuario.email
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    db.close()
    return {
        "mensaje": "Usuario agregado",
        "usuario": nuevo
    }
#==========
# ELIMINAR
#==========
@app.delete("/api/usuarios/{id}")
def eliminar(id: int):
    db = SessionLocal()
    usuario = db.query(UsuarioDB).filter(
        UsuarioDB.id == id
    ).first()
    if usuario == None:
        db.close()
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )
    db.delete(usuario)
    db.commit()
    db.close()
    return {
        "mensaje": "Usuario eliminado"
    }
