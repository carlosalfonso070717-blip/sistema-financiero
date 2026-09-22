"""Mutations del schema (Dia 1: gestion de empresas)."""
import strawberry
from strawberry.types import Info

from app.schemas.company import Company, CreateCompanyInput, UpdateCompanyInput
from app.services import company_service


@strawberry.type
class Mutation:
    @strawberry.mutation(description="Crea una empresa.")
    def create_company(self, info: Info, input: CreateCompanyInput) -> Company:
        model = company_service.create_company(
            info.context.db,
            name=input.name,
            legal_name=input.legal_name,
            tax_id=input.tax_id,
            email=input.email,
            phone=input.phone,
        )
        return Company.from_model(model)

    @strawberry.mutation(description="Actualiza parcialmente una empresa.")
    def update_company(self, info: Info, input: UpdateCompanyInput) -> Company:
        model = company_service.update_company(
            info.context.db,
            company_id=str(input.id),
            name=input.name,
            legal_name=input.legal_name,
            tax_id=input.tax_id,
            email=input.email,
            phone=input.phone,
            is_active=input.is_active,
        )
        return Company.from_model(model)

    @strawberry.mutation(description="Baja logica de una empresa (RN-06).")
    def deactivate_company(self, info: Info, id: strawberry.ID) -> Company:
        model = company_service.deactivate_company(info.context.db, str(id))
        return Company.from_model(model)
