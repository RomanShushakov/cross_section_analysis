# -*- coding:utf-8 -*-

import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
from jwt import PyJWTError
from pydantic import BaseModel

import app.section_analysis as sa
import app.image_drawing as im_draw
# from app.database import MongodbService
from app.database import get_data, save_data
from app.settings import LIFETIME, DEFAULT_OUTPUT_STRESSES, COMMON_STRUCTURAL_SECTIONS
from app.users_database import extract_users_from_db, add_user_into_db

from fastapi import FastAPI, Request, Form, HTTPException,  Depends, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

import pickle
# from bson.binary import Binary

from typing import Optional

BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
WEB_LAYOUT_DIR = os.path.normpath(os.path.join(BASE_FOLDER, 'web_layout'))

PREP_ACTION = '/analysis_results/analysis'

MESH_CHECK_PASSED_MSG = 'mesh is ok.'
MESH_CHECK_NOT_PASSED_MSG = 'Too many elements. Please increase mesh sizes or decrease cross-section dimensions.'

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "9595b0b0117f573c984b647c8760d1b041f36b4187101b4eb3767cfde8a43d32"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


app = FastAPI()

app.mount("/web_layout", StaticFiles(directory=WEB_LAYOUT_DIR), name="web_layout")

templates = Jinja2Templates(directory=WEB_LAYOUT_DIR)

# database = MongodbService.get_instance()


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = None


class User(BaseModel):
    full_name: str
    email: str
    username: str
    disabled: bool = False
    is_superuser: bool = False


class UserInCreation(User):
    password: str


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user(db_extraction, username: str):
    if username in db_extraction:
        user_dict = db_extraction[username]
        return UserInDB(**user_dict)


def authenticate_user(db_extraction, username: str, password: str):
    user = get_user(db_extraction, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except PyJWTError:
        raise credentials_exception
    all_users = await extract_users_from_db()
    user = get_user(all_users, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.get("/")
async def choose_analysis(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/auth/create_user")
async def create_user(user: UserInCreation, request: Request):
    return await add_user_into_db(user=user)


@app.post("/auth/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    all_users = await extract_users_from_db()
    user = authenticate_user(all_users, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/current_username")
async def read_users_me(request: Request, current_user: User = Depends(get_current_active_user)):
    return {"username": current_user.username}


@app.get("/users/sign_in")
async def read_users_me(request: Request, current_user: User = Depends(get_current_active_user)):
    return templates.TemplateResponse("index.html", {"request": request, "username": current_user.username})


@app.get("/sections")
async def choose_section(request: Request):
    sections = list()
    for section in COMMON_STRUCTURAL_SECTIONS:
        sections.append({'section_name': section['name'],
                         'section_image': section['image'],
                         'section_type': section['section_type']})

    return templates.TemplateResponse("sections.html", {"request": request, 'sections': sections})


@app.get("/{section_type}")
async def compose_prep(request: Request, section_type: str):
    current_common_section = [section for section in COMMON_STRUCTURAL_SECTIONS
                              if section['section_type'] == section_type]
    if current_common_section:
        image, elements = current_common_section[0]['image'], current_common_section[0]['elements']
    else:
        raise HTTPException(status_code=404, detail="Item not found")

    return templates.TemplateResponse("cross-section-page.html", {"request": request, 'section_type': section_type,
                                                                  'action': PREP_ACTION, 'image': image,
                                                                  'elements': elements})


@app.post("/analysis_results/{step}")
async def analyze_section(
        request: Request, step: str, d: Optional[float] = Form(None), b: Optional[float] = Form(None),
        n: Optional[int] = Form(None), t: Optional[float] = Form(None), d_y: Optional[float] = Form(None),
        d_x: Optional[float] = Form(None), r_out: Optional[float] = Form(None), n_r: Optional[int] = Form(None),
        t_f: Optional[float] = Form(None), t_w: Optional[float] = Form(None), r: Optional[float] = Form(None),
        b_t: Optional[float] = Form(None), b_b: Optional[float] = Form(None), t_ft: Optional[float] = Form(None),
        t_fb: Optional[float] = Form(None), r_r: Optional[float] = Form(None), r_f: Optional[float] = Form(None),
        alpha: Optional[float] = Form(None), r_t: Optional[float] = Form(None), l: Optional[float] = Form(None),
        b_l: Optional[float] = Form(None), b_r: Optional[float] = Form(None), r_in: Optional[float] = Form(None),
        rot: Optional[float] = Form(None), n_sides: Optional[int] = Form(None), section_type: str = Form(...),
        mesh_sizes: float = Form(...), N: Optional[float] = Form(0), Vx: Optional[float] = Form(0),
        Vy: Optional[float] = Form(0), Mxx: Optional[float] = Form(0), Myy: Optional[float] = Form(0),
        Mzz: Optional[float] = Form(0)):
    all_analysis_parameters = dict(
        d=d, b=b, n=n, t=t, d_y=d_y, d_x=d_x, r_out=r_out, n_r=n_r, t_f=t_f, t_w=t_w, r=r, b_t=b_t,
        b_b=b_b, t_ft=t_ft, t_fb=t_fb, r_r=r_r, r_f=r_f, alpha=alpha, r_t=r_t, l=l, b_l=b_l, b_r=b_r,
        r_in=r_in, rot=rot, n_sides=n_sides, section_type=section_type, mesh_sizes=mesh_sizes
    )

    current_common_section = [section for section in COMMON_STRUCTURAL_SECTIONS
                              if section['section_type'] == section_type]
    if current_common_section:
        analyzed_section_base_name = current_common_section[0]['analyzed_section_base_name'].format(
            **all_analysis_parameters)
        analyzing_function = getattr(sa, current_common_section[0]['analyzing_function'])
    else:
        raise HTTPException(status_code=404, detail="Item not found")
    
    section_analysis_results = await get_data(analyzed_section_base_name=analyzed_section_base_name)
    if section_analysis_results:
        if step == 'checking':
            return {'msg': MESH_CHECK_PASSED_MSG}

        area = section_analysis_results['area']
        ixx_c = section_analysis_results['ixx_c']
        iyy_c = section_analysis_results['iyy_c']
        ixy_c = section_analysis_results['ixy_c']
        torsion_constant = section_analysis_results['torsion_constant']
        warping_constant = section_analysis_results['warping_constant']
        # elastic_centroid = section_analysis_results['elastic_centroid']
        # centroidal_shear_center = section_analysis_results['centroidal_shear_center']
        elastic_centroid = pickle.loads(section_analysis_results['elastic_centroid'])
        centroidal_shear_center = pickle.loads(section_analysis_results['centroidal_shear_center'])

    else:
        mesh_check_passed, nodes, unit_stresses, area, ixx_c, iyy_c, ixy_c, torsion_constant, warping_constant, \
        elastic_centroid, centroidal_shear_center = analyzing_function(step=step, N=1, Vx=1, Vy=1, Mxx=1, Myy=1, Mzz=1,
                                                                       **all_analysis_parameters)
        if mesh_check_passed and step == 'analysis':
            await save_data(
                section={'analyzed_section_base_name': analyzed_section_base_name,
                        #  'nodes': Binary(pickle.dumps(nodes, protocol=2)),
                        #  'unit_stresses': Binary(pickle.dumps(unit_stresses, protocol=2)),
                         'nodes': pickle.dumps(nodes),
                         'unit_stresses': pickle.dumps(unit_stresses),
                         'area': area, 'ixx_c': ixx_c, 'iyy_c': iyy_c, 'ixy_c': ixy_c,
                         'torsion_constant': torsion_constant, 'warping_constant': warping_constant,
                        #  'elastic_centroid': elastic_centroid, 'centroidal_shear_center': centroidal_shear_center,
                         'elastic_centroid': pickle.dumps(elastic_centroid),
                         'centroidal_shear_center': pickle.dumps(centroidal_shear_center),
                         'expired_at': datetime.utcnow() + timedelta(seconds=LIFETIME)})
        elif mesh_check_passed and step == 'checking':
            return {'msg': MESH_CHECK_PASSED_MSG}

        else:
            if step == 'checking':
                return {'msg': MESH_CHECK_NOT_PASSED_MSG}
            else:
                return templates.TemplateResponse("mesh_check_not_passed.html", {"request": request,
                                                                                 'msg': MESH_CHECK_NOT_PASSED_MSG})

    return templates.TemplateResponse(
        "results.html", {"request": request, 'area': f'{area:.2f}', 'ixx_c': f'{ixx_c:.2f}',
                       'iyy_c': f'{iyy_c:.2f}', 'ixy_c': f'{ixy_c:.2f}',
                       'elastic_centroid': f'({elastic_centroid[0]:.2f}, {elastic_centroid[1]:.2f})',
                       'torsion_constant': f'{torsion_constant:.2f}', 'warping_constant': f'{warping_constant:.2f}',
                       'centroidal_shear_center': f'({centroidal_shear_center[0]:.2f},'
                                                  f' {centroidal_shear_center[1]:.2f})',
                       'output_stresses': DEFAULT_OUTPUT_STRESSES,
                       'analyzed_section_base_name': analyzed_section_base_name,
                       'N': N, 'Vx': Vx, 'Vy': Vy, 'Mxx': Mxx, 'Myy': Myy, 'Mzz': Mzz})


@app.get("/draw_image/{analyzed_section_base_name}/{stress_name}/{stress_description}/{N}/{Vx}/{Vy}/{Mxx}/{Myy}/{Mzz}")
async def draw_image(analyzed_section_base_name: str, stress_name: str, stress_description: str,
                     N: float, Vx: float, Vy: float, Mxx: float, Myy: float, Mzz: float):
    section_data = await get_data(analyzed_section_base_name=analyzed_section_base_name)
    nodes = pickle.loads(section_data['nodes'])
    unit_stresses = pickle.loads(section_data['unit_stresses'])

    x_coords = [node[0] for node in nodes]
    y_coords = [node[1] for node in nodes]

    if stress_name == 'sig_zz':
        sig_zz_n = unit_stresses['sig_zz_n'] * N
        sig_zz_mxx = unit_stresses['sig_zz_mxx'] * Mxx
        sig_zz_myy = unit_stresses['sig_zz_myy'] * Myy
        current_stress = sig_zz_n + sig_zz_mxx + sig_zz_myy

    elif stress_name == 'sig_zxy':
        sig_zx_mzz = unit_stresses['sig_zx_mzz'] * Mzz
        sig_zy_mzz = unit_stresses['sig_zy_mzz'] * Mzz
        sig_zx_vx = unit_stresses['sig_zx_vx'] * Vx
        sig_zy_vx = unit_stresses['sig_zy_vx'] * Vx
        sig_zx_vy = unit_stresses['sig_zx_vy'] * Vy
        sig_zy_vy = unit_stresses['sig_zy_vy'] * Vy
        current_stress = ((sig_zx_mzz + sig_zx_vx + sig_zx_vy) ** 2 + (sig_zy_mzz + sig_zy_vx + sig_zy_vy) ** 2) ** 0.5

    elif stress_name == 'sig_vm':
        sig_zz_n = unit_stresses['sig_zz_n'] * N
        sig_zz_mxx = unit_stresses['sig_zz_mxx'] * Mxx
        sig_zz_myy = unit_stresses['sig_zz_myy'] * Myy
        current_normal_stress = sig_zz_n + sig_zz_mxx + sig_zz_myy

        sig_zx_mzz = unit_stresses['sig_zx_mzz'] * Mzz
        sig_zy_mzz = unit_stresses['sig_zy_mzz'] * Mzz
        sig_zx_vx = unit_stresses['sig_zx_vx'] * Vx
        sig_zy_vx = unit_stresses['sig_zy_vx'] * Vx
        sig_zx_vy = unit_stresses['sig_zx_vy'] * Vy
        sig_zy_vy = unit_stresses['sig_zy_vy'] * Vy
        current_shear_stress = ((sig_zx_mzz + sig_zx_vx + sig_zx_vy) ** 2
                                + (sig_zy_mzz + sig_zy_vx + sig_zy_vy) ** 2) ** 0.5

        current_stress = (current_normal_stress ** 2 + 3 * (current_shear_stress ** 2)) ** 0.5

    else:
        current_stress = unit_stresses[stress_name]

    image = im_draw.draw(x_coords=x_coords, y_coords=y_coords, current_stress=current_stress,
                         stress_description=stress_description)

    return StreamingResponse(image, media_type="image/png")
