from flask import Blueprint, render_template
from crm.models import Company
from crm.utils.route_helpers import BaseRouteHandler

companies_bp = Blueprint("companies", __name__)
company_handler = BaseRouteHandler(Company, "companies")


@companies_bp.route("/")
def index():
    companies = Company.query.all()
    return render_template("companies/index.html", companies=companies)


@companies_bp.route("/<int:company_id>")
def detail(company_id):
    company = Company.query.get_or_404(company_id)
    return render_template("companies/detail.html", company=company)


@companies_bp.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        return company_handler.handle_create(
            name="name",
            industry="industry",
            website="website"
        )

    return render_template("companies/new.html")
