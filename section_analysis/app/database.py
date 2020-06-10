# -*- coding: utf-8 -*-

# import os
# from pymongo import ASCENDING
# import motor.motor_asyncio

# MONGO_DB_ADDR = os.getenv("MONGO_DB_ADDR", "localhost")


# class MongodbService(object):
#     _instance = None
#     _client = None
#     _db = None

#     @classmethod
#     def get_instance(cls, *args, **kwargs):
#         if cls._instance is None:
#             cls._instance = super().__new__(cls, *args, **kwargs)
#             cls.__init__(cls._instance, *args, **kwargs)
#         return cls._instance

#     def __init__(self):
#         self._client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DB_ADDR, 27017)
#         self._db = self._client.section_analysis
#         self._db.sections.create_index(
#             [("expired_at", ASCENDING)], expireAfterSeconds=0
#         )

#     async def get_data(self, analyzed_section_base_name):
#         return await self._db.sections.find_one(
#             {"analyzed_section_base_name": analyzed_section_base_name}
#         )

#     async def save_data(self, section):
#         await self._db.sections.insert_one(section)

import os
import asyncio
import asyncpg
import pickle

POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "pass_test")
POSTGRES_USER = os.getenv("POSTGRES_USER", "user_test")
POSTGRES_DB_ADDR = os.getenv("POSTGRES_DB_ADDR", "localhost")
POSTGRES_DB = os.getenv("POSTGRES_DB", "db_test")


async def _create_table():
    conn = await asyncpg.connect(
        f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_DB_ADDR}/{POSTGRES_DB}"
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sections(
            id serial PRIMARY KEY,
            analyzed_section_base_name text,
            nodes bytea,
            unit_stresses bytea,
            area float,
            ixx_c float,
            iyy_c float,
            ixy_c float,
            torsion_constant float,
            warping_constant float,
            elastic_centroid bytea,
            centroidal_shear_center bytea
         )
        """
    )
    conn.close()

async def get_data(analyzed_section_base_name):
    await _create_table()
    conn = await asyncpg.connect(
        f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_DB_ADDR}/{POSTGRES_DB}"
    )
    row = await conn.fetchrow(
        "SELECT * FROM sections WHERE analyzed_section_base_name = $1",
        analyzed_section_base_name,
    )
    await conn.close()
    return row

async def save_data(section):
    await _create_table()
    conn = await asyncpg.connect(
        f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_DB_ADDR}/{POSTGRES_DB}"
    )
    await conn.execute(
        """
        INSERT INTO sections(
            analyzed_section_base_name, nodes, unit_stresses,
            area, ixx_c, iyy_c, ixy_c, torsion_constant,
            warping_constant, elastic_centroid, centroidal_shear_center) VALUES(
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)""",
        section["analyzed_section_base_name"],
        section["nodes"],
        section["unit_stresses"],
        section["area"],
        section["ixx_c"],
        section["iyy_c"],
        section["ixy_c"],
        section["torsion_constant"],
        section["warping_constant"],
        section["elastic_centroid"],
        section["centroidal_shear_center"],
    )
    await conn.close()
