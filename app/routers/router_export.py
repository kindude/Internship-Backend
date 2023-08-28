import json

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from db.get_db import get_redis, get_db
from repositories.action_repository import ActionRepository
from repositories.company_repository import CompanyRepository
from repositories.export_repository import ExportRepository
from repositories.redis_repository import RedisRepository
from schemas.User import UserResponse
from utils.auth import get_current_user

router_export = APIRouter()

@router_export.get("/export/user-results/{company_id}/{user_id}", tags=["ExportData"])
async def export_user_results(
        company_id:int,
        user_id: int,
        format: str,
        current_user: UserResponse = Depends(get_current_user),
):

    if user_id == current_user.id:
        if format not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail="Invalid format")
        redis_repository = RedisRepository()
        export_repository = ExportRepository()
        user_results = await redis_repository.get_user_results_from_database(company_id=company_id, user_id=user_id)
        if not user_results:
            raise HTTPException(status_code=404, detail="User results not found")

        if format == "json":
            with open("user_result.json", "w") as json_file:
                json.dump(user_results, json_file)
            return JSONResponse(content=user_results)

        elif format == "csv":
            return export_repository.generate_csv_response(user_results, "user_results.csv")
    raise HTTPException(status_code=403, detail="You are not allowed to export quizzes of this user")


@router_export.get("/export/company-results/{company_id}", tags=["ExportData"])
async def export_company_results(
        company_id: int,
        format: str = "json",
        current_user: UserResponse = Depends(get_current_user),
        db:AsyncSession = Depends(get_db)
):
    if format not in ["json", "csv"]:
        raise HTTPException(status_code=400, detail="Invalid format")

    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(id=company_id)
    action_repository = ActionRepository(database=db)
    admins = await action_repository.get_all_admins(company_id=company_id, per_page=5, page=1)
    if admins:
        admin_ids = [admin.id for admin in admins.users]
        if company.owner_id == current_user.id or current_user.id in admin_ids:
            redis_repository = RedisRepository()
            export_repository = ExportRepository()
            company_results = await redis_repository.get_company_results(company_id=company_id)

            if not company_results:
                raise HTTPException(status_code=404, detail="No results found")

            if format == "json":
                with open("company_result.json", "w") as json_file:
                    json.dump(company_results, json_file)
                return JSONResponse(content=company_results)
            elif format == "csv":
                return export_repository.generate_csv_response(company_results, "company_results.csv")
    raise HTTPException(status_code=403, detail="You are not allowed to check all company quizzes")