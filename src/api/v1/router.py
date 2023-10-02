from ninja import NinjaAPI
from api.v1.clients.api import api_clients
from api.v1.newsletter.api import api_newsletter

api = NinjaAPI(title="Newsletters API")

api.add_router("/clients", api_clients, tags=["Clients"])
api.add_router("/newsletter", api_newsletter, tags=["Newsletter"])
