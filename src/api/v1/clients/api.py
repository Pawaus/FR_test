from ninja import Router
from domain.global_schemas import Error
from domain.clients import ClientCreate, ClientUpdate, ClientDelete, ClientDefaultResponse

from apps.newsletter.models import Client
from utils.logger import logger_main
from django.http import HttpResponse

api_clients = Router()


@api_clients.post("/create", response={200: ClientDefaultResponse, 422: Error}, summary="Create client")
def create_client(request, client: ClientCreate):
    """To create client, send:
        - phone_number
        - code_operator
        - tag
        - time_zone
    """
    logger_main.info(f"POST request /api/clients/create, phone_number={client.phone}")
    try:
        client_db = Client(number_phone=client.phone, code_operator=client.code_operator, tag=client.tag,
                           time_zone=client.time_zone)
        client_db.save()
        logger_main.info(f"Success create client in DB, id={str(client_db.id)}")
        return {"status": "ok"}
    except Exception as e:
        logger_main.error(f"Failed to create client in DB, exception:{str(e)}")
        return 422, {"message": "User already exist"}


@api_clients.put("/update", response={200: ClientDefaultResponse, 422: Error}, summary="Update client info")
def update_client_info(request, client: ClientUpdate):
    """
    To update client info, send in request:
     - phone number
     - code_operator (not required)
     - tag (not required)
     - time_zone (not required)
    """
    logger_main.info(f"PUT request /api/clients/update, phone_number={client.phone}")
    try:
        client_db = Client.objects.get(number_phone=client.phone)
        client_db.code_operator = client.code_operator if client.code_operator is not None else client_db.code_operator
        client_db.tag = client.tag if client.tag is not None else client_db.tag
        client_db.time_zone = client.time_zone if client.time_zone is not None else client_db.time_zone
        client_db.save()
        logger_main.info(f"Success update client info, phone_number={client.phone}")
        return {"status": "ok"}
    except Client.DoesNotExist:
        logger_main.error(f"Failed to update client info, client with phone {client.phone} does no exist")
        return 422, {"message": "User not found"}
    except Exception as e:
        logger_main.error(f"Failed to update client info, client with phone {client.phone}, exception: {str(e)}")
        return 422, {"message": "User not found"}


@api_clients.delete("/delete", response={204: None, 422: Error}, summary="Delete client from DB")
def delete_client(request, client: ClientDelete):
    """To delete client from DB, send phone number"""
    logger_main.info(f"DELETE request /api/clients/delete, phone_number={client.phone}")
    try:
        Client.objects.filter(number_phone=client.phone).delete()
        logger_main.info(f"Success delete client, phone_number={client.phone}")
        return HttpResponse(status=204)
    except Client.DoesNotExist:
        logger_main.error(f"Failed to delete client, client with phone {client.phone} does no exist")
        return 422, {"message": "User not found"}
    except Exception as e:
        logger_main.error(f"Failed to update client info, client with phone {client.phone} ,exception: {str(e)}")
        return 422, {"message": "User not found"}
