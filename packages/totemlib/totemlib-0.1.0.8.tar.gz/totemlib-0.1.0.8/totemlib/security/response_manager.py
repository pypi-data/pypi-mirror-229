# # Manejador de estandar para response
# # Creado por: Totem Bear
# # Fecha: 23-Ago-2023

# from fastapi import Response
# import requests
# from typing import Optional, Tuple
# from totemlib import utils as tbu
# from . import gendata as gd

# # Diccionario de métodos disponibles para invocar APIs
# METHODS = {
#     'get': requests.get,
#     'post': requests.post,
#     'put': requests.put,
#     'delete': requests.delete
# }

# # TODO - Mover esta funcion a totemlib
# def get_response(url, method, req_form: None):

#     endpoint = gd.url_api + url
#     print("\n*****endpoint: " + endpoint)
#     print("*****method: " + method)
#     print("*****req_form: ", req_form)

#     if method in METHODS:
#         if req_form is not None:
#             response = METHODS[method](url=endpoint, json=req_form)
#         else:
#             response = METHODS[method](url=endpoint)
#     else:
#         # SE DEBE RETORNAR UN ERROR RESPONSE ******************************
#         response = Response(status_code=400, content=f"Invalid method: Error \
#                             in getResponse - Is needed the method, body or \
#                             params for endpoint {{url}}")

#     print("\n*****response status-reason get_response:", response.status_code, 
#           " - ", response.reason)
#     print("\n*****response:", response, "\n")

#     return response


# # TODO - Mover esta funcion a totemlib
# def get_resp_token(url, auth_token, method, req_form: None):

#     endpoint = gd.url_api + url
#     #print("\n*****endpoint: " + endpoint)
#     #print("*****method: " + method)
#     #print("*****tokenForm: ", authToken)
#     headers = {
#         'Authorization': f'Bearer {auth_token}',
#         'Content-Type': 'application/json'
#     }
#     #print("\n*****req_form: ", req_form)

#     if method in METHODS:
#         if req_form is not None:
#             response = METHODS[method](url=endpoint, params=req_form, 
#                                        headers=headers)
#         else:
#             response = METHODS[method](url=endpoint, headers=headers)
#     else:
#         # SE DEBE RETORNAR UN ERROR RESPONSE ******************************
#         response = Response(status_code=400, content=f"Invalid method: Error \
#                             in getResponse - Is needed the method, body or \
#                             params for endpoint {{url}}")

#     print("\n*****response status-reason getResponse:", response.status_code, 
#           " - ", response.reason)
#     print("\n*****response:", response, "\n")

#     return response


# def error_response(resp: dict, msj_error: str, 
#                    detalles: Optional[Tuple] = None) -> dict:
#     """Genera una respuesta de error en formato de diccionario.

#     Args:
#         resp: Respuesta a devolver
#         msj_error (str): El mensaje de error principal a incluir en la 
#             respuesta.
#         detalles (Optional[Tuple], optional): Detalles adicionales para 
#             incluir. Por defecto en None.
#     Returns:
#         dict: Diccionario que contiene la respuesta de error.
#     """
    
#     response = {"resp": resp, "msj": msj_error, "error": True}
    
#     if detalles is not None:
#         response["detalles"] = detalles
    
#     return response


# def success_response(resp: dict, msj: str, 
#                      detalles: Optional[dict] = None) -> dict:
#     """Genera una respuesta de éxito en formato de diccionario.

#     Args:
#         resp: Respuesta a devolver
#         msj (str): El mensaje principal a incluir en la respuesta.
#         detalles (Optional[Tuple], optional): Detalles adicionales para 
#             incluir. Por defecto en None.
#     Returns:
#         dict: Diccionario que contiene la respuesta.
#     """
    
#     response = {"resp": resp, "msj": msj, "error": False}
    
#     if detalles is not None:
#         response["detalles"] = detalles
#     print(f"\n***** success_response: {response}")
    
#     return response


# def service_success(metodo: str, endpoint: str):
#     msj = f"Services-Inverfin - {metodo}: Servicio {endpoint} responde."
#     tbu.logger.printLog(gd.log_file, msj, "info")


# def service_error(metodo: str, endpoint: str):
#     msj = f"Services-Inverfin - {metodo}: Servicio {endpoint} NO responde."
#     tbu.logger.printLog(gd.log_file, msj, "error")
